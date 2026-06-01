"""Star Wars: bold gold and blue on the black of deep space."""

from __future__ import annotations

import numpy as np
from matplotlib.axes import Axes
from numpy.typing import ArrayLike

from .base import CinematicStyle


class StarWars(CinematicStyle):
    """Epic, high-impact styling for rankings and headline metrics."""

    name = "star_wars"
    base_style = "dark_background"
    background = "#000000"
    surface = "#121212"
    foreground = "#FFD700"
    edge_color = "#FFD700"
    font_weight = "bold"
    cmap = "cividis"
    palette = ("#FFD700", "#1E90FF", "#8B0000", "#FF4500", "#C0C0C0", "#1E3A5F")
    colors = {
        "light_side": "#1E90FF",
        "dark_side": "#8B0000",
        "neutral": "#FFD700",
        "empire": "#696969",
        "rebellion": "#FF4500",
        "background": "#000000",
        "primary": "#FFD700",
    }

    def plot_balance(
        self,
        categories: list[str],
        light_values: ArrayLike,
        dark_values: ArrayLike,
        ax: Axes | None = None,
    ) -> Axes:
        """Mirror light-side and dark-side magnitudes around a central axis.

        Args:
            categories: Row labels.
            light_values: Light-side magnitudes, drawn to the right.
            dark_values: Dark-side magnitudes, drawn to the left.
            ax: Existing axes to draw on, or ``None`` to create a styled figure.

        Returns:
            The axes the chart was drawn on.
        """
        light = np.asarray(light_values, dtype=float)
        dark = np.asarray(dark_values, dtype=float)
        with self._target(ax, figsize=(12.0, 7.0)) as target:
            y = np.arange(len(categories))
            target.barh(
                y, light, color=self.colors["light_side"], alpha=0.9, label="Light Side"
            )
            target.barh(
                y, -dark, color=self.colors["dark_side"], alpha=0.9, label="Dark Side"
            )
            target.set_yticks(y)
            target.set_yticklabels(categories)
            target.axvline(0, color=self.colors["neutral"], linewidth=3)
            target.legend(facecolor=self.background, edgecolor=self.foreground)
            return target

    def plot_galaxy(
        self, factions: list[str], values: ArrayLike, ax: Axes | None = None
    ) -> Axes:
        """Draw a bold bar per faction, each labelled with its value.

        Args:
            factions: Faction names along the x-axis.
            values: Magnitude per faction.
            ax: Existing axes to draw on, or ``None`` to create a styled figure.

        Returns:
            The axes the chart was drawn on.
        """
        heights = np.asarray(values, dtype=float)
        faction_colors = [
            self.colors["light_side"],
            self.colors["dark_side"],
            self.colors["rebellion"],
            self.colors["empire"],
            self.colors["neutral"],
        ]
        with self._target(ax, figsize=(12.0, 7.0)) as target:
            x = np.arange(len(factions))
            bars = target.bar(
                x,
                heights,
                color=[
                    faction_colors[i % len(faction_colors)]
                    for i in range(len(factions))
                ],
                edgecolor=self.colors["neutral"],
                linewidth=2,
                alpha=0.85,
            )
            target.set_xticks(x)
            target.set_xticklabels(factions, rotation=45, ha="right")
            for bar, value in zip(bars, heights, strict=True):
                target.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height(),
                    f"{value:.1f}",
                    ha="center",
                    va="bottom",
                    color=self.colors["neutral"],
                    fontweight="bold",
                )
            return target
