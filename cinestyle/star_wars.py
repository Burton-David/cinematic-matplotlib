import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from .base import CinematicStyle


class StarWars(CinematicStyle):
    def apply_style(self):
        self.save_defaults()
        plt.style.use('dark_background')
        mpl.rcParams['figure.facecolor'] = 'black'
        mpl.rcParams['axes.facecolor'] = '#121212'
        mpl.rcParams['axes.edgecolor'] = '#FFD700'
        mpl.rcParams['text.color'] = '#FFD700'
        mpl.rcParams['axes.labelcolor'] = '#FFD700'
        mpl.rcParams['xtick.color'] = '#FFD700'
        mpl.rcParams['ytick.color'] = '#FFD700'
        mpl.rcParams['font.weight'] = 'bold'

    def style_axes(self, ax):
        ax.set_facecolor('#121212')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#FFD700')
        ax.spines['bottom'].set_color('#FFD700')
        ax.tick_params(colors='#FFD700')
        ax.xaxis.label.set_color('#FFD700')
        ax.yaxis.label.set_color('#FFD700')

    @property
    def colors(self):
        return {
            'light_side': '#1E90FF',
            'dark_side': '#8B0000',
            'neutral': '#FFD700',
            'empire': '#696969',
            'rebellion': '#FF4500',
            'background': 'black',
            'primary': '#FFD700'
        }

    def plot_balance(self, categories, light_values, dark_values, ax=None):
        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 7))
        self.apply_style()
        self.style_axes(ax)

        x = range(len(categories))
        ax.barh(x, light_values, color=self.colors['light_side'], alpha=0.9, label='Light Side')
        ax.barh(x, [-v for v in dark_values], color=self.colors['dark_side'], alpha=0.9, label='Dark Side')
        ax.set_yticks(x)
        ax.set_yticklabels(categories)
        ax.axvline(0, color='#FFD700', linewidth=3, linestyle='-')
        ax.legend(facecolor='black', edgecolor='#FFD700')
        return ax

    def plot_galaxy(self, factions, values, ax=None):
        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 7))
        self.apply_style()
        self.style_axes(ax)

        faction_colors = [self.colors['light_side'], self.colors['dark_side'],
                         self.colors['rebellion'], self.colors['empire'], self.colors['neutral']]

        bars = ax.bar(range(len(factions)), values,
                      color=[faction_colors[i % len(faction_colors)] for i in range(len(factions))],
                      edgecolor='#FFD700', linewidth=2, alpha=0.85)

        ax.set_xticks(range(len(factions)))
        ax.set_xticklabels(factions, rotation=45, ha='right')

        for i, (bar, value) in enumerate(zip(bars, values)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{value:.1f}', ha='center', va='bottom',
                   color='#FFD700', fontweight='bold')

        return ax
