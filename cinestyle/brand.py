"""Define your own reusable matplotlib brand.

The original ``datavisualization_branding_matplotlib`` notebook made one durable
point: a visual brand is just a bundle of rcParams you define once and reuse
everywhere -- "do it once and forget about it." :class:`Brand` is that idea as a
typed, tested object. Describe your colors and chrome once, then scope it with
``use()``, register it as a named style sheet, or export it to a ``matplotlibrc``
file you can drop into any project.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from cycler import cycler

from ._rc import RcStyle, read_matplotlibrc

_RECOGNIZED_KEYS = frozenset(
    {
        "figure.facecolor",
        "savefig.facecolor",
        "axes.facecolor",
        "axes.edgecolor",
        "axes.labelcolor",
        "axes.titlecolor",
        "text.color",
        "xtick.color",
        "ytick.color",
        "font.family",
        "font.weight",
        "axes.grid",
        "axes.spines.top",
        "axes.spines.right",
        "axes.prop_cycle",
        "grid.color",
        "grid.alpha",
        "axes.linewidth",
    }
)


@dataclass
class Brand(RcStyle):
    """A reusable matplotlib brand built from a few declarative fields.

    Attributes:
        name: Identifier used as the default registration name.
        palette: Colors driving ``axes.prop_cycle``.
        background: Figure (and saved-figure) face color.
        surface: Axes face color; defaults to ``background`` when ``None``.
        foreground: Text, tick and title color.
        edge_color: Spine color; defaults to ``foreground`` when ``None``.
        grid_color: Grid color, or ``None`` to disable the grid.
        grid_alpha: Grid transparency when a grid is shown.
        font_family: Matplotlib font family.
        font_weight: Default font weight.
        framed: When ``True``, show all four spines at 1.5pt.
        extra_rc: Any additional rcParams to overlay last.
    """

    name: str
    palette: Sequence[str]
    background: str = "white"
    surface: str | None = None
    foreground: str = "black"
    edge_color: str | None = None
    grid_color: str | None = None
    grid_alpha: float = 0.3
    font_family: str = "sans-serif"
    font_weight: str = "normal"
    framed: bool = False
    extra_rc: Mapping[str, Any] = field(default_factory=dict)

    def as_rc(self) -> dict[str, Any]:
        """Assemble the rcParams mapping for this brand."""
        surface = self.surface if self.surface is not None else self.background
        edge = self.edge_color if self.edge_color is not None else self.foreground
        rc: dict[str, Any] = {
            "figure.facecolor": self.background,
            "savefig.facecolor": self.background,
            "axes.facecolor": surface,
            "axes.edgecolor": edge,
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
        if self.grid_color is not None:
            rc["grid.color"] = self.grid_color
            rc["grid.alpha"] = self.grid_alpha
        if self.framed:
            rc["axes.linewidth"] = 1.5
        rc.update(self.extra_rc)
        return rc

    @classmethod
    def from_matplotlibrc(cls, path: str | Path, name: str = "imported") -> Brand:
        """Build a brand from an existing matplotlibrc file.

        Recognized chrome keys map onto the brand's fields; anything else is
        preserved in :attr:`extra_rc`, so a round-trip through
        :meth:`to_matplotlibrc` is lossless.

        Args:
            path: Path to the matplotlibrc file.
            name: Name to give the resulting brand.

        Returns:
            A :class:`Brand` reconstructed from the file.
        """
        rc = read_matplotlibrc(path)
        cyc = rc.get("axes.prop_cycle")
        palette = list(cyc.by_key().get("color", [])) if cyc is not None else []
        family = rc.get("font.family", "sans-serif")
        if isinstance(family, list | tuple):
            family = family[0] if family else "sans-serif"
        extra = {k: v for k, v in rc.items() if k not in _RECOGNIZED_KEYS}
        return cls(
            name=name,
            palette=palette,
            background=str(rc.get("figure.facecolor", "white")),
            surface=str(rc.get("axes.facecolor", rc.get("figure.facecolor", "white"))),
            foreground=str(rc.get("text.color", "black")),
            edge_color=str(rc.get("axes.edgecolor", rc.get("text.color", "black"))),
            grid_color=(
                str(rc["grid.color"])
                if rc.get("axes.grid") and "grid.color" in rc
                else None
            ),
            grid_alpha=float(rc.get("grid.alpha", 0.3)),
            font_family=str(family),
            font_weight=str(rc.get("font.weight", "normal")),
            framed=bool(rc.get("axes.spines.top", False)),
            extra_rc=extra,
        )


def define_brand(
    name: str,
    *,
    palette: Sequence[str],
    background: str = "white",
    surface: str | None = None,
    foreground: str = "black",
    edge_color: str | None = None,
    grid_color: str | None = None,
    grid_alpha: float = 0.3,
    font_family: str = "sans-serif",
    font_weight: str = "normal",
    framed: bool = False,
    extra_rc: Mapping[str, Any] | None = None,
) -> Brand:
    """Create a :class:`Brand` with keyword-only ergonomics.

    Example:
        >>> brand = define_brand(
        ...     "acme",
        ...     palette=["#0B5FFF", "#FF6B00", "#00B5AD"],
        ...     background="#FBFBFD",
        ...     foreground="#1A1A2E",
        ...     grid_color="#E3E3EA",
        ... )
        >>> brand.register()          # plt.style.use("cinestyle-acme")
        >>> with brand.use():
        ...     ...

    Returns:
        The configured brand.
    """
    return Brand(
        name=name,
        palette=list(palette),
        background=background,
        surface=surface,
        foreground=foreground,
        edge_color=edge_color,
        grid_color=grid_color,
        grid_alpha=grid_alpha,
        font_family=font_family,
        font_weight=font_weight,
        framed=framed,
        extra_rc=dict(extra_rc or {}),
    )
