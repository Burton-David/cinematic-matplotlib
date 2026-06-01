"""Register the bundled OFL fonts with matplotlib.

Themes reference real fonts (Share Tech Mono, EB Garamond, Jost, ...) so a chart looks
the same on every machine, not just on one that happens to have the font
installed. matplotlib's font manager keeps a persisted cache that does not know
about our bundled files, so the fonts are (idempotently) registered at import
time from the package's data directory.

All bundled fonts are licensed under the SIL Open Font License; the license
texts ship alongside them under ``data/fonts/licenses``.
"""

from __future__ import annotations

from functools import lru_cache
from importlib.resources import as_file, files

import matplotlib.font_manager as fm

_FONT_DIR = files("cinestyle") / "data" / "fonts"


@lru_cache(maxsize=1)
def register_fonts() -> list[str]:
    """Register every bundled font with matplotlib; return the family names.

    Idempotent: the work happens once per process. Call sites can rely on the
    returned families being resolvable by ``font.family`` afterwards.
    """
    families: set[str] = set()
    for entry in _FONT_DIR.iterdir():
        if entry.name.endswith((".ttf", ".otf")):
            with as_file(entry) as path:
                fm.fontManager.addfont(str(path))
                families.add(fm.FontProperties(fname=str(path)).get_name())
    return sorted(families)


def available_fonts() -> list[str]:
    """Return the bundled font family names (registering them if needed)."""
    return register_fonts()
