#!/usr/bin/env python3
"""Regenerate the committed gallery images.

Every figure here is built from deterministic synthetic data so the output is
reproducible: running ``python scripts/generate_gallery.py`` recreates the exact
PNGs tracked in ``images/``. The gallery is the project's selling point, so the
figures double as the canonical demonstration of each style.
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

from cinestyle import (  # noqa: E402
    BladeRunner,
    FilmNoir,
    Ghibli,
    StarWars,
    WesAnderson,
)

SEED = 7
_IMAGES_DIR = Path(__file__).resolve().parent.parent / "images"


def _hero() -> Figure:
    """Before/after hero: the same series in matplotlib default vs cinestyle."""
    rng = np.random.default_rng(SEED)
    months = np.arange(24)
    revenue = np.cumsum(rng.normal(1.0, 1.4, months.size)) + 12
    forecast = revenue + rng.normal(0.0, 0.8, months.size) + 1.5

    fig = plt.figure(figsize=(13.0, 5.4), facecolor="#0f0f12")
    fig.suptitle(
        "Same data, cinematic finish", color="white", fontsize=16, fontweight="bold"
    )

    before = fig.add_subplot(1, 2, 1)
    before.set_facecolor("white")
    before.plot(months, revenue, color="#1f77b4", linewidth=2)
    before.fill_between(months, revenue, color="#1f77b4", alpha=0.15)
    before.set_title("Before — matplotlib default", color="#c9c9d1")
    before.tick_params(colors="#c9c9d1")
    for spine in before.spines.values():
        spine.set_color("#777")

    blade = BladeRunner()
    after = fig.add_subplot(1, 2, 2)
    blade.style_axes(after)
    after.plot(
        months, revenue, color=blade.colors["neon_cyan"], linewidth=2.5, label="Revenue"
    )
    after.fill_between(months, revenue, color=blade.colors["neon_cyan"], alpha=0.12)
    after.plot(
        months,
        forecast,
        color=blade.colors["neon_magenta"],
        linewidth=2.5,
        label="Forecast",
    )
    after.set_title("After — cinestyle Blade Runner", color=blade.colors["neon_cyan"])
    after.legend(
        facecolor=blade.background, edgecolor=blade.foreground, labelcolor="white"
    )
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    return fig


def _noir() -> Figure:
    """Film Noir signature: light vs shadow diverging bars."""
    style = FilmNoir()
    scenes = ["Opening", "The Meeting", "Betrayal", "Pursuit", "Confession", "Finale"]
    rng = np.random.default_rng(SEED)
    light = rng.uniform(3, 9, len(scenes))
    shadow = rng.uniform(3, 9, len(scenes))
    with style.use():
        fig, ax = plt.subplots(figsize=(9.0, 5.6))
        style.plot_shadows(scenes, light, shadow, ax=ax)
        ax.set_title("FILM NOIR — Light & Shadow", fontsize=15, fontweight="bold")
        ax.set_xlabel("Tonal weight per scene")
        fig.tight_layout()
    return fig


def _ghibli() -> Figure:
    """Studio Ghibli signature: layered, pastoral landscape."""
    style = Ghibli()
    rng = np.random.default_rng(SEED)
    ridge = np.cumsum(rng.normal(0, 1, 120))
    ridge = ridge - ridge.min() + 4
    with style.use():
        fig, ax = plt.subplots(figsize=(9.0, 5.6))
        style.plot_landscape(ridge, ax=ax)
        ax.set_title("Studio Ghibli — A Quiet Valley", fontsize=15)
        ax.set_xlabel("Distance")
        ax.set_ylabel("Elevation")
        fig.tight_layout()
    return fig


def _wes_anderson() -> Figure:
    """Wes Anderson signature: symmetrical pastel comparison."""
    style = WesAnderson()
    rooms = ["Lobby", "Suite 401", "The Bath", "Kitchen", "Gardens", "Cellar"]
    rng = np.random.default_rng(SEED)
    left = rng.uniform(4, 10, len(rooms))
    right = rng.uniform(4, 10, len(rooms))
    with style.use():
        fig, ax = plt.subplots(figsize=(9.5, 5.6))
        style.plot_symmetry(left, right, labels=rooms, ax=ax)
        ax.set_title("The Grand Budapest — Symmetry", fontsize=15)
        ax.set_xlabel("Guests (left)        Staff (right)")
        fig.tight_layout()
    return fig


def _blade_runner() -> Figure:
    """Blade Runner signature: layered neon signals."""
    style = BladeRunner()
    t = np.linspace(0, 12, 240)
    signals = [
        np.sin(t) * np.exp(-0.04 * t) + 1.2,
        np.cos(0.8 * t) * 0.7,
        np.sin(1.6 * t + 1) * 0.5 - 1.0,
    ]
    with style.use():
        fig, ax = plt.subplots(figsize=(9.5, 5.6))
        style.plot_neon_lines(
            *signals, labels=["Sector A", "Sector B", "Sector C"], ax=ax
        )
        ax.set_title("BLADE RUNNER — City Signals", fontsize=15, fontweight="bold")
        ax.set_xlabel("Cycle")
        fig.tight_layout()
    return fig


def _star_wars() -> Figure:
    """Star Wars signature: bold, value-labelled faction bars."""
    style = StarWars()
    factions = ["Jedi", "Sith", "Rebels", "Empire", "Bounty Hunters"]
    rng = np.random.default_rng(SEED)
    strength = rng.uniform(45, 95, len(factions))
    with style.use():
        fig, ax = plt.subplots(figsize=(9.5, 5.8))
        style.plot_galaxy(factions, strength, ax=ax)
        ax.set_title("A GALAXY OF POWER", fontsize=16, fontweight="bold")
        ax.set_ylabel("Influence")
        fig.tight_layout()
    return fig


FIGURES: dict[str, Callable[[], Figure]] = {
    "hero_before_after": _hero,
    "noir": _noir,
    "ghibli": _ghibli,
    "wes_anderson": _wes_anderson,
    "blade_runner": _blade_runner,
    "star_wars": _star_wars,
}


def render(name: str, outdir: Path, dpi: int = 150) -> Path:
    """Build a single named figure and save it to *outdir*; return its path."""
    fig = FIGURES[name]()
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


def render_all(outdir: Path = _IMAGES_DIR, dpi: int = 150) -> list[Path]:
    """Render every gallery figure into *outdir* and return the written paths."""
    return [render(name, outdir, dpi=dpi) for name in FIGURES]


def main() -> None:
    parser = argparse.ArgumentParser(description="Regenerate the cinestyle gallery.")
    parser.add_argument(
        "-o", "--outdir", type=Path, default=_IMAGES_DIR, help="Output directory."
    )
    parser.add_argument("--dpi", type=int, default=150, help="Output resolution.")
    args = parser.parse_args()
    paths = render_all(args.outdir, dpi=args.dpi)
    for path in paths:
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
