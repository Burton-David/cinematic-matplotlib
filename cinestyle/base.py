"""Base class shared by every cinematic style.

A concrete style is mostly declarative: it sets a handful of chrome attributes
(background, foreground, palette, ...) and the base assembles a complete
rcParams mapping from them. On top of that, :class:`CinematicStyle` offers a
small library of convenience plotting helpers that render *inside* the style's
scoped context, so calling them never leaks styling into the rest of a session.
"""

from __future__ import annotations

import contextlib
from collections.abc import Iterator, Sequence
from typing import Any

import matplotlib as mpl
import matplotlib.pyplot as plt
from cycler import cycler
from matplotlib.axes import Axes
from numpy.typing import ArrayLike

from ._rc import RcStyle

_DEFAULT_FIGSIZE = (10.0, 6.0)


class CinematicStyle(RcStyle):
    """Foundation for the film-inspired styles.

    Subclasses set the class attributes below to describe their look. The base
    turns those into rcParams (:meth:`as_rc`), styles individual axes
    (:meth:`style_axes`), and provides shared plotting helpers.

    Attributes:
        name: Short identifier, e.g. ``"noir"``.
        base_style: Optional matplotlib style sheet to layer underneath.
        background: Figure (and saved-figure) face color.
        surface: Axes face color.
        foreground: Text, tick and title color.
        edge_color: Spine color; falls back to ``foreground`` when ``None``.
        grid_color: Grid color, or ``None`` to disable the grid.
        grid_alpha: Grid transparency when a grid is shown.
        font_family: Matplotlib font family.
        font_weight: Default font weight.
        framed: When ``True``, show all four spines (Wes Anderson's framed look).
        cmap: Default colormap for image-based plots.
        palette: Colors driving ``axes.prop_cycle``.
        colors: Named semantic colors; must include ``"primary"``.
    """

    name: str = "cinematic"
    base_style: str | None = None
    background: str = "white"
    surface: str = "white"
    foreground: str = "black"
    edge_color: str | None = None
    grid_color: str | None = None
    grid_alpha: float = 0.3
    font_family: str = "sans-serif"
    font_weight: str = "normal"
    framed: bool = False
    cmap: str = "viridis"
    palette: Sequence[str] = ()
    colors: dict[str, str] = {"primary": "black"}

    def __init__(self, data: Any = None) -> None:
        """Create a style instance.

        Args:
            data: Optional payload kept for callers that thread data through a
                style object; unused by the library itself.
        """
        self.data = data

    @property
    def _edge(self) -> str:
        return self.edge_color if self.edge_color is not None else self.foreground

    def as_rc(self) -> dict[str, Any]:
        """Assemble the full rcParams mapping for this style.

        Layers the optional ``base_style`` sheet underneath, then applies the
        style's chrome, grid, fonts and ``prop_cycle``.
        """
        rc: dict[str, Any] = {}
        if self.base_style is not None:
            rc.update(mpl.style.library[self.base_style])
        rc.update(
            {
                "figure.facecolor": self.background,
                "savefig.facecolor": self.background,
                "axes.facecolor": self.surface,
                "axes.edgecolor": self._edge,
                "axes.labelcolor": self.foreground,
                "axes.titlecolor": self.foreground,
                "text.color": self.foreground,
                "xtick.color": self.foreground,
                "ytick.color": self.foreground,
                "font.family": self.font_family,
                "font.weight": self.font_weight,
                "axes.grid": self.grid_color is not None,
                "axes.spines.top": self.framed,
                "axes.spines.right": self.framed,
                "axes.prop_cycle": cycler(color=list(self.palette)),
            }
        )
        if self.grid_color is not None:
            rc["grid.color"] = self.grid_color
            rc["grid.alpha"] = self.grid_alpha
        if self.framed:
            rc["axes.linewidth"] = 1.5
        return rc

    def style_axes(self, ax: Axes) -> Axes:
        """Brand an existing axes in place and return it.

        Use this when you already hold an ``Axes`` created under default
        rcParams and want to apply the style's chrome to just that axes (the
        figure face color is updated too).
        """
        ax.figure.set_facecolor(self.background)
        ax.set_facecolor(self.surface)
        for side in ("top", "right"):
            ax.spines[side].set_visible(self.framed)
            if self.framed:
                ax.spines[side].set_color(self._edge)
                ax.spines[side].set_linewidth(1.5)
        for side in ("left", "bottom"):
            ax.spines[side].set_color(self._edge)
            if self.framed:
                ax.spines[side].set_linewidth(1.5)
        ax.tick_params(colors=self.foreground)
        ax.xaxis.label.set_color(self.foreground)
        ax.yaxis.label.set_color(self.foreground)
        ax.title.set_color(self.foreground)
        if self.grid_color is not None:
            ax.grid(visible=True, color=self.grid_color, alpha=self.grid_alpha)
        return ax

    @contextlib.contextmanager
    def _target(
        self, ax: Axes | None, figsize: tuple[float, float] = _DEFAULT_FIGSIZE
    ) -> Iterator[Axes]:
        """Yield a styled axes to draw on, leaking no global state.

        When *ax* is provided it is styled in place. Otherwise a new figure is
        created inside this style's scoped context, so the figure keeps the
        styling while global rcParams are restored on exit.
        """
        if ax is not None:
            self.style_axes(ax)
            yield ax
        else:
            with self.use():
                _fig, new_ax = plt.subplots(figsize=figsize)
                self.style_axes(new_ax)
                yield new_ax

    def plot_line(
        self, x: ArrayLike, y: ArrayLike, ax: Axes | None = None, **kwargs: Any
    ) -> Axes:
        """Draw a styled line plot and return the axes."""
        color = kwargs.pop("color", self.colors.get("primary"))
        with self._target(ax) as target:
            target.plot(x, y, color=color, linewidth=2, **kwargs)
            return target

    def plot_bar(
        self,
        categories: Sequence[str],
        values: ArrayLike,
        ax: Axes | None = None,
        **kwargs: Any,
    ) -> Axes:
        """Draw a styled bar chart and return the axes."""
        color = kwargs.pop("color", self.colors.get("primary"))
        with self._target(ax) as target:
            target.bar(categories, values, color=color, **kwargs)
            return target

    def plot_scatter(
        self, x: ArrayLike, y: ArrayLike, ax: Axes | None = None, **kwargs: Any
    ) -> Axes:
        """Draw a styled scatter plot and return the axes."""
        color = kwargs.pop("color", self.colors.get("primary"))
        alpha = kwargs.pop("alpha", 0.6)
        with self._target(ax) as target:
            target.scatter(x, y, color=color, alpha=alpha, **kwargs)
            return target

    def plot_histogram(
        self, data: ArrayLike, bins: int = 30, ax: Axes | None = None, **kwargs: Any
    ) -> Axes:
        """Draw a styled histogram and return the axes."""
        color = kwargs.pop("color", self.colors.get("primary"))
        alpha = kwargs.pop("alpha", 0.8)
        with self._target(ax) as target:
            target.hist(data, bins=bins, color=color, alpha=alpha, **kwargs)
            return target

    def plot_heatmap(
        self, data: ArrayLike, ax: Axes | None = None, **kwargs: Any
    ) -> Axes:
        """Draw a styled heatmap with a colorbar and return the axes."""
        cmap = kwargs.pop("cmap", self.cmap)
        with self._target(ax, figsize=(10.0, 8.0)) as target:
            im = target.imshow(data, aspect="auto", cmap=cmap, **kwargs)
            target.figure.colorbar(im, ax=target)
            return target

    def plot_area(
        self, x: ArrayLike, y: ArrayLike, ax: Axes | None = None, **kwargs: Any
    ) -> Axes:
        """Draw a styled filled-area plot and return the axes."""
        color = kwargs.pop("color", self.colors.get("primary"))
        alpha = kwargs.pop("alpha", 0.5)
        with self._target(ax) as target:
            target.fill_between(x, y, color=color, alpha=alpha, **kwargs)
            target.plot(x, y, color=color, linewidth=2)
            return target
