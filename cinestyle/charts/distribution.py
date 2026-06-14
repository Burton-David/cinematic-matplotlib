"""Distribution idioms: beeswarm, ridgeline, hexbin density.

Three ways to show shape rather than a single summary. Each takes tidy data and
an axes, applies the active theme, and returns the axes (or the primary artist
where one object is the natural handle).
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from matplotlib.axes import Axes
from matplotlib.collections import PolyCollection
from matplotlib.colors import Colormap
from numpy.typing import ArrayLike, NDArray

from . import _base


def beeswarm(
    values: ArrayLike,
    groups: Sequence[object] | None = None,
    ax: Axes | None = None,
    *,
    orient: str = "h",
    size: float = 5.0,
    span: float = 0.4,
    color: str | None = None,
) -> Axes:
    """Plot a one-dimensional scatter that spreads points instead of overplotting.

    A beeswarm shows every observation while keeping density legible: where a
    strip plot would stack points into an opaque line, the swarm nudges them off
    the category line just far enough not to overlap. With *groups*, one swarm is
    drawn per category and colored from the theme cycle.

    Args:
        values: The observations.
        groups: Optional category per observation; unique values become slots.
        ax: Target axes (defaults to the current axes).
        orient: ``"h"`` puts categories on the x-axis (values vertical), ``"v"``
            flips it.
        size: Marker size in points.
        span: Half-width of a swarm, in category-slot units (0.5 fills the slot).
        color: Single-color override; ignored when *groups* is given.

    Returns:
        The axes.
    """
    ax = _base.current_ax(ax)
    values = np.asarray(values, dtype=float)
    if groups is None:
        keys: list[object] = [0]
        members = [np.ones(values.size, dtype=bool)]
    else:
        keys = list(dict.fromkeys(groups))
        group_arr = np.asarray(groups, dtype=object)
        members = [group_arr == k for k in keys]

    for slot, (_key, mask) in enumerate(zip(keys, members, strict=True)):
        vals = values[mask]
        if vals.size == 0:
            continue
        offsets = _swarm(vals, span=span)
        point_color = color or (_base.primary() if groups is None else _base.nth(slot))
        pos = slot + offsets
        if orient == "h":
            ax.scatter(pos, vals, s=size**2, color=point_color, zorder=3)
        else:
            ax.scatter(vals, pos, s=size**2, color=point_color, zorder=3)

    ticks = list(range(len(keys)))
    labels = [str(k) for k in keys]
    if orient == "h":
        ax.set_xticks(ticks, labels)
        ax.margins(x=0.1)
    else:
        ax.set_yticks(ticks, labels)
        ax.margins(y=0.1)
    return ax


def _swarm(vals: NDArray[np.float64], *, span: float) -> NDArray[np.float64]:
    vmin, vmax = float(vals.min()), float(vals.max())
    if vmax == vmin:
        return np.zeros(vals.size)
    norm = (vals - vmin) / (vmax - vmin)
    # Finer bins as the count grows, so a dense column packs tighter rather than
    # ballooning sideways past the slot.
    bins = float(np.clip(vals.size * 0.6, 12, 60))
    raw = _base.swarm_offsets(norm, gap=1.0 / bins, span=1.0)
    peak = float(np.abs(raw).max())
    return raw / peak * span if peak > 0 else raw


def ridgeline(
    distributions: Sequence[ArrayLike],
    labels: Sequence[str] | None = None,
    ax: Axes | None = None,
    *,
    overlap: float = 0.7,
    fill_alpha: float = 0.8,
    points: int = 256,
) -> Axes:
    """Stack smoothed densities into overlapping ridges (a joyplot).

    Each distribution becomes a filled Gaussian density on its own baseline;
    baselines are spaced so neighbors overlap by *overlap*, the layered look
    that lets many distributions share one panel and still be compared. Ridges
    are drawn back to front so a taller ridge reads as in front of the next.

    Args:
        distributions: One sample array per row.
        labels: Optional row labels, shown on the y-axis.
        ax: Target axes (defaults to the current axes).
        overlap: Fraction a ridge may climb into the row above it, in [0, 1).
        fill_alpha: Opacity of each ridge fill.
        points: Grid resolution for each density.

    Returns:
        The axes.
    """
    ax = _base.current_ax(ax)
    arrays = [np.asarray(d, dtype=float) for d in distributions]
    lo = min(a.min() for a in arrays)
    hi = max(a.max() for a in arrays)
    pad = 0.05 * (hi - lo or 1.0)
    grid = np.linspace(lo - pad, hi + pad, points)

    densities = [_base.gaussian_kde(a, grid) for a in arrays]
    peak = max((d.max() for d in densities), default=1.0) or 1.0
    step = 1.0 - overlap  # vertical distance between successive baselines

    n = len(arrays)
    for i in reversed(range(n)):  # back (top) to front (bottom)
        base = i * step
        height = densities[i] / peak
        color = _base.nth(i)
        ax.fill_between(
            grid, base, base + height, color=color, alpha=fill_alpha, zorder=i
        )
        ax.plot(grid, base + height, color=_base.foreground(), linewidth=0.8, zorder=i)

    baselines = [i * step for i in range(n)]
    ax.set_yticks(baselines, list(labels) if labels else [str(i) for i in range(n)])
    ax.margins(y=0.02)
    return ax


def hexbin_density(
    x: ArrayLike,
    y: ArrayLike,
    ax: Axes | None = None,
    *,
    gridsize: int = 30,
    mincnt: int = 1,
    cmap: str | None = None,
) -> PolyCollection:
    """Bin a dense scatter into hexagons shaded by the theme's sequential map.

    The honest tool once a scatter turns into a cloud: hexagonal bins read
    density without the moire that square bins produce. Empty cells are left
    unfilled (``mincnt=1``) so the plot background shows through.

    Args:
        x, y: Point coordinates.
        ax: Target axes (defaults to the current axes).
        gridsize: Number of hexagons across the x-axis.
        mincnt: Minimum count for a cell to be drawn.
        cmap: Colormap name override; defaults to the active theme's sequential.

    Returns:
        The hexbin :class:`~matplotlib.collections.PolyCollection`, so the caller
        can attach a colorbar.
    """
    ax = _base.current_ax(ax)
    colormap: str | Colormap = cmap if cmap is not None else _base.sequential_cmap()
    return ax.hexbin(
        np.asarray(x, dtype=float),
        np.asarray(y, dtype=float),
        gridsize=gridsize,
        mincnt=mincnt,
        cmap=colormap,
        linewidths=0.2,
        edgecolors=_base.muted(),
    )
