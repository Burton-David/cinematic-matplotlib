import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from .base import CinematicStyle


class WesAnderson(CinematicStyle):
    def apply_style(self):
        self.save_defaults()
        mpl.rcParams['figure.facecolor'] = '#F5F5DC'
        mpl.rcParams['axes.facecolor'] = '#F5F5DC'
        mpl.rcParams['font.family'] = 'serif'
        mpl.rcParams['axes.edgecolor'] = '#8B7355'
        mpl.rcParams['grid.color'] = '#D3D3D3'

    def style_axes(self, ax):
        ax.set_facecolor('#F5F5DC')
        ax.spines['top'].set_color('#8B7355')
        ax.spines['right'].set_color('#8B7355')
        ax.spines['left'].set_color('#8B7355')
        ax.spines['bottom'].set_color('#8B7355')
        ax.spines['top'].set_linewidth(1.5)
        ax.spines['right'].set_linewidth(1.5)
        ax.spines['left'].set_linewidth(1.5)
        ax.spines['bottom'].set_linewidth(1.5)

    @property
    def colors(self):
        return {
            'primary': '#FFCBA4',
            'secondary': '#87CEEB',
            'accent': '#FFB6C1',
            'earth': '#C1FFC1',
            'sunset': '#F4A460'
        }

    @property
    def palette(self):
        return ['#FFCBA4', '#87CEEB', '#FFB6C1', '#C1FFC1', '#F4A460',
                '#DDA0DD', '#98FB98', '#FFE4B5']

    def plot_symmetry(self, left_data, right_data, labels=None, ax=None):
        if ax is None:
            fig, ax = plt.subplots(figsize=(14, 6))
        self.apply_style()
        self.style_axes(ax)

        if labels is None:
            labels = [f'Item {i+1}' for i in range(len(left_data))]

        y_pos = np.arange(len(labels))
        ax.barh(y_pos, left_data, color=self.palette[0], alpha=0.8, label='Left')
        ax.barh(y_pos, [-x for x in right_data], color=self.palette[1], alpha=0.8, label='Right')
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels)
        ax.axvline(0, color='#8B7355', linewidth=2)
        ax.legend()
        return ax

    def plot_grid(self, data_matrix, ax=None):
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 10))
        self.apply_style()

        n_items = len(data_matrix)
        grid_size = int(np.ceil(np.sqrt(n_items)))

        for i, value in enumerate(data_matrix):
            row = i // grid_size
            col = i % grid_size
            color = self.palette[i % len(self.palette)]
            rect = plt.Rectangle((col, grid_size - row - 1), 1, 1,
                                facecolor=color, edgecolor='#8B7355', linewidth=2)
            ax.add_patch(rect)

        ax.set_xlim(0, grid_size)
        ax.set_ylim(0, grid_size)
        ax.set_aspect('equal')
        ax.axis('off')
        return ax
