"""Post-processing visual effects, principally the neon glow/bloom.

Glow cannot live in rcParams (there is no rc key for path effects), so it is a
deliberate post-process step you apply after drawing. The implementation stacks
translucent :class:`~matplotlib.patheffects.Stroke` layers of increasing width
beneath the original artist: one extra artist's worth of work, rather than
redrawing each line many times.
"""

from __future__ import annotations

from typing import Any, cast

import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
from matplotlib.artist import Artist
from matplotlib.axes import Axes
from matplotlib.collections import Collection
from matplotlib.colors import to_hex
from matplotlib.lines import Line2D
from matplotlib.patches import Patch


def _artist_color(artist: Artist) -> str:
    if isinstance(artist, Line2D):
        return to_hex(artist.get_color())
    if isinstance(artist, Patch):
        return to_hex(artist.get_edgecolor())
    return "white"


def _base_linewidth(artist: Artist) -> float:
    getter = getattr(artist, "get_linewidth", None)
    if getter is None:
        return 1.5
    value = getter()
    if isinstance(value, list | tuple) or hasattr(value, "__len__"):
        return float(value[0]) if len(value) else 1.5
    return float(value)


def glow_artist(
    artist: Artist,
    *,
    intensity: float = 0.6,
    layers: int = 6,
    color: str | None = None,
) -> None:
    """Give a single artist a soft glow via stacked stroke path-effects.

    Args:
        artist: A line, patch or collection to make glow.
        intensity: Glow strength in roughly [0, 1].
        layers: Number of halo layers; more is smoother but slower.
        color: Override glow color; defaults to the artist's own color.
    """
    glow_color = color or _artist_color(artist)
    base_lw = _base_linewidth(artist)
    effects: list[path_effects.AbstractPathEffect] = []
    for i in range(layers, 0, -1):
        width = base_lw + (i / layers) * (4.0 + 16.0 * intensity)
        alpha = 0.45 * intensity / layers
        effects.append(
            path_effects.Stroke(linewidth=width, foreground=glow_color, alpha=alpha)
        )
    effects.append(path_effects.Normal())
    artist.set_path_effects(effects)


def add_glow(
    ax: Axes | None = None,
    *,
    intensity: float = 0.6,
    layers: int = 6,
    lines: bool = True,
    patches: bool = False,
) -> Axes:
    """Apply a glow to the artists already drawn on *ax*.

    Call after plotting. By default it glows line plots (the most effective
    target); enable ``patches`` to glow bars and filled areas too.

    Args:
        ax: Target axes; defaults to the current axes.
        intensity: Glow strength in roughly [0, 1].
        layers: Number of halo layers per artist.
        lines: Glow ``Line2D`` artists.
        patches: Glow ``Patch`` artists (bars, areas).

    Returns:
        The axes, for chaining.
    """
    ax = ax or plt.gca()
    if lines:
        for line in ax.get_lines():
            glow_artist(line, intensity=intensity, layers=layers)
    if patches:
        for patch in ax.patches:
            glow_artist(patch, intensity=intensity, layers=layers)
    return ax


def glow_collection(
    collection: Collection, *, intensity: float = 0.6, layers: int = 6
) -> None:
    """Apply a glow to a collection (e.g. a scatter ``PathCollection``)."""
    edge = collection.get_edgecolor()
    color = to_hex(cast(Any, edge[0])) if len(edge) else None
    glow_artist(collection, intensity=intensity, layers=layers, color=color)
