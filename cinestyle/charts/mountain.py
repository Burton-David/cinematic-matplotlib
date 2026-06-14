"""The signature idiom: a topographic mountain silhouette.

``mountain`` reads an elevation-like profile as terrain. It draws the profile as
a filled front ridge, stacks receding ranges behind it for depth, can shade an
annotated zone band across the scene, and marks the peaks with a value-encoded
glyph. It is the library's editorial set piece: a chart that looks like a
landscape and still carries data honestly on its y-axis.
"""

from __future__ import annotations

from collections.abc import Sequence

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from numpy.typing import ArrayLike, NDArray

from . import _base


def _smooth(values: NDArray[np.float64], window: int) -> NDArray[np.float64]:
    """Moving average with edge padding, so the ends do not droop to zero."""
    if window <= 1:
        return values
    kernel = np.ones(window) / window
    padded = np.pad(values, window // 2, mode="edge")
    return np.convolve(padded, kernel, mode="same")[
        window // 2 : window // 2 + values.size
    ]


def _detect_peaks(heights: NDArray[np.float64], limit: int) -> list[int]:
    """Indices of prominent, well-separated local maxima, at most *limit*.

    Two filters keep the marks honest: a height cut (above the mean by half a
    standard deviation, so a summit rather than noise) and a minimum spacing, so
    a jagged crest reports one peak instead of a cluster of near-equal bumps.
    """
    interior = np.arange(1, heights.size - 1)
    is_max = (heights[interior] > heights[interior - 1]) & (
        heights[interior] >= heights[interior + 1]
    )
    candidates = interior[is_max]
    cut = heights.mean() + 0.5 * heights.std()
    candidates = candidates[heights[candidates] >= cut]
    min_gap = max(1, heights.size // 12)
    chosen: list[int] = []
    for idx in sorted(candidates, key=lambda i: heights[i], reverse=True):
        if all(abs(idx - kept) >= min_gap for kept in chosen):
            chosen.append(int(idx))
        if len(chosen) >= limit:
            break
    return sorted(chosen)


def mountain(
    heights: ArrayLike,
    x: ArrayLike | None = None,
    ax: Axes | None = None,
    *,
    layers: int = 3,
    zone: tuple[float, float] | None = None,
    zone_label: str | None = None,
    peaks: Sequence[int] | None = None,
    peak_labels: Sequence[str] | None = None,
    peak_values: ArrayLike | None = None,
    label_fmt: str = "{:.0f}",
    cmap: str | None = None,
) -> Axes:
    """Render a profile as a layered mountain silhouette with marked peaks.

    Args:
        heights: The front ridge profile (an elevation series).
        x: Optional x positions; defaults to ``0..n-1``.
        ax: Target axes (defaults to the current axes).
        layers: Total ranges drawn, including the front one. Each range behind
            sits higher and paler, the atmospheric-perspective cue that makes
            depth read.
        zone: Optional ``(low, high)`` band shaded across the scene, e.g. a
            danger altitude. Drawn under the front ridge so terrain occludes it.
        zone_label: Text annotation for the zone, placed at its right edge.
        peaks: Indices to mark; when omitted, prominent local maxima are found.
        peak_labels: Optional label per marked peak.
        peak_values: Optional value per peak to color-encode; defaults to the
            peak height. Mapped through the theme's sequential colormap.
        label_fmt: Format for the value shown above each peak.
        cmap: Sequential colormap name override; defaults to the theme's.

    Returns:
        The axes.
    """
    ax = _base.current_ax(ax)
    profile = np.asarray(heights, dtype=float)
    xs = np.arange(profile.size) if x is None else np.asarray(x, dtype=float)
    colormap = _base.sequential_cmap() if cmap is None else plt.get_cmap(cmap)
    # Anchor everything to the data's own floor and span, so a profile that lives
    # at 4000 m reads the same as one that lives at 4: the lift below is a slice
    # of the span, not of an absolute height that would tower over offset data.
    floor = float(profile.min())
    span = float(profile.max()) - floor or 1.0

    if zone is not None:
        low, high = zone
        ax.axhspan(low, high, color=_base.muted(), alpha=0.5, zorder=0)
        if zone_label:
            # Pin the label to the upper-left inside the band, where it cannot run
            # off the right edge regardless of the band's height.
            ax.annotate(
                zone_label,
                (xs[0], min(high, profile.max())),
                xytext=(8, -6),
                textcoords="offset points",
                ha="left",
                va="top",
                color=_base.foreground(),
                alpha=0.85,
            )

    # Receding ranges, deepest first: each is the front profile rolled along and
    # smoothed (so it reads as a different ridgeline), pulled toward the floor and
    # lifted by a slice of the span. Painter's order plus a paler fill does the
    # rest; the dark front fill below then covers their bases.
    shift = max(1, profile.size // 14)
    for depth in range(layers - 1, 0, -1):
        lift = span * 0.1 * depth
        rolled = _smooth(np.roll(profile, shift * depth), shift)
        ridge = floor + (rolled - floor) * (1.0 - 0.12 * depth) + lift
        tone = colormap(max(0.12, 0.82 - 0.22 * depth))
        ax.fill_between(xs, floor + lift, ridge, color=tone, zorder=depth)

    ax.fill_between(xs, floor, profile, color=colormap(0.9), zorder=layers)
    ax.plot(xs, profile, color=_base.foreground(), linewidth=1.0, zorder=layers + 1)

    indices = list(peaks) if peaks is not None else _detect_peaks(profile, limit=6)
    if indices:
        marks = (
            profile[indices]
            if peak_values is None
            else np.asarray(peak_values, dtype=float)
        )
        vmin, vmax = float(marks.min()), float(marks.max())
        spread = vmax - vmin or 1.0
        for slot, idx in enumerate(indices):
            value = float(marks[slot])
            ax.scatter(
                xs[idx],
                profile[idx],
                marker="^",
                s=140,
                color=colormap(0.2 + 0.7 * (value - vmin) / spread),
                edgecolor=_base.foreground(),
                linewidth=1.0,
                zorder=layers + 2,
            )
            text = label_fmt.format(value)
            # Auto-detected peaks need not match the labels given, so label only
            # the ones a caller named and leave the rest as bare values.
            if peak_labels is not None and slot < len(peak_labels):
                text = f"{peak_labels[slot]}\n{text}"
            ax.annotate(
                text,
                (xs[idx], profile[idx]),
                xytext=(0, 10),
                textcoords="offset points",
                ha="center",
                va="bottom",
                color=_base.foreground(),
                zorder=layers + 2,
            )
    ax.margins(x=0.0)
    return ax
