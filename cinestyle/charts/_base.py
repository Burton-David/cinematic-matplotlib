"""Shared plumbing for the chart-idiom builders.

The builders are deliberately thin: a theme already owns color and type through
rcParams, so a builder reads what it needs from the *active* theme rather than
taking a palette argument. These helpers are that bridge, plus a couple of small
numeric routines (a dependency-free Gaussian KDE, a non-overlapping swarm layout)
that more than one idiom needs.
"""

from __future__ import annotations

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.colors import Colormap
from numpy.typing import NDArray


def current_ax(ax: Axes | None) -> Axes:
    return ax if ax is not None else plt.gca()


def active_palette() -> list[str]:
    """The active theme's categorical colors, from the rc ``prop_cycle``."""
    cycle = mpl.rcParams["axes.prop_cycle"].by_key()
    return list(cycle.get("color", ["#4C78A8"]))


def primary() -> str:
    """The focal color: the first entry of the active categorical cycle."""
    return active_palette()[0]


def foreground() -> str:
    return str(mpl.rcParams["text.color"])


def muted() -> str:
    """The de-emphasized chrome color (the theme's grid color)."""
    return str(mpl.rcParams["grid.color"])


def sequential_cmap() -> Colormap:
    """The active theme's default (sequential) colormap."""
    return plt.get_cmap(mpl.rcParams["image.cmap"])


def diverging_cmap() -> Colormap:
    """The active theme's diverging colormap, by naming convention.

    Themes register their diverging map as the sequential name plus ``_div``;
    if that is not present (a plain rc with a stock cmap) fall back to a neutral
    built-in diverging map rather than guessing.
    """
    seq_name = mpl.rcParams["image.cmap"]
    div_name = f"{seq_name}_div"
    if div_name in mpl.colormaps:
        return plt.get_cmap(div_name)
    return plt.get_cmap("RdBu_r")


def nth(index: int) -> str:
    """Palette color *index*, wrapping if the cycle is shorter."""
    palette = active_palette()
    return palette[index % len(palette)]


def gaussian_kde(
    samples: NDArray[np.float64], grid: NDArray[np.float64]
) -> NDArray[np.float64]:
    """Evaluate a Gaussian kernel density of *samples* on *grid*.

    Bandwidth follows Silverman's rule. Implemented here so a ridgeline does not
    drag in SciPy for one density estimate; for the smooth 1-D densities a
    ridgeline shows, Silverman is the sensible default anyway.
    """
    samples = np.asarray(samples, dtype=float)
    n = samples.size
    if n < 2:
        return np.zeros_like(grid)
    std = samples.std(ddof=1)
    if std == 0:
        return np.zeros_like(grid)
    iqr = np.subtract(*np.percentile(samples, [75, 25]))
    spread = min(std, iqr / 1.349) if iqr > 0 else std
    bandwidth = 0.9 * spread * n ** (-1 / 5)
    if bandwidth == 0:
        return np.zeros_like(grid)
    z = (grid[:, None] - samples[None, :]) / bandwidth
    kernel = np.exp(-0.5 * z**2) / np.sqrt(2 * np.pi)
    density = kernel.sum(axis=1) / (n * bandwidth)
    return np.asarray(density, dtype=np.float64)


def swarm_offsets(
    values: NDArray[np.float64], *, gap: float, span: float
) -> NDArray[np.float64]:
    """Lay *values* out as a beeswarm, returning the off-axis offset per point.

    Everything here is in one normalized unit so the geometry is well defined:
    the caller scales ``values`` to that unit, ``gap`` is the marker diameter in
    it, and the returned offsets are too. Points are placed in ascending order;
    each takes the offset nearest the center line that clears every already
    placed point within one ``gap`` along both axes. That gives the dense,
    non-overlapping spread a swarm wants, without the jitter that lets points
    collide.

    Args:
        values: Point positions along the value axis, in the normalized unit.
        gap: Marker diameter in the same unit (the collision distance).
        span: Largest offset allowed before a point rides the edge.

    Returns:
        One offset per point, in input order, centered on zero.
    """
    order = np.argsort(values, kind="stable")
    placed_val: list[float] = []
    placed_off: list[float] = []
    for v in values[order]:
        near = [
            placed_off[i]
            for i in range(len(placed_val))
            if abs(placed_val[i] - v) < gap
        ]
        chosen = 0.0
        if near:
            candidate = 0.0
            while candidate <= span:
                for sign in (candidate, -candidate):
                    if all(abs(sign - o) >= gap for o in near):
                        chosen = sign
                        break
                else:
                    candidate += gap * 0.5
                    continue
                break
            else:
                chosen = span  # swarm is saturated; ride the edge
        placed_val.append(v)
        placed_off.append(chosen)
    offsets = np.zeros(values.size)
    offsets[order] = placed_off
    return offsets
