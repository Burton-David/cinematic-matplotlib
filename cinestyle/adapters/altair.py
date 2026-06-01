"""Emit a cinestyle Theme as an Altair (Vega-Lite) theme.

What crosses over: background, axis/legend chrome, font family, the categorical
range, and the sequential/diverging ranges. Requires Altair 5.5+ (the
``alt.theme`` API).
"""

from __future__ import annotations

from importlib.util import find_spec
from typing import Any

from ..registry import get_theme, list_themes
from ..theme import Theme


def _require_altair() -> None:
    if find_spec("altair") is None:
        raise ImportError(
            "The Altair adapter needs the optional dependency 'altair' (5.5+, and "
            "'vl-convert-python' to export images): pip install 'cinestyle[altair]'"
        )


def to_altair_theme(theme: str | Theme) -> dict[str, Any]:
    """Return the Vega-Lite theme config for *theme*.

    The chrome and ranges live under ``config`` (where Vega-Lite reads them);
    ``background`` is the one key that sits at the spec's top level.
    """
    t = theme if isinstance(theme, Theme) else get_theme(theme)
    sequential = t.colormap_hex("sequential", 9)
    diverging = t.colormap_hex("diverging", 9)
    return {
        "background": t.background,
        "config": {
            "view": {"fill": t.surface, "stroke": "transparent"},
            "axis": {
                "gridColor": t.muted,
                "domainColor": t.foreground,
                "tickColor": t.foreground,
                "labelColor": t.foreground,
                "titleColor": t.foreground,
            },
            "legend": {"labelColor": t.foreground, "titleColor": t.foreground},
            "title": {"color": t.foreground},
            # A CSS-style fallback so renderers that lack the bundled display
            # font (vl-convert, browsers) substitute a sans rather than drop text.
            "font": f"{t.font_family}, sans-serif",
            "range": {
                "category": list(t.palette),
                "ordinal": sequential,
                "ramp": sequential,
                "heatmap": sequential,
                "diverging": diverging,
            },
        },
    }


def _require_theme_api(alt: Any) -> Any:
    api = getattr(alt, "theme", None)
    if api is None:  # pragma: no cover - exercised only on old Altair
        raise ImportError(
            "The Altair adapter needs Altair 5.5+ (the alt.theme API). "
            "Upgrade with: pip install 'cinestyle[altair]'"
        )
    return api


def register_altair(prefix: str = "cinestyle", enable: str | None = None) -> list[str]:
    """Register every cinestyle theme as an Altair theme.

    Args:
        prefix: Names register as ``<prefix>-<theme>``.
        enable: If given, enable ``<prefix>-<enable>`` after registering.

    Returns:
        The registered theme names.
    """
    _require_altair()
    import altair as alt

    api = _require_theme_api(alt)
    names = []
    for name in list_themes():
        theme_name = f"{prefix}-{name}"
        # Bind `name` as a default so each registered callable keeps its own.
        api.register(theme_name, enable=False)(lambda name=name: to_altair_theme(name))
        names.append(theme_name)
    if enable is not None:
        api.enable(f"{prefix}-{enable}")
    return names


def use_altair(theme: str | Theme, prefix: str = "cinestyle") -> str:
    """Register *theme* and enable it as the active Altair theme; return its name."""
    _require_altair()
    import altair as alt

    api = _require_theme_api(alt)
    t = theme if isinstance(theme, Theme) else get_theme(theme)
    theme_name = f"{prefix}-{t.name}"
    api.register(theme_name, enable=True)(lambda: to_altair_theme(t))
    return theme_name
