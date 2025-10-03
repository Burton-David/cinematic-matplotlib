import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from .base import CinematicStyle


class BladeRunner(CinematicStyle):
    def apply_style(self):
        self.save_defaults()
        plt.style.use('dark_background')
        mpl.rcParams['figure.facecolor'] = '#0a0a0a'
        mpl.rcParams['axes.facecolor'] = '#0a0a0a'
        mpl.rcParams['axes.edgecolor'] = '#00FFFF'
        mpl.rcParams['text.color'] = '#00FFFF'
        mpl.rcParams['axes.labelcolor'] = '#00FFFF'
        mpl.rcParams['xtick.color'] = '#00FFFF'
        mpl.rcParams['ytick.color'] = '#00FFFF'
        mpl.rcParams['grid.color'] = '#FF00FF'
        mpl.rcParams['grid.alpha'] = 0.3

    def style_axes(self, ax):
        ax.set_facecolor('#0a0a0a')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#00FFFF')
        ax.spines['bottom'].set_color('#00FFFF')
        ax.tick_params(colors='#00FFFF')
        ax.xaxis.label.set_color('#00FFFF')
        ax.yaxis.label.set_color('#00FFFF')
        ax.grid(True, alpha=0.2, color='#FF00FF')

    @property
    def colors(self):
        return {
            'neon_cyan': '#00FFFF',
            'neon_magenta': '#FF00FF',
            'neon_yellow': '#FFFF00',
            'electric_blue': '#0080FF',
            'hot_pink': '#FF1493',
            'background': '#0a0a0a',
            'primary': '#00FFFF'
        }

    def plot_neon_lines(self, *datasets, labels=None, ax=None):
        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 6))
        self.apply_style()
        self.style_axes(ax)

        neon_colors = ['#00FFFF', '#FF00FF', '#FFFF00', '#0080FF']
        for i, data in enumerate(datasets):
            color = neon_colors[i % len(neon_colors)]
            label = labels[i] if labels and i < len(labels) else f'Signal {i+1}'
            ax.plot(data, color=color, linewidth=2.5, alpha=0.9, label=label)

        ax.legend(facecolor='#0a0a0a', edgecolor='#00FFFF')
        return ax

    def plot_matrix(self, matrix_data, ax=None):
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 8))
        self.apply_style()
        self.style_axes(ax)

        from matplotlib.colors import LinearSegmentedColormap
        colors = ['#0a0a0a', '#FF00FF', '#00FFFF']
        n_bins = 100
        cmap = LinearSegmentedColormap.from_list('cyberpunk', colors, N=n_bins)

        im = ax.imshow(matrix_data, cmap=cmap, aspect='auto')
        plt.colorbar(im, ax=ax)
        return ax
