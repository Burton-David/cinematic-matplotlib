"""Blade Runner: cyberpunk neons glowing on deep, dark backgrounds."""

from __future__ import annotations

from collections.abc import Sequence

from matplotlib.axes import Axes
from matplotlib.colors import LinearSegmentedColormap
from numpy.typing import ArrayLike

from .base import CinematicStyle


class BladeRunner(CinematicStyle):
    """Neon cyan-and-magenta styling for modern, futuristic, technical charts."""

    name = "blade_runner"
    base_style = "dark_background"
    background = "#0a0a0a"
    surface = "#0a0a0a"
    foreground = "#00FFFF"
    edge_color = "#00FFFF"
    grid_color = "#FF00FF"
    grid_alpha = 0.25
    cmap = "cool"
    palette = ("#00FFFF", "#FF00FF", "#FFFF00", "#0080FF", "#FF1493")
    colors = {
        "neon_cyan": "#00FFFF",
        "neon_magenta": "#FF00FF",
        "neon_yellow": "#FFFF00",
        "electric_blue": "#0080FF",
        "hot_pink": "#FF1493",
        "background": "#0a0a0a",
        "primary": "#00FFFF",
    }

    def plot_neon_lines(
        self,
        *datasets: ArrayLike,
        labels: Sequence[str] | None = None,
        ax: Axes | None = None,
    ) -> Axes:
        """Plot one or more series cycling through the neon palette.

        Args:
            *datasets: One or more series to draw.
            labels: Optional labels; default to ``Signal 1..n``.
            ax: Existing axes to draw on, or ``None`` to create a styled figure.

        Returns:
            The axes the chart was drawn on.
        """
        with self._target(ax, figsize=(12.0, 6.0)) as target:
            for i, data in enumerate(datasets):
                color = self.palette[i % len(self.palette)]
                label = labels[i] if labels and i < len(labels) else f"Signal {i + 1}"
                target.plot(data, color=color, linewidth=2.5, alpha=0.9, label=label)
            target.legend(facecolor=self.background, edgecolor=self.foreground)
            return target

    def plot_matrix(self, matrix: ArrayLike, ax: Axes | None = None) -> Axes:
        """Render a matrix through a custom cyberpunk colormap with a colorbar.

        Args:
            matrix: 2-D data to display as an image.
            ax: Existing axes to draw on, or ``None`` to create a styled figure.

        Returns:
            The axes the chart was drawn on.
        """
        cmap = LinearSegmentedColormap.from_list(
            "cyberpunk",
            [self.background, self.colors["neon_magenta"], self.colors["neon_cyan"]],
            N=256,
        )
        with self._target(ax, figsize=(10.0, 8.0)) as target:
            im = target.imshow(matrix, cmap=cmap, aspect="auto")
            target.figure.colorbar(im, ax=target)
            return target
