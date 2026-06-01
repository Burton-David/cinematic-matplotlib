"""Author your own reusable brand: a :class:`~cinestyle.theme.Theme` you define.

The original branding idea was "design a look once and reuse it everywhere."
With the theme engine, a brand is simply a theme you build yourself: give it a
palette and a little chrome and you get the same perceptually-derived colormaps,
scoped/global application, style-sheet registration and ``matplotlibrc`` export
that the built-in film themes have.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from coloraide import Color

from .theme import Theme

# A brand is just a Theme the user authors; the alias documents that intent.
Brand = Theme


def _mix(color1: str, color2: str, t: float) -> str:
    """Interpolate between two colors in OKLab and return a hex string."""
    return (
        Color(color1)
        .mix(color2, t, space="oklab")
        .convert("srgb")
        .to_string(hex=True, upper=True)
    )


def define_brand(
    name: str,
    *,
    palette: Sequence[str],
    background: str = "#FFFFFF",
    surface: str | None = None,
    foreground: str = "#1A1A1A",
    muted: str | None = None,
    grid: bool = True,
    framed: bool = False,
    font_family: str = "DejaVu Sans",
    font_weight: str = "normal",
    glow: float = 0.0,
    look: str | None = None,
    extra_rc: Mapping[str, Any] | None = None,
    note: str = "",
) -> Theme:
    """Create a reusable brand theme from a palette and a little chrome.

    Args:
        name: Brand identifier (used as the default registration name).
        palette: The brand's colors; the first is treated as primary.
        background: Figure face color.
        surface: Axes face color; defaults to ``background``.
        foreground: Text / tick / spine color.
        muted: Grid color; defaults to a blend of background and foreground.
        grid: Whether to show a grid.
        framed: Show all four spines.
        font_family: Font family to use throughout.
        font_weight: Default font weight.
        glow: Default glow intensity for :func:`cinestyle.add_glow`.
        look: Name of a film-look LUT to associate, if any.
        extra_rc: Any additional rcParams to overlay last.
        note: Free-form provenance note.

    Returns:
        A :class:`~cinestyle.theme.Theme` you can ``use()``, ``register()`` or
        export with ``to_matplotlibrc()``.

    Example:
        >>> brand = define_brand(
        ...     "acme",
        ...     palette=["#0B5FFF", "#FF6B00", "#00B5AD"],
        ...     background="#FBFBFD",
        ...     foreground="#1A1A2E",
        ... )
        >>> brand.register()
        >>> with brand.use():
        ...     ...
    """
    surface = surface if surface is not None else background
    muted = muted if muted is not None else _mix(background, foreground, 0.45)
    return Theme(
        name=name,
        heroes=tuple(palette),
        background=background,
        surface=surface,
        foreground=foreground,
        muted=muted,
        grid=grid,
        framed=framed,
        font_family=font_family,
        font_weight=font_weight,
        glow=glow,
        look=look,
        extra_rc=dict(extra_rc or {}),
        note=note or f"User-defined brand {name!r}.",
    )
