"""Time-series idioms: underwater drawdown, streamgraph, rolling-correlation heatmap.

Charts built for a value that moves through time: how far a series sits below its
own peak, how a composition breathes, and how relationships drift.
"""

from __future__ import annotations

from collections.abc import Sequence
from itertools import combinations
from typing import Any, cast

import numpy as np
from matplotlib.axes import Axes
from matplotlib.colors import Colormap
from matplotlib.image import AxesImage
from matplotlib.ticker import FuncFormatter
from numpy.typing import ArrayLike

from . import _base


def underwater(
    series: ArrayLike,
    x: ArrayLike | None = None,
    ax: Axes | None = None,
    *,
    color: str | None = None,
) -> Axes:
    """Plot an underwater curve: the drawdown from each running peak.

    Drawdown is ``series / running_max - 1``, so the line sits at zero whenever
    the series makes a new high and dips below the rest of the time. It is the
    honest picture of downside that an equity curve hides: a chart that spends
    most of its time underwater has been painful to hold.

    Args:
        series: The level series (prices, an index, cumulative returns).
        x: Optional x positions; defaults to ``0..n-1``.
        ax: Target axes (defaults to the current axes).
        color: Fill and line color (default: primary).

    Returns:
        The axes.
    """
    ax = _base.current_ax(ax)
    levels = np.asarray(series, dtype=float)
    xs = np.arange(levels.size) if x is None else np.asarray(x, dtype=float)
    running_peak = np.maximum.accumulate(levels)
    drawdown = levels / running_peak - 1.0
    paint = color or _base.primary()
    ax.fill_between(xs, drawdown, 0.0, color=paint, alpha=0.35, zorder=1)
    ax.plot(xs, drawdown, color=paint, linewidth=1.8, zorder=2)
    ax.axhline(0.0, color=_base.foreground(), linewidth=1.0)
    ax.set_ylim(top=0.0)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _p: f"{v:.0%}"))
    return ax


def streamgraph(
    data: ArrayLike,
    x: ArrayLike | None = None,
    labels: Sequence[str] | None = None,
    ax: Axes | None = None,
    *,
    baseline: str = "wiggle",
    alpha: float = 0.9,
) -> Axes:
    """Stack series around a flowing center line (a ThemeRiver / streamgraph).

    A streamgraph trades a readable absolute axis for a strong read of how a
    composition shifts: each band's thickness is its value, and the wiggle
    baseline minimizes the wobble so trends in the bands stay legible. Use it for
    "what is the mix, and how does it move", not for reading exact totals.

    Args:
        data: 2-D array, one row per series, one column per time step.
        x: Optional time positions; defaults to ``0..n-1``.
        labels: Series labels for the legend.
        ax: Target axes (defaults to the current axes).
        baseline: Stack baseline; ``"wiggle"`` is the streamgraph default,
            ``"sym"`` centers on zero, ``"zero"`` is a plain stacked area.
        alpha: Band opacity.

    Returns:
        The axes.
    """
    ax = _base.current_ax(ax)
    matrix = np.asarray(data, dtype=float)
    xs = np.arange(matrix.shape[1]) if x is None else np.asarray(x, dtype=float)
    colors = [_base.nth(i) for i in range(matrix.shape[0])]
    ax.stackplot(
        xs,
        *matrix,
        baseline=cast("Any", baseline),
        colors=colors,
        labels=list(labels) if labels else (),
        alpha=alpha,
    )
    # The y-axis of a wiggle stream carries no fixed zero, so reading values off
    # it would mislead; drop it and let the bands speak.
    if baseline in {"wiggle", "sym"}:
        ax.yaxis.set_visible(False)
        ax.spines["left"].set_visible(False)
    return ax


def rolling_corr_heatmap(
    series: ArrayLike,
    window: int,
    labels: Sequence[str] | None = None,
    ax: Axes | None = None,
    *,
    cmap: str | None = None,
) -> AxesImage:
    """Show how every pairwise correlation drifts over time, as a heatmap.

    Each row is one pair of series; each column is a window ending at that time
    step; the cell is their Pearson correlation in that window, on a diverging
    scale fixed to [-1, 1] so the neutral pivot reads as "no relationship". It
    surfaces the thing a static correlation matrix hides: that correlations move,
    and tend to converge toward 1 exactly when diversification is needed most.

    Args:
        series: 2-D array shaped ``(time, n_series)``.
        window: Rolling window length, in time steps.
        labels: Names for the series, used to label each pair row.
        ax: Target axes (defaults to the current axes).
        cmap: Diverging colormap name; defaults to the theme's diverging map.

    Returns:
        The heatmap :class:`~matplotlib.image.AxesImage`.
    """
    ax = _base.current_ax(ax)
    data = np.asarray(series, dtype=float)
    n_time, n_series = data.shape
    if window > n_time:
        raise ValueError(f"window {window} exceeds series length {n_time}")
    names = list(labels) if labels else [str(i) for i in range(n_series)]
    pairs = list(combinations(range(n_series), 2))

    heat = np.empty((len(pairs), n_time - window + 1))
    for col, end in enumerate(range(window - 1, n_time)):
        block = data[end - window + 1 : end + 1]
        corr = np.corrcoef(block, rowvar=False)
        for row, (i, j) in enumerate(pairs):
            heat[row, col] = corr[i, j]

    colormap: str | Colormap = cmap if cmap is not None else _base.diverging_cmap()
    image = ax.imshow(
        heat, aspect="auto", cmap=colormap, vmin=-1.0, vmax=1.0, origin="lower"
    )
    ax.set_yticks(range(len(pairs)), [f"{names[i]}/{names[j]}" for i, j in pairs])
    ax.set_xlabel(f"window end (length {window})")
    return image
