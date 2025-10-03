import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from .base import CinematicStyle


class Ghibli(CinematicStyle):
    def apply_style(self):
        self.save_defaults()
        plt.style.use('seaborn-v0_8-whitegrid')
        mpl.rcParams['font.family'] = 'serif'
        mpl.rcParams['figure.facecolor'] = '#fdfdf8'
        mpl.rcParams['axes.facecolor'] = '#fdfdf8'
        mpl.rcParams['axes.edgecolor'] = '#c7c7ba'
        mpl.rcParams['grid.color'] = '#e8e8e0'

    def style_axes(self, ax):
        ax.set_facecolor('#fdfdf8')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#c7c7ba')
        ax.spines['bottom'].set_color('#c7c7ba')
        ax.grid(True, alpha=0.3, color='#e8e8e0')

    @property
    def colors(self):
        return {
            'primary': '#90EE90',
            'secondary': '#87CEEB',
            'accent': '#FFB6C1',
            'earth': '#D2B48C',
            'forest': '#6B8E23'
        }

    def plot_landscape(self, data, ax=None):
        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 6))
        self.apply_style()
        self.style_axes(ax)

        x = np.arange(len(data))
        ax.fill_between(x, data, color=self.colors['forest'], alpha=0.3, label='Forest')
        ax.fill_between(x, data * 0.6, color=self.colors['earth'], alpha=0.4, label='Earth')
        ax.plot(x, data, color=self.colors['forest'], linewidth=2)
        ax.legend()
        return ax

    def plot_flow(self, time_series, ax=None):
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 6))
        self.apply_style()
        self.style_axes(ax)

        x = np.arange(len(time_series))
        ax.plot(x, time_series, color=self.colors['primary'], linewidth=3, alpha=0.8)
        ax.fill_between(x, time_series, color=self.colors['primary'], alpha=0.2)

        smoothed = np.convolve(time_series, np.ones(5)/5, mode='same')
        ax.plot(x, smoothed, color=self.colors['secondary'], linewidth=2, linestyle='--', alpha=0.6)
        return ax
