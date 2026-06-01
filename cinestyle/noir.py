"""Film Noir: high-contrast reds and whites on near-black backgrounds."""

from __future__ import annotations

import numpy as np
from matplotlib.axes import Axes
from numpy.typing import ArrayLike

from .base import CinematicStyle


class FilmNoir(CinematicStyle):
    """Dramatic, high-contrast styling for stark splits and binary comparisons."""

    name = "noir"
    base_style = "dark_background"
    background = "#0a0a0a"
    surface = "#121212"
    foreground = "#ffffff"
    cmap = "bone"
    palette = ("#8B0000", "#FFFFFF", "#B22222", "#A9A9A9", "#696969", "#FF6347")
    colors = {
        "primary": "#8B0000",
        "secondary": "#FFFFFF",
        "accent": "#696969",
        "background": "#121212",
    }

    def plot_shadows(
        self,
        categories: list[str],
        light_values: ArrayLike,
        dark_values: ArrayLike,
        ax: Axes | None = None,
    ) -> Axes:
        """Mirror "light" and "shadow" magnitudes around a central axis.

        Args:
            categories: Row labels.
            light_values: Positive ("light") magnitudes, drawn to the right.
            dark_values: "Shadow" magnitudes, drawn to the left.
            ax: Existing axes to draw on, or ``None`` to create a styled figure.

        Returns:
            The axes the chart was drawn on.
        """
        light = np.asarray(light_values, dtype=float)
        dark = np.asarray(dark_values, dtype=float)
        with self._target(ax, figsize=(12.0, 6.0)) as target:
            y = np.arange(len(categories))
            target.barh(
                y, light, color=self.colors["secondary"], alpha=0.85, label="Light"
            )
            target.barh(
                y, -dark, color=self.colors["primary"], alpha=0.85, label="Shadows"
            )
            target.set_yticks(y)
            target.set_yticklabels(categories)
            target.axvline(0, color=self.foreground, linewidth=2, linestyle="--")
            target.legend()
            return target

    def plot_contrast(
        self, light: ArrayLike, dark: ArrayLike, ax: Axes | None = None
    ) -> Axes:
        """Plot two series and shade the gap between them by which leads.

        Args:
            light: First ("light") series.
            dark: Second ("dark") series.
            ax: Existing axes to draw on, or ``None`` to create a styled figure.

        Returns:
            The axes the chart was drawn on.
        """
        light_arr = np.asarray(light, dtype=float)
        dark_arr = np.asarray(dark, dtype=float)
        x = np.arange(len(light_arr))
        light_leads = (light_arr >= dark_arr).tolist()
        dark_leads = (light_arr < dark_arr).tolist()
        with self._target(ax) as target:
            target.plot(
                x, light_arr, color=self.colors["secondary"], linewidth=3, label="Light"
            )
            target.plot(
                x, dark_arr, color=self.colors["primary"], linewidth=3, label="Dark"
            )
            target.fill_between(
                x,
                light_arr,
                dark_arr,
                where=light_leads,
                color=self.colors["secondary"],
                alpha=0.2,
            )
            target.fill_between(
                x,
                light_arr,
                dark_arr,
                where=dark_leads,
                color=self.colors["primary"],
                alpha=0.2,
            )
            target.legend()
            return target
