"""cinestyle: cinematic matplotlib styles plus a reusable-brand API.

Five film-inspired styles (Film Noir, Studio Ghibli, Wes Anderson, Blade Runner,
Star Wars) and a :class:`~cinestyle.brand.Brand` type for defining your own. Each
style can be used three ways:

* scoped context manager -- ``with FilmNoir().use(): ...``
* registered style sheet -- ``cinestyle.register(); plt.style.use("cinestyle-noir")``
* signature plotting helpers -- ``FilmNoir().plot_shadows(...)``
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

from .base import CinematicStyle
from .blade_runner import BladeRunner
from .brand import Brand, define_brand
from .ghibli import Ghibli
from .noir import FilmNoir
from .star_wars import StarWars
from .wes_anderson import WesAnderson

try:
    __version__ = version("cinestyle")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"

STYLES: tuple[type[CinematicStyle], ...] = (
    FilmNoir,
    Ghibli,
    WesAnderson,
    BladeRunner,
    StarWars,
)


def register(prefix: str = "cinestyle") -> list[str]:
    """Register every built-in style as a named matplotlib style sheet.

    After calling this, the styles are available via ``plt.style.use`` and
    appear in ``plt.style.available``.

    Args:
        prefix: Name prefix; styles register as ``<prefix>-<style name>``.

    Returns:
        The registered style-sheet names, e.g. ``["cinestyle-noir", ...]``.
    """
    return [style().register(f"{prefix}-{style.name}") for style in STYLES]


__all__ = [
    "BladeRunner",
    "Brand",
    "CinematicStyle",
    "FilmNoir",
    "Ghibli",
    "StarWars",
    "WesAnderson",
    "__version__",
    "define_brand",
    "register",
]
