#!/usr/bin/env python3
"""A tour of cinestyle in one runnable file.

Run headless with ``python examples/quickstart.py``; it writes a few PNGs to the
current directory demonstrating each capability.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

import cinestyle as cs  # noqa: E402


def scoped_theme() -> None:
    """Apply a theme to a single figure with a scoped context manager."""
    x = np.linspace(0, 12, 200)
    with cs.use("blade_runner"):
        fig, ax = plt.subplots(figsize=(9, 5))
        for i in range(4):
            ax.plot(x, np.sin(x + i * 0.6) + i * 0.4)
        cs.add_glow(ax)  # the neon glow that makes this theme sing
        ax.set_title("CITY SIGNALS")
        fig.savefig(
            "quickstart_theme.png",
            dpi=130,
            bbox_inches="tight",
            facecolor=fig.get_facecolor(),
        )
    plt.close(fig)


def registered_style_sheet() -> None:
    """Register the themes and use one like any matplotlib style."""
    cs.register()
    with plt.style.context("cinestyle-dune"):
        fig, ax = plt.subplots(figsize=(9, 5))
        ax.imshow(np.add.outer(np.linspace(0, 1, 60), np.linspace(0, 1, 60)))
        ax.set_title("plt.style.use('cinestyle-dune')")
        fig.savefig(
            "quickstart_stylesheet.png",
            dpi=130,
            bbox_inches="tight",
            facecolor=fig.get_facecolor(),
        )
    plt.close(fig)


def accessibility() -> None:
    """Check a theme palette and build a colorblind-safe variant."""
    theme = cs.get_theme("blade_runner")
    print(cs.check_accessibility(theme.palette, background=theme.background).summary())
    safe = theme.accessible()
    print("accessible variant:", safe.palette)


def film_look() -> None:
    """Apply a film-look grade to an image plot and export it as a .cube LUT."""
    look = cs.get_look("teal_orange")
    fig, ax = plt.subplots(figsize=(7, 5))
    im = ax.imshow(np.random.default_rng(0).random((80, 80)), cmap="gray")
    look.apply_to_image(im)
    ax.set_title("teal_orange film look")
    fig.savefig("quickstart_look.png", dpi=130, bbox_inches="tight")
    plt.close(fig)
    look.to_cube("teal_orange.cube")


def custom_brand() -> None:
    """Define your own reusable brand."""
    brand = cs.define_brand(
        "acme",
        palette=["#0B5FFF", "#FF6B00", "#00B5AD"],
        background="#FBFBFD",
        foreground="#1A1A2E",
    )
    brand.register()  # plt.style.use("cinestyle-acme")
    brand.to_matplotlibrc("acme.mplstyle")  # reuse anywhere matplotlib reads styles


if __name__ == "__main__":
    scoped_theme()
    registered_style_sheet()
    accessibility()
    film_look()
    custom_brand()
    print("wrote quickstart_theme.png, quickstart_stylesheet.png, quickstart_look.png")
