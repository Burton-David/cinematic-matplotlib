"""Comparison and ranking idioms: dumbbell, lollipop, slope, bump.

Charts that put a small number of labeled items side by side and let the reader
compare them directly, instead of reading values off a shared axis.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from matplotlib.axes import Axes
from numpy.typing import ArrayLike

from . import _base


def dumbbell(
    labels: Sequence[str],
    start: ArrayLike,
    end: ArrayLike,
    ax: Axes | None = None,
    *,
    start_color: str | None = None,
    end_color: str | None = None,
    size: float = 8.0,
) -> Axes:
    """Draw a before/after dumbbell per category: two dots joined by a bar.

    The gap between the dots is the story, so the connector is what the eye
    lands on. The start dot is muted and the end dot takes the focal color, so
    direction reads without a legend.

    Args:
        labels: Category labels, top to bottom.
        start: Value at the start of each pair.
        end: Value at the end of each pair.
        ax: Target axes (defaults to the current axes).
        start_color: Override for the start dot (default: muted).
        end_color: Override for the end dot (default: primary).
        size: Dot size in points.

    Returns:
        The axes.
    """
    ax = _base.current_ax(ax)
    start = np.asarray(start, dtype=float)
    end = np.asarray(end, dtype=float)
    y = np.arange(len(labels))
    c_start = start_color or _base.muted()
    c_end = end_color or _base.primary()
    for yi, x0, x1 in zip(y, start, end, strict=True):
        ax.plot([x0, x1], [yi, yi], color=_base.muted(), linewidth=2.5, zorder=1)
    ax.scatter(start, y, s=size**2, color=c_start, zorder=2, label="start")
    ax.scatter(end, y, s=size**2, color=c_end, zorder=3, label="end")
    ax.set_yticks(y, list(labels))
    ax.margins(y=0.1)
    return ax


def lollipop(
    labels: Sequence[str],
    values: ArrayLike,
    ax: Axes | None = None,
    *,
    baseline: float = 0.0,
    orient: str = "h",
    color: str | None = None,
    size: float = 8.0,
) -> Axes:
    """Plot lollipops: a thin stem to a dot, the decluttered cousin of a bar.

    A lollipop carries the same information as a bar but with far less ink, which
    keeps a long category list from turning into a wall of color.

    Args:
        labels: Category labels.
        values: Value per category.
        ax: Target axes (defaults to the current axes).
        baseline: Where stems start (often 0, or a reference level).
        orient: ``"h"`` for horizontal lollipops, ``"v"`` for vertical.
        color: Override the stem and dot color (default: primary).
        size: Dot size in points.

    Returns:
        The axes.
    """
    ax = _base.current_ax(ax)
    values = np.asarray(values, dtype=float)
    pos = np.arange(len(labels))
    paint = color or _base.primary()
    if orient == "h":
        ax.hlines(pos, baseline, values, color=_base.muted(), linewidth=1.6, zorder=1)
        ax.scatter(values, pos, s=size**2, color=paint, zorder=2)
        ax.set_yticks(pos, list(labels))
        ax.margins(y=0.08)
    else:
        ax.vlines(pos, baseline, values, color=_base.muted(), linewidth=1.6, zorder=1)
        ax.scatter(pos, values, s=size**2, color=paint, zorder=2)
        ax.set_xticks(pos, list(labels))
        ax.margins(x=0.08)
    return ax


def slope(
    labels: Sequence[str],
    before: ArrayLike,
    after: ArrayLike,
    ax: Axes | None = None,
    *,
    before_label: str = "Before",
    after_label: str = "After",
    value_fmt: str = "{:.0f}",
) -> Axes:
    """Draw a slopegraph: two columns of values joined per category.

    A slopegraph answers "what changed between two states" for a handful of
    series at once, where the slope of each line is the change. Each line takes
    a cycle color; the end labels carry the values so the axis can stay bare.

    Args:
        labels: Series labels.
        before: Left-column value per series.
        after: Right-column value per series.
        ax: Target axes (defaults to the current axes).
        before_label: Heading for the left column.
        after_label: Heading for the right column.
        value_fmt: Format for the value annotations.

    Returns:
        The axes.
    """
    ax = _base.current_ax(ax)
    before = np.asarray(before, dtype=float)
    after = np.asarray(after, dtype=float)
    for i, (lab, b, a) in enumerate(zip(labels, before, after, strict=True)):
        color = _base.nth(i)
        ax.plot([0, 1], [b, a], color=color, linewidth=2.0, marker="o", zorder=2)
        ax.annotate(
            f"{lab}  {value_fmt.format(b)}",
            (0, b),
            xytext=(-8, 0),
            textcoords="offset points",
            ha="right",
            va="center",
            color=color,
        )
        ax.annotate(
            f"{value_fmt.format(a)}  {lab}",
            (1, a),
            xytext=(8, 0),
            textcoords="offset points",
            ha="left",
            va="center",
            color=color,
        )
    ax.set_xticks([0, 1], [before_label, after_label])
    ax.set_xlim(-0.5, 1.5)
    ax.tick_params(left=False, labelleft=False)
    for side in ("left", "right", "top"):
        ax.spines[side].set_visible(False)
    return ax


def bump(
    values: ArrayLike,
    periods: Sequence[str] | None = None,
    labels: Sequence[str] | None = None,
    ax: Axes | None = None,
    *,
    size: float = 7.0,
    highest_is_best: bool = True,
) -> Axes:
    """Plot a bump chart: how a set of items trade ranks over time.

    Each row of *values* is one series measured across the columns; the builder
    converts values to ranks per column and draws each series as a line through
    its ranks, rank 1 at the top. It is the chart for "who is winning, and when
    did the order change".

    Args:
        values: 2-D array, one row per series, one column per period.
        periods: Column (time) labels.
        labels: Series labels, attached at the final period.
        ax: Target axes (defaults to the current axes).
        size: Marker size in points.
        highest_is_best: When true the largest value ranks 1; set false when a
            smaller value is better (lap time, error rate).

    Returns:
        The axes.
    """
    ax = _base.current_ax(ax)
    matrix = np.asarray(values, dtype=float)
    n_series, n_periods = matrix.shape
    # argsort twice turns values into ranks; negate first when larger is better.
    ordered = -matrix if highest_is_best else matrix
    ranks = ordered.argsort(axis=0).argsort(axis=0) + 1

    x = np.arange(n_periods)
    for i in range(n_series):
        color = _base.nth(i)
        ax.plot(x, ranks[i], color=color, linewidth=2.0, marker="o", markersize=size)
        if labels is not None:
            ax.annotate(
                str(labels[i]),
                (x[-1], ranks[i, -1]),
                xytext=(8, 0),
                textcoords="offset points",
                ha="left",
                va="center",
                color=color,
            )
    ax.set_yticks(range(1, n_series + 1))
    ax.set_ylim(n_series + 0.5, 0.5)  # inverted: rank 1 on top
    if periods is not None:
        ax.set_xticks(x, list(periods))
    ax.margins(x=0.08)
    return ax
