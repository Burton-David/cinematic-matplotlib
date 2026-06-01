#!/usr/bin/env python3
"""Regenerate the committed gallery images.

Every figure is built from deterministic synthetic data so the output is
reproducible: running ``python scripts/generate_gallery.py`` recreates the exact
PNGs tracked in ``images/``. The gallery is the project's selling point, so the
figures double as the canonical demonstration of each theme.
"""

from __future__ import annotations

import argparse
from collections.abc import Callable
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402

import cinestyle as cs  # noqa: E402

SEED = 11
_IMAGES_DIR = Path(__file__).resolve().parent.parent / "images"


def _signals(n: int, length: int = 200) -> tuple[np.ndarray, list[np.ndarray]]:
    x = np.linspace(0, 12, length)
    rng = np.random.default_rng(SEED)
    series = [
        np.sin(x + i * 0.7) * (1.0 - 0.05 * i) + i * 0.45 + rng.normal(0, 0.03, length)
        for i in range(n)
    ]
    return x, series


def hero() -> Figure:
    """Before/after hero: the same data in matplotlib default vs cinestyle."""
    x, series = _signals(4)
    fig = plt.figure(figsize=(13.0, 5.2), facecolor="#0E0F13")
    fig.suptitle(
        "Same data, cinematic finish", color="white", fontsize=16, fontweight="bold"
    )

    before = fig.add_subplot(1, 2, 1)
    before.set_facecolor("white")
    for s in series:
        before.plot(x, s, linewidth=2)
    before.set_title("Before: matplotlib default", color="#C9C9D1")
    before.tick_params(colors="#C9C9D1")
    for spine in before.spines.values():
        spine.set_color("#777")

    theme = cs.get_theme("blade_runner")
    with theme.use():
        after = fig.add_subplot(1, 2, 2)
        for s in series:
            after.plot(x, s, linewidth=2.5)
        cs.add_glow(after, intensity=theme.glow)
        after.set_title("After: cinestyle blade_runner", color=theme.foreground)
        after.set_facecolor(theme.surface)
        for spine in after.spines.values():
            spine.set_color(theme.foreground)
        after.tick_params(colors=theme.foreground)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    return fig


def theme_card(name: str) -> Figure:
    """One theme's card: its color cycle next to its sequential colormap."""
    theme = cs.get_theme(name)
    x, series = _signals(len(theme.palette))
    with theme.use():
        fig, (lines_ax, cmap_ax) = plt.subplots(
            1, 2, figsize=(10.0, 3.6), gridspec_kw={"width_ratios": [2.3, 1.0]}
        )
        for s in series:
            lines_ax.plot(x, s, linewidth=2.2)
        if theme.glow:
            cs.add_glow(lines_ax, intensity=theme.glow)
        lines_ax.set_title(name, fontsize=15, fontweight=theme.title_weight)
        lines_ax.set_xlabel("time")
        lines_ax.set_ylabel("signal")
        gradient = np.tile(np.linspace(0, 1, 160), (28, 1))
        cmap_ax.imshow(gradient, cmap=theme.sequential, aspect="auto")
        cmap_ax.set_title("sequential", fontsize=11)
        cmap_ax.set_xticks([])
        cmap_ax.set_yticks([])
        fig.tight_layout()
    return fig


def accessibility_demo() -> Figure:
    """Show a theme palette beside its colorblind-safe variant."""
    theme = cs.get_theme("blade_runner")
    safe = theme.accessible()
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 3.2), facecolor="#0A0C12")
    for ax, palette, title in (
        (axes[0], theme.palette, "blade_runner"),
        (axes[1], safe.palette, "accessible() variant"),
    ):
        for i, hex_color in enumerate(palette):
            ax.add_patch(plt.Rectangle((i, 0), 1, 1, facecolor=hex_color))
        ax.set_xlim(0, len(palette))
        ax.set_ylim(0, 1)
        ax.set_title(title, color="white", fontsize=13)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_facecolor("#0A0C12")
    fig.tight_layout()
    return fig


def _builders() -> dict[str, Callable[[], Figure]]:
    builders: dict[str, Callable[[], Figure]] = {
        "hero_before_after": hero,
        "accessibility": accessibility_demo,
    }
    for name in cs.list_themes():
        builders[name] = lambda name=name: theme_card(name)
    return builders


def render(name: str, outdir: Path, dpi: int = 130) -> Path:
    """Build a single named figure and save it to *outdir*; return its path."""
    fig = _builders()[name]()
    outdir.mkdir(parents=True, exist_ok=True)
    path = outdir / f"{name}.png"
    fig.savefig(
        path,
        dpi=dpi,
        bbox_inches="tight",
        facecolor=fig.get_facecolor(),
        metadata={"Software": "cinestyle"},
    )
    plt.close(fig)
    return path


def render_all(outdir: Path = _IMAGES_DIR, dpi: int = 130) -> list[Path]:
    """Render every gallery figure into *outdir* and return the written paths."""
    return [render(name, outdir, dpi=dpi) for name in _builders()]


def main() -> None:
    parser = argparse.ArgumentParser(description="Regenerate the cinestyle gallery.")
    parser.add_argument("-o", "--outdir", type=Path, default=_IMAGES_DIR)
    parser.add_argument("--dpi", type=int, default=130)
    args = parser.parse_args()
    for path in render_all(args.outdir, dpi=args.dpi):
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
