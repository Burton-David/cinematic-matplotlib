"""Animation: render data reveals to mp4 or gif, in the theme's motion.

The engine wraps :class:`matplotlib.animation.FuncAnimation`; you supply an
``update(frame)`` and it handles the writer, the headless render and the graceful
mp4-to-gif fallback. The presets and reveal helpers are the vocabulary that
``update`` is written in, and a theme's ``motion`` attribute names the preset that
suits it (terminal counts up, petroleum flows, altitude ascends, atlas fills).
"""

from __future__ import annotations

from .engine import animate
from .presets import (
    PRESETS,
    Preset,
    count_up,
    ease_in_out_sine,
    ease_out_cubic,
    ease_out_quad,
    get_preset,
    grow_bars,
    linear,
    progress,
    reveal_line,
    tween,
)

__all__ = [
    "PRESETS",
    "Preset",
    "animate",
    "count_up",
    "ease_in_out_sine",
    "ease_out_cubic",
    "ease_out_quad",
    "get_preset",
    "grow_bars",
    "linear",
    "progress",
    "reveal_line",
    "tween",
]
