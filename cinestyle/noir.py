import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from .base import CinematicStyle


class FilmNoir(CinematicStyle):
    def apply_style(self):
        self.save_defaults()
        plt.style.use('dark_background')
        mpl.rcParams['figure.facecolor'] = '#0a0a0a'
        mpl.rcParams['axes.facecolor'] = '#121212'
        mpl.rcParams['axes.edgecolor'] = 'white'
        mpl.rcParams['text.color'] = 'white'
        mpl.rcParams['axes.labelcolor'] = 'white'
        mpl.rcParams['xtick.color'] = 'white'
        mpl.rcParams['ytick.color'] = 'white'

    def style_axes(self, ax):
        ax.set_facecolor('#121212')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('white')
        ax.spines['bottom'].set_color('white')
        ax.tick_params(colors='white')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')

    @property
    def colors(self):
        return {
            'primary': '#8B0000',
            'secondary': '#FFFFFF',
            'accent': '#696969',
            'background': '#121212'
        }

    def plot_shadows(self, categories, light_values, dark_values, ax=None):
        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 6))
        self.apply_style()
        self.style_axes(ax)

        x = range(len(categories))
        ax.barh(x, light_values, color='#FFFFFF', alpha=0.8, label='Light')
        ax.barh(x, [-v for v in dark_values], color='#8B0000', alpha=0.8, label='Shadows')
        ax.set_yticks(x)
        ax.set_yticklabels(categories)
        ax.axvline(0, color='white', linewidth=2, linestyle='--')
        ax.legend()
        return ax

    def plot_contrast(self, data1, data2, ax=None):
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 6))
        self.apply_style()
        self.style_axes(ax)

        ax.plot(data1, color='#FFFFFF', linewidth=3, label='Light', alpha=0.9)
        ax.plot(data2, color='#8B0000', linewidth=3, label='Dark', alpha=0.9)
        ax.fill_between(range(len(data1)), data1, data2,
                        where=(np.array(data1) >= np.array(data2)),
                        color='#FFFFFF', alpha=0.2)
        ax.fill_between(range(len(data1)), data1, data2,
                        where=(np.array(data1) < np.array(data2)),
                        color='#8B0000', alpha=0.2)
        ax.legend()
        return ax
