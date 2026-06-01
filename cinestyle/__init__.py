"""cinestyle: cinematic theming with color science, for matplotlib, Plotly and Altair.

Twenty-four film-inspired themes (plus a brand authoring API) that are
beautiful, correct, and accessible. Palettes and colormaps are derived in a
perceptual color space; any palette can be audited and repaired for color-vision
deficiency; and one theme spec drives matplotlib, Plotly or Altair. On
matplotlib a theme also brings bundled fonts, a neon glow and film-look LUTs
(those three are matplotlib-only).

    import cinestyle

    with cinestyle.use("blade_runner"):        # matplotlib, scoped
        ...

    cinestyle.register_plotly()                 # template="cinestyle-dune"
    cinestyle.register_altair(enable="ghibli")  # an Altair theme

    cinestyle.audit("blade_runner")             # colorblind-safety report
"""

from __future__ import annotations

from collections.abc import Sequence
from importlib.metadata import PackageNotFoundError, version
from typing import Any

from . import color
from .accessibility import (
    AccessibilityReport,
    accessible_variant,
    check_accessibility,
    contrast_ratio,
)
from .adapters import (
    register_altair,
    register_plotly,
    to_altair_theme,
    to_plotly_template,
    use_altair,
    use_plotly,
)
from .brand import Brand, define_brand
from .effects import add_glow, glow_artist
from .fonts import available_fonts, register_fonts
from .luts import Look
from .registry import (
    LOOKS,
    THEMES,
    get_look,
    get_theme,
    list_themes,
    register,
)
from .theme import Theme

# Bundled fonts must be registered before any theme sets ``font.family``.
register_fonts()

try:
    __version__ = version("cinestyle")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"


def use(name: str) -> Any:
    """Return a scoped context manager that applies theme *name*.

    Example:
        >>> with cinestyle.use("matrix"):
        ...     ...
    """
    return get_theme(name).use()


def apply(name: str) -> Theme:
    """Apply theme *name* to global rcParams; returns it (undo with ``.restore()``)."""
    return get_theme(name).apply()


def _resolve_palette(
    target: Theme | str | Sequence[str], background: str | None
) -> tuple[list[str], str | None]:
    if isinstance(target, Theme):
        return list(target.palette), background or target.background
    if isinstance(target, str):
        # A lone hex string is a one-color palette, not a theme name; a bare
        # name that is not a theme still errors helpfully via get_theme.
        if target.startswith("#"):
            return [target], background
        theme = get_theme(target)
        return list(theme.palette), background or theme.background
    return list(target), background


def audit(
    target: Theme | str | Sequence[str], background: str | None = None
) -> AccessibilityReport:
    """Audit any palette, theme name, or Theme for colorblind-safety and contrast.

    Example:
        >>> cinestyle.audit("blade_runner").safe
        >>> cinestyle.audit(["#D62728", "#2CA02C"]).summary()
    """
    palette, resolved_bg = _resolve_palette(target, background)
    return check_accessibility(palette, background=resolved_bg)


def repair(target: Theme | str | Sequence[str]) -> list[str]:
    """Return a colorblind-safe version of any palette, theme name, or Theme."""
    palette, _ = _resolve_palette(target, None)
    return accessible_variant(palette)


__all__ = [
    "AccessibilityReport",
    "Brand",
    "LOOKS",
    "Look",
    "THEMES",
    "Theme",
    "__version__",
    "accessible_variant",
    "add_glow",
    "apply",
    "audit",
    "available_fonts",
    "check_accessibility",
    "color",
    "contrast_ratio",
    "define_brand",
    "get_look",
    "get_theme",
    "glow_artist",
    "list_themes",
    "register",
    "register_altair",
    "register_fonts",
    "register_plotly",
    "repair",
    "to_altair_theme",
    "to_plotly_template",
    "use",
    "use_altair",
    "use_plotly",
]
