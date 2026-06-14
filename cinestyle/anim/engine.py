"""Render a frame-update function to a movie file.

Thin wrapper over :class:`matplotlib.animation.FuncAnimation` that picks the
writer from the output extension and degrades honestly: an ``.mp4`` request with
no ffmpeg available (and no ``imageio-ffmpeg`` from the ``[anim]`` extra to supply
one) falls back to a gif beside it, with a logged warning, rather than failing.
Rendering is headless and deterministic: the same update function and frame count
produce the same file.
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any, cast

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter, FuncAnimation, PillowWriter
from matplotlib.figure import Figure

from .presets import Preset, get_preset

logger = logging.getLogger("cinestyle")


def _ffmpeg_ready() -> bool:
    """True if matplotlib can find an ffmpeg, wiring up imageio-ffmpeg if present."""
    if FFMpegWriter.isAvailable():
        return True
    try:
        import imageio_ffmpeg
    except ImportError:
        return False
    # imageio-ffmpeg bundles a binary; point matplotlib at it so mp4 works
    # without a system install (this is what the [anim] extra buys).
    mpl.rcParams["animation.ffmpeg_path"] = imageio_ffmpeg.get_ffmpeg_exe()
    return FFMpegWriter.isAvailable()


def animate(
    fig: Figure,
    frames: int | Iterable[object],
    update: Callable[[object], object],
    *,
    preset: str | Preset | None = None,
    fps: int | None = None,
    out: str | Path = "animation.mp4",
    dpi: int = 100,
) -> Path:
    """Render *update* over *frames* to a movie file, and return its path.

    Args:
        fig: The figure to animate.
        frames: A frame count, or an iterable of frame values passed to *update*.
        update: Called once per frame to redraw; the matplotlib animation func.
        preset: Optional motion preset (name or :class:`Preset`); sets the frame
            rate when *fps* is not given.
        fps: Frames per second; overrides the preset's rate.
        out: Output path. ``.mp4`` renders with ffmpeg, ``.gif`` with Pillow. An
            ``.mp4`` with no ffmpeg available falls back to ``.gif``.
        dpi: Render resolution.

    Returns:
        The path actually written (which may differ from *out* if mp4 fell back
        to gif).
    """
    chosen = get_preset(preset)
    rate = fps if fps is not None else (chosen.fps if chosen else 30)
    target = Path(out)
    target.parent.mkdir(parents=True, exist_ok=True)

    # blit is off, so the update's return value is unused; matplotlib's stub
    # still types it as returning artists, hence the cast.
    anim = FuncAnimation(fig, cast("Any", update), frames=frames, blit=False)
    if target.suffix.lower() == ".gif":
        anim.save(target, writer=PillowWriter(fps=rate), dpi=dpi)
    elif _ffmpeg_ready():
        anim.save(target, writer=FFMpegWriter(fps=rate), dpi=dpi)
    else:
        target = target.with_suffix(".gif")
        logger.warning(
            "no ffmpeg available; rendering %s as gif instead "
            "(install cinestyle[anim] for mp4)",
            out,
        )
        anim.save(target, writer=PillowWriter(fps=rate), dpi=dpi)

    plt.close(fig)
    return target
