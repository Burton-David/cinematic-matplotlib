"""cinestyle: cinematic matplotlib theming, done with color science.

Ten film-inspired themes (and a brand authoring API) that are *beautiful,
correct, and accessible*: palettes and colormaps are derived in a perceptual
color space, bundled fonts make them reproducible, an optional glow brings the
neon looks to life, and any palette can be checked or repaired for color-vision
deficiency. cinestyle only sets rcParams and registers colormaps, so a theme
works across every chart type -- you never have to switch themes mid-deck.

Use a theme three ways::

    import cinestyle

    with cinestyle.use("blade_runner"):      # scoped
        ...

    cinestyle.register()                      # plt.style.use("cinestyle-dune")

    theme = cinestyle.get_theme("ghibli")     # the Theme object itself
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
from typing import Any

from . import color
from .accessibility import (
    AccessibilityReport,
    accessible_variant,
    check_accessibility,
    contrast_ratio,
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
    "register_fonts",
    "use",
]
