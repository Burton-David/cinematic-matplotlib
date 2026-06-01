"""Studio Ghibli: soft, pastoral palettes with calm, organic shapes."""

from __future__ import annotations

import numpy as np
from matplotlib.axes import Axes
from numpy.typing import ArrayLike

from .base import CinematicStyle


class Ghibli(CinematicStyle):
    """Gentle, nature-inspired styling for distributions and flowing series."""

    name = "ghibli"
    base_style = "seaborn-v0_8-whitegrid"
    background = "#fdfdf8"
    surface = "#fdfdf8"
    foreground = "#4a4a40"
    edge_color = "#c7c7ba"
    grid_color = "#e8e8e0"
    grid_alpha = 0.7
    font_family = "serif"
    cmap = "YlGn"
    palette = (
        "#6B8E23",
        "#87CEEB",
        "#D2B48C",
        "#FFB6C1",
        "#9ACD32",
        "#F4A460",
        "#90EE90",
    )
    colors = {
        "primary": "#6B8E23",
        "secondary": "#87CEEB",
        "accent": "#FFB6C1",
        "earth": "#D2B48C",
        "forest": "#6B8E23",
    }

    def plot_landscape(self, data: ArrayLike, ax: Axes | None = None) -> Axes:
        """Stack translucent "forest" and "earth" layers under a ridge line.

        Args:
            data: The series forming the upper ridge of the landscape.
            ax: Existing axes to draw on, or ``None`` to create a styled figure.

        Returns:
            The axes the chart was drawn on.
        """
        values = np.asarray(data, dtype=float)
        x = np.arange(len(values))
        with self._target(ax, figsize=(12.0, 6.0)) as target:
            target.fill_between(
                x, values, color=self.colors["forest"], alpha=0.3, label="Forest"
            )
            target.fill_between(
                x, values * 0.6, color=self.colors["earth"], alpha=0.4, label="Earth"
            )
            target.plot(x, values, color=self.colors["forest"], linewidth=2)
            target.legend()
            return target

    def plot_flow(self, time_series: ArrayLike, ax: Axes | None = None) -> Axes:
        """Draw a flowing series with a filled body and a smoothed overlay.

        Args:
            time_series: The series to render.
            ax: Existing axes to draw on, or ``None`` to create a styled figure.

        Returns:
            The axes the chart was drawn on.
        """
        values = np.asarray(time_series, dtype=float)
        x = np.arange(len(values))
        window = min(5, len(values)) or 1
        smoothed = np.convolve(values, np.ones(window) / window, mode="same")
        with self._target(ax) as target:
            target.plot(x, values, color=self.colors["primary"], linewidth=3, alpha=0.8)
            target.fill_between(x, values, color=self.colors["primary"], alpha=0.2)
            target.plot(
                x,
                smoothed,
                color=self.colors["secondary"],
                linewidth=2,
                linestyle="--",
                alpha=0.7,
            )
            return target
