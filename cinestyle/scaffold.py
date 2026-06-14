"""Editorial scaffolding: the chrome a finished figure needs every time.

A theme handles color and type; these helpers handle the layout moves that turn
a plot into a published exhibit and that are tedious to repeat: a finding-driven
title with a muted subtitle and a small source line, decluttered spines,
thousands/currency tick formatting, value labels, and a print-ready save.

They read the active theme through rcParams (``text.color`` and the rest), so a
call like :func:`finish` looks right under any theme without being told which
one is active.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from pathlib import Path

import matplotlib as mpl
import numpy as np
from matplotlib.axes import Axes
from matplotlib.axis import Axis
from matplotlib.container import BarContainer
from matplotlib.figure import Figure
from matplotlib.text import Text
from matplotlib.ticker import FuncFormatter

logger = logging.getLogger("cinestyle")

# The two dash characters house style forbids in figure text. Hyphen-minus and
# the figure dash are fine; these two are the ones that sneak in from prose.
_BANNED_DASHES = {"—": "em dash", "–": "en dash"}


def despine(ax: Axes, *, top: bool = True, right: bool = True) -> Axes:
    """Hide the top and right spines (the usual editorial declutter)."""
    if top:
        ax.spines["top"].set_visible(False)
    if right:
        ax.spines["right"].set_visible(False)
    return ax


def finish(
    ax: Axes,
    title: str,
    subtitle: str | None = None,
    source: str | None = None,
    *,
    despine_ax: bool = True,
) -> Axes:
    """Add a finding-driven title block, a source line, and declutter the axes.

    The title is the chart's finding, set bold and flush left above the plot;
    the subtitle is a muted second line for the supporting detail; the source is
    a small muted line at the figure's lower left. Colors come from the active
    theme, so this reads correctly without being passed one.

    Args:
        ax: The axes to finish.
        title: The finding. Stated as a claim, not a label ("Sales doubled in
            Q3", not "Quarterly sales").
        subtitle: Optional supporting line under the title.
        source: Optional provenance line for the figure's lower left.
        despine_ax: Hide the top and right spines.

    Returns:
        The axes, for chaining.
    """
    fg = mpl.rcParams["text.color"]
    ax.set_title("")  # finish owns the title block; clear any axes title first

    # Title and subtitle ride in axes-fraction space above the plot so they stay
    # flush-left with the data regardless of tick-label width.
    ax.text(
        0.0,
        1.10,
        title,
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=mpl.rcParams["axes.titlesize"],
        fontweight=mpl.rcParams["axes.titleweight"],
        color=fg,
    )
    if subtitle:
        ax.text(
            0.0,
            1.025,
            subtitle,
            transform=ax.transAxes,
            ha="left",
            va="bottom",
            fontsize=mpl.rcParams["font.size"] * 0.92,
            color=fg,
            alpha=0.72,
        )
    if source:
        ax.figure.text(
            0.01,
            0.01,
            source,
            ha="left",
            va="bottom",
            fontsize=mpl.rcParams["font.size"] * 0.78,
            color=fg,
            alpha=0.55,
        )
    if despine_ax:
        despine(ax)
    return ax


def _resolve_axis(ax: Axes, axis: str) -> Axis:
    if axis == "y":
        return ax.yaxis
    if axis == "x":
        return ax.xaxis
    raise ValueError(f"axis must be 'x' or 'y', got {axis!r}")


def thousands(ax: Axes, axis: str = "y") -> Axes:
    """Format an axis with thousands separators (12000 -> '12,000')."""
    _resolve_axis(ax, axis).set_major_formatter(
        FuncFormatter(lambda value, _pos: f"{value:,.0f}")
    )
    return ax


def currency(ax: Axes, axis: str = "y", symbol: str = "$") -> Axes:
    """Format an axis as currency with thousands separators ('$12,000').

    Negative values keep the sign in front of the symbol ('-$3,000'), which is
    how a finance reader expects a loss to read.
    """

    def fmt(value: float, _pos: int) -> str:
        sign = "-" if value < 0 else ""
        return f"{sign}{symbol}{abs(value):,.0f}"

    _resolve_axis(ax, axis).set_major_formatter(FuncFormatter(fmt))
    return ax


def value_labels(
    ax: Axes,
    fmt: str | Callable[[float], str] = "{:,.0f}",
    *,
    padding: float = 3.0,
    color: str | None = None,
) -> Axes:
    """Label the bars on *ax* with their values.

    Works on the bar containers matplotlib already tracks, so it labels grouped
    and stacked bars too. A no-op (with a logged note) if the axes holds no bars.

    Args:
        ax: The axes whose bars to label.
        fmt: A ``str.format`` template taking the value, or a callable value->str.
        padding: Points between the bar end and its label.
        color: Label color; defaults to the theme's text color.
    """
    containers = [c for c in ax.containers if isinstance(c, BarContainer)]
    if not containers:
        logger.warning("value_labels: no bar containers on these axes")
        return ax
    labeler = fmt if callable(fmt) else (lambda v: fmt.format(v))
    text_color = color or mpl.rcParams["text.color"]
    for container in containers:
        values = np.asarray(container.datavalues, dtype=float)
        labels = [labeler(float(v)) for v in values]
        ax.bar_label(container, labels=labels, padding=padding, color=text_color)
    return ax


def lint_text(fig: Figure) -> list[str]:
    """Report em or en dashes in any text the figure draws (house style ban).

    Scans every text artist (titles, labels, ticks, annotations, legends) and
    returns one message per offending string. It only reports; it never edits
    the figure. Each finding is also logged at WARNING.

    Returns:
        A list of human-readable findings; empty when the figure is clean.
    """
    findings: list[str] = []
    seen: set[tuple[int, str]] = set()
    for artist in fig.findobj(Text):
        text = artist.get_text()
        if not text:
            continue
        for char, label in _BANNED_DASHES.items():
            if char in text and (id(artist), char) not in seen:
                seen.add((id(artist), char))
                message = f"{label} in figure text: {text!r}"
                findings.append(message)
                logger.warning(message)
    return findings


def save(fig: Figure, path: str | Path, *, dpi: int = 300) -> Path:
    """Save a print-ready figure: 300 dpi, tight bbox, parents made, then closed.

    The saved face color is taken from the figure so a dark theme exports dark
    rather than on a default white card. The figure is closed afterwards, since
    a saved figure is usually done being used.

    Returns:
        The path written.
    """
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        target,
        dpi=dpi,
        bbox_inches="tight",
        facecolor=fig.get_facecolor(),
    )
    import matplotlib.pyplot as plt

    plt.close(fig)
    return target
