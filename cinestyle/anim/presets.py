"""Motion presets and the reveal/tween helpers a frame-update function uses.

An animation here is built the matplotlib way: you write an ``update(frame)`` that
redraws for a given step, and :func:`cinestyle.anim.animate` renders it. These
helpers are what that update reaches for: easing curves, value interpolation, and
a few reveal moves (unmask a line, grow bars, count a number up). The four named
presets pair an easing with a sensible frame rate and carry the *character* each
subject theme asks for, so a theme's ``motion`` attribute selects one.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
from matplotlib.container import BarContainer
from matplotlib.lines import Line2D
from numpy.typing import ArrayLike, NDArray


def linear(t: float) -> float:
    return t


def ease_out_cubic(t: float) -> float:
    """Fast then settling: the snap a counter or ticker wants."""
    return 1.0 - (1.0 - t) ** 3


def ease_in_out_sine(t: float) -> float:
    """Smooth in and out: a liquid, seeping motion."""
    return -(math.cos(math.pi * t) - 1.0) / 2.0


def ease_out_quad(t: float) -> float:
    """Decelerating: a climb that eases as it nears the summit."""
    return 1.0 - (1.0 - t) ** 2


@dataclass(frozen=True)
class Preset:
    """A named motion: an easing curve plus a default frame rate.

    Attributes:
        name: Identifier, matching a theme's ``motion`` attribute.
        fps: The frame rate that suits this motion.
        ease: Maps linear progress in [0, 1] to eased progress in [0, 1].
        description: What the motion evokes.
    """

    name: str
    fps: int
    ease: Callable[[float], float]
    description: str


PRESETS: dict[str, Preset] = {
    "ticker": Preset("ticker", 24, ease_out_cubic, "values snap up, then settle"),
    "flowing": Preset("flowing", 30, ease_in_out_sine, "a liquid, seeping reveal"),
    "ascending": Preset("ascending", 30, ease_out_quad, "a bottom-to-summit climb"),
    "map_fill": Preset("map_fill", 12, linear, "a steady fill, by date"),
}


def get_preset(preset: str | Preset | None) -> Preset | None:
    """Resolve a preset name (or pass a Preset through, or None)."""
    if preset is None or isinstance(preset, Preset):
        return preset
    try:
        return PRESETS[preset]
    except KeyError:
        raise KeyError(
            f"Unknown motion preset {preset!r}. Available: {', '.join(PRESETS)}"
        ) from None


def progress(frame: int, n_frames: int, ease: Callable[[float], float] | None) -> float:
    """Turn a frame index into eased progress in [0, 1]."""
    raw = 0.0 if n_frames <= 1 else frame / (n_frames - 1)
    return ease(raw) if ease else raw


def tween(start: ArrayLike, end: ArrayLike, t: float) -> NDArray[np.float64]:
    """Interpolate from *start* to *end* at progress *t* (scalars or arrays)."""
    a = np.asarray(start, dtype=float)
    b = np.asarray(end, dtype=float)
    return np.asarray(a + (b - a) * t, dtype=np.float64)


def count_up(target: float, t: float) -> float:
    """A number counting from zero to *target* at progress *t*."""
    return float(target) * t


def reveal_line(line: Line2D, x: ArrayLike, y: ArrayLike, t: float) -> Line2D:
    """Unmask *line* left to right, showing the first fraction *t* of its points."""
    xs = np.asarray(x, dtype=float)
    ys = np.asarray(y, dtype=float)
    keep = max(1, int(round(t * xs.size)))
    line.set_data(xs[:keep], ys[:keep])
    return line


def grow_bars(bars: BarContainer, targets: ArrayLike, t: float) -> BarContainer:
    """Grow each bar in *bars* from zero toward its target height at progress *t*."""
    heights = tween(np.zeros_like(np.asarray(targets, dtype=float)), targets, t)
    for bar, height in zip(bars, heights, strict=True):
        bar.set_height(float(height))
    return bars
