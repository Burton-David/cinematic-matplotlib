#!/usr/bin/env python3
"""The three ways to use cinestyle, in one runnable file.

Run headless with ``python examples/quickstart.py``; it writes three PNGs to the
current directory, one per usage mode.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

import cinestyle  # noqa: E402
from cinestyle import BladeRunner, define_brand  # noqa: E402


def scoped_context() -> None:
    """Mode 1: a scoped context manager that never leaks global rcParams."""
    x = np.linspace(0, 12, 200)
    with BladeRunner().use():
        fig, ax = plt.subplots(figsize=(9, 5))
        ax.plot(x, np.sin(x), linewidth=2.5)
        ax.plot(x, np.cos(x), linewidth=2.5)
        ax.set_title("Scoped with FilmNoir().use()")
        fig.savefig("quickstart_context.png", dpi=130, bbox_inches="tight")
    plt.close(fig)


def named_style_sheet() -> None:
    """Mode 2: register the styles and use them like any matplotlib style."""
    cinestyle.register()
    with plt.style.context("cinestyle-star_wars"):
        fig, ax = plt.subplots(figsize=(9, 5))
        ax.bar(["Light", "Dark"], [85, 92])
        ax.set_title("plt.style.use('cinestyle-star_wars')")
        fig.savefig("quickstart_stylesheet.png", dpi=130, bbox_inches="tight")
    plt.close(fig)


def custom_brand() -> None:
    """Mode 3: define your own reusable brand and export it for any project."""
    brand = define_brand(
        "acme",
        palette=["#0B5FFF", "#FF6B00", "#00B5AD"],
        background="#FBFBFD",
        foreground="#1A1A2E",
        grid_color="#E3E3EA",
    )
    brand.register()
    brand.to_matplotlibrc("acme.mplstyle")
    with brand.use():
        fig, ax = plt.subplots(figsize=(9, 5))
        for offset in range(3):
            ax.plot(np.linspace(0, 10, 100), np.sin(np.linspace(0, 10, 100)) + offset)
        ax.set_title("define_brand('acme', ...)")
        fig.savefig("quickstart_brand.png", dpi=130, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    scoped_context()
    named_style_sheet()
    custom_brand()
    print(
        "wrote quickstart_context.png, quickstart_stylesheet.png, quickstart_brand.png"
    )
