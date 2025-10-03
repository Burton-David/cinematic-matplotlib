import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np


class CinematicStyle:
    def __init__(self, data=None):
        self.data = data
        self._original_rcparams = {}

    def apply_style(self):
        raise NotImplementedError

    def save_defaults(self):
        self._original_rcparams = {
            'figure.facecolor': mpl.rcParams['figure.facecolor'],
            'axes.facecolor': mpl.rcParams['axes.facecolor'],
            'axes.edgecolor': mpl.rcParams['axes.edgecolor'],
            'text.color': mpl.rcParams['text.color'],
            'axes.labelcolor': mpl.rcParams['axes.labelcolor'],
            'xtick.color': mpl.rcParams['xtick.color'],
            'ytick.color': mpl.rcParams['ytick.color'],
            'font.family': mpl.rcParams['font.family'],
        }

    def restore_defaults(self):
        if self._original_rcparams:
            mpl.rcParams.update(self._original_rcparams)

    def style_axes(self, ax):
        raise NotImplementedError

    @property
    def colors(self):
        raise NotImplementedError

    def plot_line(self, x, y, ax=None, **kwargs):
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 6))
        self.apply_style()
        self.style_axes(ax)

        color = kwargs.pop('color', self.colors.get('primary'))
        ax.plot(x, y, color=color, linewidth=2, **kwargs)
        return ax

    def plot_bar(self, categories, values, ax=None, **kwargs):
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 6))
        self.apply_style()
        self.style_axes(ax)

        color = kwargs.pop('color', self.colors.get('primary'))
        ax.bar(categories, values, color=color, **kwargs)
        return ax

    def plot_scatter(self, x, y, ax=None, **kwargs):
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 6))
        self.apply_style()
        self.style_axes(ax)

        color = kwargs.pop('color', self.colors.get('primary'))
        ax.scatter(x, y, color=color, alpha=0.6, **kwargs)
        return ax

    def plot_histogram(self, data, bins=30, ax=None, **kwargs):
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 6))
        self.apply_style()
        self.style_axes(ax)

        color = kwargs.pop('color', self.colors.get('primary'))
        ax.hist(data, bins=bins, color=color, alpha=0.7, **kwargs)
        return ax

    def plot_heatmap(self, data, ax=None, **kwargs):
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 8))
        self.apply_style()
        self.style_axes(ax)

        cmap = kwargs.pop('cmap', 'viridis')
        im = ax.imshow(data, aspect='auto', cmap=cmap, **kwargs)
        plt.colorbar(im, ax=ax)
        return ax

    def plot_area(self, x, y, ax=None, **kwargs):
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 6))
        self.apply_style()
        self.style_axes(ax)

        color = kwargs.pop('color', self.colors.get('primary'))
        ax.fill_between(x, y, color=color, alpha=0.5, **kwargs)
        ax.plot(x, y, color=color, linewidth=2)
        return ax
