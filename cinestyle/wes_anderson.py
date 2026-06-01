"""Wes Anderson: framed, symmetrical layouts in curated pastels."""

from __future__ import annotations

import numpy as np
from matplotlib.axes import Axes
from matplotlib.patches import Rectangle
from numpy.typing import ArrayLike

from .base import CinematicStyle


class WesAnderson(CinematicStyle):
    """Symmetrical, pastel styling for balanced, categorical compositions."""

    name = "wes_anderson"
    background = "#F5F5DC"
    surface = "#F5F5DC"
    foreground = "#8B7355"
    edge_color = "#8B7355"
    framed = True
    font_family = "serif"
    cmap = "pink"
    palette = (
        "#FFCBA4",
        "#87CEEB",
        "#FFB6C1",
        "#C1FFC1",
        "#F4A460",
        "#DDA0DD",
        "#98FB98",
        "#FFE4B5",
    )
    colors = {
        "primary": "#FFCBA4",
        "secondary": "#87CEEB",
        "accent": "#FFB6C1",
        "earth": "#C1FFC1",
        "sunset": "#F4A460",
    }

    def plot_symmetry(
        self,
        left_data: ArrayLike,
        right_data: ArrayLike,
        labels: list[str] | None = None,
        ax: Axes | None = None,
    ) -> Axes:
        """Draw two pastel series mirrored around a center axis.

        Args:
            left_data: Magnitudes drawn to the right of center.
            right_data: Magnitudes drawn to the left of center.
            labels: Row labels; defaults to ``Item 1..n``.
            ax: Existing axes to draw on, or ``None`` to create a styled figure.

        Returns:
            The axes the chart was drawn on.
        """
        left = np.asarray(left_data, dtype=float)
        right = np.asarray(right_data, dtype=float)
        if labels is None:
            labels = [f"Item {i + 1}" for i in range(len(left))]
        with self._target(ax, figsize=(14.0, 6.0)) as target:
            y = np.arange(len(labels))
            target.barh(y, left, color=self.palette[0], alpha=0.85, label="Left")
            target.barh(y, -right, color=self.palette[1], alpha=0.85, label="Right")
            target.set_yticks(y)
            target.set_yticklabels(labels)
            target.axvline(0, color=self.foreground, linewidth=2)
            target.legend()
            return target

    def plot_grid(self, data: ArrayLike, ax: Axes | None = None) -> Axes:
        """Lay values out as a symmetrical grid of pastel, framed cells.

        Args:
            data: Values, one per cell, laid out row-major into a square grid.
            ax: Existing axes to draw on, or ``None`` to create a styled figure.

        Returns:
            The axes the chart was drawn on.
        """
        values = np.asarray(data, dtype=float)
        grid_size = int(np.ceil(np.sqrt(len(values)))) or 1
        with self._target(ax, figsize=(10.0, 10.0)) as target:
            for i in range(len(values)):
                row, col = divmod(i, grid_size)
                target.add_patch(
                    Rectangle(
                        (col, grid_size - row - 1),
                        1,
                        1,
                        facecolor=self.palette[i % len(self.palette)],
                        edgecolor=self.foreground,
                        linewidth=2,
                    )
                )
            target.set_xlim(0, grid_size)
            target.set_ylim(0, grid_size)
            target.set_aspect("equal")
            target.axis("off")
            return target
