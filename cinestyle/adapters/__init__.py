"""Backend adapters: emit a cinestyle Theme for non-matplotlib libraries.

A theme is mostly backend-neutral design tokens (palette, colormap stops,
background, foreground, fonts). These adapters translate those tokens into each
library's own theming system. They never re-derive color; the matplotlib themes
remain the source of truth.

Glow and film-look LUTs do not appear here: they are matplotlib render-pipeline
features and do not have an equivalent in Plotly or Altair.

Each adapter imports its backend lazily, so importing :mod:`cinestyle` never
requires Plotly or Altair to be installed.
"""

from __future__ import annotations

from .altair import register_altair, to_altair_theme, use_altair
from .plotly import register_plotly, to_plotly_template, use_plotly

__all__ = [
    "register_altair",
    "register_plotly",
    "to_altair_theme",
    "to_plotly_template",
    "use_altair",
    "use_plotly",
]
