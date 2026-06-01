"""The :class:`Theme`: one object that fully describes a cinematic look.

A theme bundles everything needed to make matplotlib speak in a film's visual
language: the chrome (backgrounds, text, grid, spines), a perceptually-derived
categorical palette and matching colormaps, a bundled font, and optional cues
for effects (glow) and film-look LUTs. It is a *pure styling* object: it sets
rcParams and registers colormaps, so it works across every chart type without
wrapping any plotting call. There is no ``plot_*`` API to outgrow.

A theme is defined declaratively from a few sourced "hero" colors; the palette
and colormaps are derived from them on first use via :mod:`cinestyle.color`.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from functools import cached_property
from typing import Any

import matplotlib as mpl
import matplotlib.colors as mcolors
import numpy as np
from cycler import cycler
from matplotlib.colors import LinearSegmentedColormap

from . import color as _color
from ._rc import RcStyle, register_style


@dataclass
class Theme(RcStyle):
    """A complete, reusable cinematic matplotlib theme.

    Attributes:
        name: Identifier, e.g. ``"blade_runner"``.
        heroes: Sourced signature colors; the first is treated as primary.
        background: Figure / saved-figure face color.
        surface: Axes face color.
        foreground: Primary text, tick, title and spine color.
        muted: Secondary color for grid lines and de-emphasized chrome.
        grid: Whether to draw a grid.
        framed: Show all four spines (vs. just left/bottom).
        font_family: Registered font family the theme uses everywhere.
        font_weight: Default font weight.
        title_weight: Weight for axes and figure titles.
        cycle_length: Number of colors in the derived categorical cycle.
        seq_anchor: Hue source for the sequential colormap (default: primary).
        div_pair: Two colors for the diverging colormap (default: first and last hero).
        glow: Suggested default glow intensity for :func:`cinestyle.add_glow`.
        look: Name of the film-look LUT associated with this theme, if any.
        film: Which film / color grade this theme targets (documentation).
        note: Provenance of the palette (documentation).
    """

    name: str
    heroes: tuple[str, ...]
    background: str
    surface: str
    foreground: str
    muted: str
    grid: bool = True
    framed: bool = False
    font_family: str = "DejaVu Sans"
    font_weight: str = "normal"
    title_weight: str = "bold"
    cycle_length: int = 8
    palette_override: tuple[str, ...] | None = None
    seq_anchor: str | None = None
    div_pair: tuple[str, str] | None = None
    glow: float = 0.0
    look: str | None = None
    film: str = ""
    note: str = ""
    extra_rc: Mapping[str, Any] = field(default_factory=dict)

    @cached_property
    def palette(self) -> list[str]:
        """The categorical color cycle, derived from the heroes (mood-preserving).

        An explicit ``palette_override`` (used by variants such as the
        colorblind-safe one) takes precedence over derivation.
        """
        if self.palette_override is not None:
            return list(self.palette_override)
        # Constrain *added* colors to a lightness band that stays visible against
        # the theme's surface (the sourced heroes are always kept verbatim): on a
        # dark theme keep extensions clearly lighter than the background, and the
        # reverse on a light theme.
        surface_l = _color.lightness(self.surface)
        if surface_l < 0.5:
            band = (max(0.42, surface_l + 0.2), 0.9)  # lighter than a dark surface
        else:
            band = (0.32, min(0.72, surface_l - 0.1))  # darker than a light surface
        return _color.categorical_cycle(self.heroes, self.cycle_length, lightness=band)

    @property
    def primary(self) -> str:
        """The theme's primary color (first hero)."""
        return self.heroes[0]

    @property
    def sequential_name(self) -> str:
        return f"cinestyle:{self.name}"

    @property
    def diverging_name(self) -> str:
        return f"cinestyle:{self.name}_div"

    @cached_property
    def sequential(self) -> LinearSegmentedColormap:
        """A single-hue sequential colormap with monotonic lightness."""
        anchor = self.seq_anchor or self.primary
        return _color.sequential_cmap(anchor, self.sequential_name)

    @cached_property
    def diverging(self) -> LinearSegmentedColormap:
        """A diverging colormap with symmetric arms between two hero hues."""
        low, high = self.div_pair or (self.heroes[0], self.heroes[-1])
        return _color.diverging_cmap(low, high, self.diverging_name)

    @cached_property
    def colormaps(self) -> dict[str, LinearSegmentedColormap]:
        """All colormaps this theme contributes, keyed by registered name."""
        return {
            self.sequential_name: self.sequential,
            f"{self.sequential_name}_r": self.sequential.reversed(),
            self.diverging_name: self.diverging,
            f"{self.diverging_name}_r": self.diverging.reversed(),
        }

    def colormap_hex(self, which: str = "sequential", n: int = 9) -> list[str]:
        """Sample a colormap to *n* hex stops.

        This is the bridge that lets a theme leave matplotlib: a Colormap object
        is not portable, but the hex stops it samples to are accepted as a color
        scale by Plotly, Altair and the rest.
        """
        if which == "sequential":
            cmap = self.sequential
        elif which == "diverging":
            cmap = self.diverging
        else:
            raise ValueError(
                f"which must be 'sequential' or 'diverging', got {which!r}"
            )
        return [mcolors.to_hex(cmap(v)) for v in np.linspace(0.0, 1.0, n)]

    def _register_assets(self) -> None:
        """Register this theme's colormaps and named colors (idempotent)."""
        for cmap_name, cmap in self.colormaps.items():
            if cmap_name not in mpl.colormaps:
                mpl.colormaps.register(cmap, name=cmap_name)
        named = mcolors.get_named_colors_mapping()
        for i, hero in enumerate(self.heroes):
            named[f"cinestyle:{self.name}-{i + 1}"] = hero

    def as_rc(self) -> dict[str, Any]:
        """Assemble the full rcParams mapping that defines this theme.

        Sets chrome, fonts, the categorical ``prop_cycle`` and the default image
        colormap, plus colors for artists that have their own rcParams (boxplots,
        patches, legends), so the theme reads correctly across chart types.
        """
        rc: dict[str, Any] = {
            # Figure / save
            "figure.facecolor": self.background,
            "figure.edgecolor": self.background,
            "savefig.facecolor": self.background,
            "savefig.edgecolor": self.background,
            "figure.titlesize": "large",
            "figure.titleweight": self.title_weight,
            # Axes
            "axes.facecolor": self.surface,
            "axes.edgecolor": self.foreground,
            "axes.labelcolor": self.foreground,
            "axes.titlecolor": self.foreground,
            "axes.titleweight": self.title_weight,
            "axes.labelweight": self.font_weight,
            "axes.linewidth": 1.5 if self.framed else 1.0,
            "axes.axisbelow": True,
            "axes.grid": self.grid,
            "axes.spines.top": self.framed,
            "axes.spines.right": self.framed,
            "axes.prop_cycle": cycler(color=self.palette),
            # Text / fonts
            "text.color": self.foreground,
            "font.family": self.font_family,
            "font.weight": self.font_weight,
            # Ticks
            "xtick.color": self.foreground,
            "ytick.color": self.foreground,
            "xtick.labelcolor": self.foreground,
            "ytick.labelcolor": self.foreground,
            # Grid
            "grid.color": self.muted,
            "grid.alpha": 0.4,
            "grid.linewidth": 0.8,
            # Lines / markers / patches
            "lines.linewidth": 2.0,
            "lines.solid_capstyle": "round",
            "patch.edgecolor": self.foreground,
            "patch.force_edgecolor": False,
            "scatter.edgecolors": "none",
            "hatch.color": self.foreground,
            # Images
            "image.cmap": self.sequential_name,
            # Legend
            "legend.facecolor": self.surface,
            "legend.edgecolor": self.foreground,
            "legend.framealpha": 0.85,
            "legend.labelcolor": self.foreground,
            # Boxplot (matplotlib styles these only via rcParams)
            "boxplot.boxprops.color": self.foreground,
            "boxplot.whiskerprops.color": self.foreground,
            "boxplot.capprops.color": self.foreground,
            "boxplot.flierprops.markeredgecolor": self.foreground,
            "boxplot.medianprops.color": self.primary,
            "boxplot.meanprops.markerfacecolor": self.primary,
            "boxplot.meanprops.markeredgecolor": self.primary,
        }
        rc.update(self.extra_rc)
        return rc

    def register(self, name: str | None = None) -> str:
        """Register the style sheet *and* this theme's colormaps and colors."""
        self._register_assets()
        return register_style(name or f"cinestyle-{self.name}", self.as_rc())

    def use(self) -> Any:
        """Scoped context manager; ensures colormaps are registered first."""
        self._register_assets()
        return super().use()

    def apply(self) -> Theme:
        """Apply globally; ensures colormaps are registered first."""
        self._register_assets()
        super().apply()
        return self

    def accessible(self) -> Theme:
        """Return a colorblind-safe variant of this theme.

        Reorders and nudges the categorical palette so colors stay distinct
        under color-vision deficiency, keeping the theme's chrome. Requires the
        ``[a11y]`` extra (``daltonlens``).
        """
        from .accessibility import accessible_variant

        safe = accessible_variant(self.palette)
        return Theme(
            name=f"{self.name}_accessible",
            heroes=self.heroes,
            background=self.background,
            surface=self.surface,
            foreground=self.foreground,
            muted=self.muted,
            grid=self.grid,
            framed=self.framed,
            font_family=self.font_family,
            font_weight=self.font_weight,
            title_weight=self.title_weight,
            palette_override=tuple(safe),
            seq_anchor=self.seq_anchor,
            div_pair=self.div_pair,
            glow=self.glow,
            look=self.look,
            film=self.film,
            note=f"Colorblind-safe variant of {self.name}.",
        )
