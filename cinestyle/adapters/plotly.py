"""Emit a cinestyle Theme as a Plotly template.

What crosses over: background, font family, the categorical colorway, and the
sequential/diverging colorscales. Fonts are best-effort: Plotly renders through
a browser engine, so a bundled font only shows if it is installed on the system
doing the rendering; the family name is set regardless.
"""

from __future__ import annotations

from importlib.util import find_spec
from typing import Any

from ..registry import get_theme, list_themes
from ..theme import Theme


def _require_plotly() -> None:
    if find_spec("plotly") is None:
        raise ImportError(
            "The Plotly adapter needs the optional dependency 'plotly' (and "
            "'kaleido' to export images): pip install 'cinestyle[plotly]'"
        )


def _scale(theme: Theme, which: str, n: int = 11) -> list[list[Any]]:
    stops = theme.colormap_hex(which, n)
    last = max(len(stops) - 1, 1)
    return [[i / last, color] for i, color in enumerate(stops)]


def to_plotly_template(theme: str | Theme) -> Any:
    """Build a ``plotly.graph_objects.layout.Template`` for *theme*."""
    _require_plotly()
    import plotly.graph_objects as go

    t = theme if isinstance(theme, Theme) else get_theme(theme)
    axis = {
        "gridcolor": t.muted,
        "linecolor": t.foreground,
        "zerolinecolor": t.muted,
        "tickcolor": t.foreground,
    }
    return go.layout.Template(
        layout={
            "paper_bgcolor": t.background,
            "plot_bgcolor": t.surface,
            "font": {"color": t.foreground, "family": f"{t.font_family}, sans-serif"},
            "title": {"font": {"color": t.foreground}},
            "colorway": list(t.palette),
            "colorscale": {
                "sequential": _scale(t, "sequential"),
                "sequentialminus": _scale(t, "sequential"),
                "diverging": _scale(t, "diverging"),
            },
            "xaxis": axis,
            "yaxis": axis,
        }
    )


def register_plotly(prefix: str = "cinestyle") -> list[str]:
    """Register every cinestyle theme as a Plotly template.

    After this, ``fig.update_layout(template="cinestyle-dune")`` works, and the
    names appear in ``plotly.io.templates``.

    Returns:
        The registered template names.
    """
    _require_plotly()
    import plotly.io as pio

    names = []
    for name in list_themes():
        template_name = f"{prefix}-{name}"
        pio.templates[template_name] = to_plotly_template(name)
        names.append(template_name)
    return names


def use_plotly(theme: str | Theme, prefix: str = "cinestyle") -> str:
    """Register *theme* and make it Plotly's default template; return its name."""
    _require_plotly()
    import plotly.io as pio

    t = theme if isinstance(theme, Theme) else get_theme(theme)
    template_name = f"{prefix}-{t.name}"
    pio.templates[template_name] = to_plotly_template(t)
    pio.templates.default = template_name
    return template_name
