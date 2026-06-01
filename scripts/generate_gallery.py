#!/usr/bin/env python3
"""Regenerate the committed gallery: themed in-universe cards, the before/after
hero, an accessibility demo, and the film-reel GIF.

Each theme plots data drawn from its own film (Tears in Rain, the Bride's kill
count, the Balance of the Force) in a chart type that suits it, so the gallery
reads as a curated reel rather than the same sine wave restyled. Everything is
built from deterministic synthetic data, so the committed images regenerate
exactly. Pass --reel to also build images/cinestyle_reel.gif (slower).
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

import cinestyle as cs  # noqa: E402

SEED = 11
_ROOT = Path(__file__).resolve().parent.parent
_IMAGES_DIR = _ROOT / "images"
_FONT_DIR = _ROOT / "cinestyle" / "data" / "fonts"


# Each drawer fills one axes with that film's data. The theme is already active
# (so palette, font, background apply); drawers reach for explicit palette
# entries only where a specific color carries meaning (light vs dark side).
def _glow(ax: plt.Axes, theme: cs.Theme) -> None:
    if theme.glow:
        cs.add_glow(ax, intensity=theme.glow)


def _noir(ax: plt.Axes, t: cs.Theme, rng: np.random.Generator) -> None:
    x = np.arange(12)
    ax.fill_between(
        x,
        rng.uniform(3, 9, 12),
        step="mid",
        color=t.palette[0],
        alpha=0.85,
        label="testimony",
    )
    ax.fill_between(
        x,
        -rng.uniform(3, 9, 12),
        step="mid",
        color=t.palette[1],
        alpha=0.85,
        label="alibi",
    )
    ax.axhline(0, color=t.foreground, linewidth=1.5, linestyle="--")
    ax.set_title("SHADOWS OF SUSPICION")
    ax.set_xlabel("scene")
    ax.legend(loc="lower right")


def _ghibli(ax: plt.Axes, t: cs.Theme, rng: np.random.Generator) -> None:
    x = np.linspace(0, 120, 200)
    ridge = np.cumsum(rng.normal(0, 1, 200))
    ridge = ridge - ridge.min() + 4
    ax.fill_between(x, ridge, color=t.palette[1], alpha=0.35, label="forest")
    ax.fill_between(x, ridge * 0.55, color=t.palette[2], alpha=0.5, label="meadow")
    ax.plot(x, ridge, color=t.palette[1], linewidth=2)
    ax.set_title("The Quiet Valley")
    ax.set_xlabel("distance")
    ax.set_ylabel("elevation")
    ax.legend()


def _wes_anderson(ax: plt.Axes, t: cs.Theme, rng: np.random.Generator) -> None:
    floors = ["Lobby", "Second", "Third", "Suite 401", "The Spa", "Roof"]
    y = np.arange(len(floors))
    ax.barh(y, rng.uniform(4, 10, 6), color=t.palette[0], alpha=0.9, label="guests")
    ax.barh(y, -rng.uniform(2, 7, 6), color=t.palette[1], alpha=0.9, label="staff")
    ax.axvline(0, color=t.foreground, linewidth=1.5)
    ax.set_yticks(y, floors)
    ax.set_title("THE GRAND BUDAPEST: occupancy")
    ax.legend(loc="lower right")


def _blade_runner(ax: plt.Axes, t: cs.Theme, rng: np.random.Generator) -> None:
    x = np.linspace(0, 12, 240)
    for i, decay in enumerate((0.04, 0.09, 0.14)):
        ax.plot(
            x,
            np.sin(x * (1 + 0.3 * i)) * np.exp(-decay * x) + (2 - i),
            linewidth=2.5,
            color=t.palette[i],
            label=f"replicant {i + 1}",
        )
    ax.set_title("TEARS IN RAIN")
    ax.set_xlabel("time to deactivation")
    ax.legend()
    _glow(ax, t)


def _star_wars(ax: plt.Axes, t: cs.Theme, rng: np.random.Generator) -> None:
    eps = ["IV", "V", "VI", "I", "II", "III", "VII", "VIII", "IX"]
    x = np.arange(len(eps))
    ax.bar(x, rng.uniform(3, 9, 9), color=t.palette[1], label="light side")
    ax.bar(x, -rng.uniform(3, 9, 9), color=t.palette[2], label="dark side")
    ax.axhline(0, color=t.palette[0], linewidth=2)
    ax.set_xticks(x, eps)
    ax.set_title("BALANCE OF THE FORCE")
    ax.set_xlabel("episode")
    ax.legend()


def _matrix(ax: plt.Axes, t: cs.Theme, rng: np.random.Generator) -> None:
    x = np.arange(48)
    density = np.abs(np.sin(x / 5) * 6 + rng.uniform(0, 4, 48)) + 1
    ax.fill_between(x, density, color=t.palette[0], alpha=0.4)
    ax.plot(x, density, color=t.palette[0], linewidth=2)
    ax.set_title("DIGITAL RAIN")
    ax.set_xlabel("column")
    ax.set_ylabel("glyphs per second")
    _glow(ax, t)


def _dune(ax: plt.Axes, t: cs.Theme, rng: np.random.Generator) -> None:
    grid = np.add.outer(np.linspace(0, 1, 30), np.linspace(0, 1, 30))
    grid += rng.normal(0, 0.1, grid.shape)
    ax.imshow(grid, cmap=t.sequential, aspect="auto")
    ax.set_title("THE SPICE MUST FLOW")
    ax.set_xlabel("longitude")
    ax.set_ylabel("latitude")


def _fury_road(ax: plt.Axes, t: cs.Theme, rng: np.random.Generator) -> None:
    x = np.arange(20)
    ax.fill_between(
        x,
        np.clip(8 - x * 0.3 + rng.normal(0, 0.6, 20), 0, None),
        color=t.palette[0],
        alpha=0.6,
        label="fuel",
    )
    ax.fill_between(
        x,
        -np.clip(6 - x * 0.2 + rng.normal(0, 0.6, 20), 0, None),
        color=t.palette[2],
        alpha=0.6,
        label="water",
    )
    ax.axhline(0, color=t.foreground, linewidth=1.2)
    ax.set_title("WITNESS ME: reserves on the run")
    ax.set_xlabel("day on the Fury Road")
    ax.legend()


def _kill_bill(ax: plt.Axes, t: cs.Theme, rng: np.random.Generator) -> None:
    chapters = ["Origin", "Vernita", "O-Ren", "Crazy 88", "Budd", "Elle", "Bill"]
    kills = [1, 1, 1, 88, 1, 1, 1]
    ax.bar(
        range(len(chapters)),
        kills,
        color=t.palette[0],
        edgecolor=t.palette[1],
        linewidth=1.5,
    )
    ax.set_xticks(range(len(chapters)), chapters, rotation=30, ha="right")
    ax.set_title("ROARING RAMPAGE OF REVENGE")
    ax.set_ylabel("kill count")  # the Crazy 88 spike dwarfs the rest, as it should


def _in_the_mood(ax: plt.Axes, t: cs.Theme, rng: np.random.Generator) -> None:
    x = np.linspace(0, 24, 200)
    encounters = np.exp(-((x - 21) ** 2) / 6) + 0.3 * np.exp(-((x - 8) ** 2) / 4)
    ax.fill_between(x, encounters, color=t.palette[0], alpha=0.3)
    ax.plot(x, encounters, color=t.palette[0], linewidth=2.5)
    ax.set_title("ENCOUNTERS IN THE CORRIDOR")
    ax.set_xlabel("hour")
    ax.set_ylabel("chance meeting")


def _sin_city(ax: plt.Axes, t: cs.Theme, rng: np.random.Generator) -> None:
    districts = ["Old Town", "The Docks", "Sacred Oaks", "The Pits", "Basin City"]
    base = rng.uniform(3, 8, 5)
    colors = [t.palette[2], t.palette[2], t.palette[0], t.palette[2], t.palette[1]]
    ax.bar(range(5), base, color=colors)
    ax.set_xticks(range(5), districts, rotation=20, ha="right")
    ax.set_title("THE HARD GOODBYE: crime by district")
    ax.set_ylabel("incidents")


def _akira(ax: plt.Axes, t: cs.Theme, rng: np.random.Generator) -> None:
    x = np.linspace(0, 10, 200)
    for i in range(3):
        ax.plot(
            x,
            np.sin(x * (1.5 + i)) * (1.2 - 0.2 * i) + i,
            linewidth=2.5,
            color=t.palette[i],
            label=f"sector {i + 1}",
        )
    ax.set_title("NEO-TOKYO: power surges")
    ax.set_xlabel("seconds to detonation")
    ax.legend()
    _glow(ax, t)


def _the_fall(ax: plt.Axes, t: cs.Theme, rng: np.random.Generator) -> None:
    x = np.linspace(0, 10, 120)
    for i in range(4):
        ax.plot(
            x,
            np.cumsum(rng.normal(0.1 * (i - 1.5), 0.5, 120)),
            linewidth=2.5,
            color=t.palette[i],
            label=f"tale {i + 1}",
        )
    ax.set_title("THE FALL: a story in colors")
    ax.set_xlabel("chapter")
    ax.legend()


def _tron(ax: plt.Axes, t: cs.Theme, rng: np.random.Generator) -> None:
    x = np.arange(15)
    ax.plot(
        x,
        np.cumsum(rng.uniform(0, 3, 15)),
        linewidth=2.5,
        color=t.palette[0],
        marker="o",
        label="programs",
    )
    ax.plot(
        x,
        np.cumsum(rng.uniform(0, 2, 15)),
        linewidth=2.5,
        color=t.palette[1],
        marker="o",
        label="CLU's army",
    )
    ax.set_title("ON THE GRID: derezzed per cycle")
    ax.set_xlabel("cycle")
    ax.legend()
    _glow(ax, t)


def _amelie(ax: plt.Axes, t: cs.Theme, rng: np.random.Generator) -> None:
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    ax.bar(range(6), rng.integers(2, 9, 6), color=t.palette[0], alpha=0.9)
    ax.plot(
        range(6), rng.integers(2, 9, 6), color=t.palette[1], linewidth=2.5, marker="o"
    )
    ax.set_xticks(range(6), months)
    ax.set_title("LES BONNES ACTIONS")
    ax.set_ylabel("good deeds")


def _the_shining(ax: plt.Axes, t: cs.Theme, rng: np.random.Generator) -> None:
    x = np.arange(20)
    ax.plot(
        x,
        np.cumsum(np.abs(rng.normal(0.5, 0.6, 20))),
        linewidth=2.5,
        color=t.palette[0],
        label="wrong turns",
    )
    ax.plot(
        x,
        np.cumsum(np.abs(rng.normal(0.3, 0.4, 20))),
        linewidth=2.5,
        color=t.palette[3],
        label="sanity lost",
    )
    ax.set_title("THE OVERLOOK: a long winter")
    ax.set_xlabel("week")
    ax.legend(loc="upper left")


def _drive(ax: plt.Axes, t: cs.Theme, rng: np.random.Generator) -> None:
    x = np.linspace(0, 5, 200)
    ax.plot(
        x, 60 + 40 * np.sin(x * 2) * np.exp(-0.2 * x), linewidth=3, color=t.palette[0]
    )
    ax.set_title("A REAL HUMAN BEING: the getaway")
    ax.set_xlabel("minutes")
    ax.set_ylabel("mph")
    _glow(ax, t)


def _grand_budapest(ax: plt.Axes, t: cs.Theme, rng: np.random.Generator) -> None:
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    ax.bar(
        range(7),
        rng.integers(20, 90, 7),
        color=[t.palette[i % len(t.palette)] for i in range(7)],
    )
    ax.set_xticks(range(7), days)
    ax.set_title("MENDL'S: courtesan au chocolat, sold")
    ax.set_ylabel("boxes")


def _nolan(ax: plt.Axes, t: cs.Theme, rng: np.random.Generator) -> None:
    x = np.linspace(0, 10, 200)
    for i in range(4):
        ax.plot(
            x,
            np.sin(x / (1 + i)) + i * 0.6,
            linewidth=2,
            color=t.palette[i],
            label=f"level {i + 1}",
        )
    ax.set_title("TIME, RELATIVE: depth of the dream")
    ax.set_xlabel("surface time")
    ax.legend(loc="upper left")


def _hero(ax: plt.Axes, t: cs.Theme, rng: np.random.Generator) -> None:
    x = np.linspace(0, 10, 120)
    for i, label in enumerate(("as told", "as feared", "as it was")):
        ax.plot(
            x,
            np.cumsum(rng.normal(0.1, 0.5, 120)) + i,
            linewidth=2.5,
            color=t.palette[i],
            label=label,
        )
    ax.set_title("HERO: three tellings of one tale")
    ax.set_xlabel("the telling")
    ax.legend(loc="upper left")


def _suspiria(ax: plt.Axes, t: cs.Theme, rng: np.random.Generator) -> None:
    acts = ["Arrival", "The Rehearsal", "The Cellar", "The Sabbath"]
    ax.bar(
        range(4),
        [1, 2, 4, 9],
        color=[t.palette[i] for i in range(4)],
        edgecolor=t.foreground,
        linewidth=1.2,
    )
    ax.set_xticks(range(4), acts, rotation=15, ha="right")
    ax.set_title("SUSPIRIA: disappearances by act")
    ax.set_ylabel("vanished")
    _glow(ax, t)


def _moonlight(ax: plt.Axes, t: cs.Theme, rng: np.random.Generator) -> None:
    x = np.linspace(0, 10, 150)
    for i, label in enumerate(("Little", "Chiron", "Black")):
        ax.plot(
            x,
            np.sin(x + i * 1.5) * (1 - 0.1 * i) + i,
            linewidth=2.5,
            color=t.palette[i % len(t.palette)],
            label=label,
        )
    ax.set_title("MOONLIGHT: three chapters")
    ax.set_xlabel("a life, in blue")
    ax.legend(loc="upper left")


def _blade_runner_2049(ax: plt.Axes, t: cs.Theme, rng: np.random.Generator) -> None:
    x = np.arange(16)
    ax.bar(x, rng.uniform(2, 8, 16), color=t.palette[0], label="LA, cold")
    ax.bar(x, -rng.uniform(2, 8, 16), color=t.palette[1], label="Vegas, warm")
    ax.axhline(0, color=t.foreground, linewidth=1.2)
    ax.set_title("2049: cold city, warm ruin")
    ax.set_xlabel("sector")
    ax.legend()


def _her(ax: plt.Axes, t: cs.Theme, rng: np.random.Generator) -> None:
    x = np.arange(30)
    ax.fill_between(x, np.cumsum(rng.uniform(0, 5, 30)), color=t.palette[0], alpha=0.3)
    ax.plot(x, np.cumsum(rng.uniform(0, 5, 30)), color=t.palette[1], linewidth=2.5)
    ax.set_title("HER: conversations with Samantha")
    ax.set_xlabel("day")
    ax.set_ylabel("hours spent talking")


# marquee name (for the reel caption) and the drawer for each theme
THEMED: dict[str, tuple[str, object]] = {
    "noir": ("Film Noir", _noir),
    "ghibli": ("Studio Ghibli", _ghibli),
    "wes_anderson": ("Wes Anderson", _wes_anderson),
    "blade_runner": ("Blade Runner", _blade_runner),
    "star_wars": ("Star Wars", _star_wars),
    "matrix": ("The Matrix", _matrix),
    "dune": ("Dune", _dune),
    "fury_road": ("Mad Max: Fury Road", _fury_road),
    "kill_bill": ("Kill Bill", _kill_bill),
    "in_the_mood": ("In the Mood for Love", _in_the_mood),
    "sin_city": ("Sin City", _sin_city),
    "akira": ("Akira", _akira),
    "the_fall": ("The Fall", _the_fall),
    "tron": ("Tron: Legacy", _tron),
    "amelie": ("Amelie", _amelie),
    "the_shining": ("The Shining", _the_shining),
    "drive": ("Drive", _drive),
    "grand_budapest": ("The Grand Budapest Hotel", _grand_budapest),
    "nolan": ("Christopher Nolan", _nolan),
    "hero": ("Hero", _hero),
    "suspiria": ("Suspiria", _suspiria),
    "moonlight": ("Moonlight", _moonlight),
    "blade_runner_2049": ("Blade Runner 2049", _blade_runner_2049),
    "her": ("Her", _her),
}


def card(name: str) -> Figure:
    """Render one theme's in-universe chart as a card figure."""
    _marquee, drawer = THEMED[name]
    rng = np.random.default_rng(SEED)
    with cs.use(name):
        fig, ax = plt.subplots(figsize=(8.0, 5.0))
        drawer(ax, cs.get_theme(name), rng)
        fig.tight_layout()
    return fig


def hero() -> Figure:
    """Before/after: the same data in matplotlib default vs cinestyle."""
    rng = np.random.default_rng(SEED)
    x = np.arange(24)
    revenue = np.cumsum(rng.normal(1.0, 1.4, x.size)) + 12
    forecast = revenue + rng.normal(0.0, 0.8, x.size) + 1.5
    fig = plt.figure(figsize=(13.0, 5.2), facecolor="#0E0F13")
    fig.suptitle(
        "Same data, cinematic finish", color="white", fontsize=16, fontweight="bold"
    )
    before = fig.add_subplot(1, 2, 1)
    before.set_facecolor("white")
    before.plot(x, revenue, color="#1f77b4", linewidth=2)
    before.fill_between(x, revenue, color="#1f77b4", alpha=0.15)
    before.set_title("Before: matplotlib default", color="#C9C9D1")
    before.tick_params(colors="#C9C9D1")
    for spine in before.spines.values():
        spine.set_color("#777")
    theme = cs.get_theme("blade_runner")
    with theme.use():
        after = fig.add_subplot(1, 2, 2)
        for series in (revenue, forecast):
            after.plot(x, series, linewidth=2.5)
        cs.add_glow(after, intensity=theme.glow)
        after.set_title("After: cinestyle blade_runner", color=theme.foreground)
        after.set_facecolor(theme.surface)
        for spine in after.spines.values():
            spine.set_color(theme.foreground)
        after.tick_params(colors=theme.foreground)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    return fig


def accessibility_demo() -> Figure:
    """Show a theme palette beside its colorblind-safe variant."""
    theme = cs.get_theme("blade_runner")
    safe = cs.repair("blade_runner")
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 3.2), facecolor="#0A0C12")
    for ax, palette, title in (
        (axes[0], theme.palette, "blade_runner"),
        (axes[1], safe, "repaired (colorblind safe)"),
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


def _save(fig: Figure, path: Path, dpi: int) -> Path:
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
    """Render the themed cards, the hero, and the accessibility demo."""
    outdir.mkdir(parents=True, exist_ok=True)
    paths = [
        _save(hero(), outdir / "hero_before_after.png", dpi),
        _save(accessibility_demo(), outdir / "accessibility.png", dpi),
    ]
    for name in THEMED:
        paths.append(_save(card(name), outdir / f"{name}.png", dpi))
    return paths


def _film_frame(
    card_img: Image.Image, marquee: str, size: tuple[int, int]
) -> Image.Image:
    """Place a card inside a film-strip frame with sprockets and a marquee."""
    frame = Image.new("RGB", size, "#0a0a0a")
    draw = ImageDraw.Draw(frame)
    sprocket_w, gap = 26, 18
    for edge_x in (16, size[0] - 16 - sprocket_w):
        y = 22
        while y < size[1] - 90:
            draw.rounded_rectangle(
                [edge_x, y, edge_x + sprocket_w, y + 30], radius=6, fill="#2a2a2a"
            )
            y += 30 + gap
    inner_w = size[0] - 2 * (sprocket_w + 40)
    scaled = card_img.resize((inner_w, int(card_img.height * inner_w / card_img.width)))
    frame.paste(scaled, ((size[0] - scaled.width) // 2, 28))
    try:
        big = ImageFont.truetype(str(_FONT_DIR / "BebasNeue-Regular.ttf"), 46)
        small = ImageFont.truetype(str(_FONT_DIR / "BebasNeue-Regular.ttf"), 22)
    except OSError:  # pragma: no cover - font always ships
        big = small = ImageFont.load_default()
    draw.text(
        (size[0] // 2, size[1] - 70),
        "NOW SHOWING",
        font=small,
        fill="#7a7a7a",
        anchor="mm",
    )
    draw.text(
        (size[0] // 2, size[1] - 40),
        marquee.upper(),
        font=big,
        fill="#ededed",
        anchor="mm",
    )
    return frame


def build_reel(
    outdir: Path = _IMAGES_DIR, dpi: int = 150, duration: int = 1100
) -> Path:
    """Assemble the themed cards into a looping film-reel GIF."""
    size = (1180, 820)
    frames = []
    for name, (marquee, _drawer) in THEMED.items():
        buffer = outdir / f"_reel_{name}.png"
        _save(card(name), buffer, dpi)
        with Image.open(buffer) as raw:
            frame = _film_frame(raw.convert("RGB"), marquee, size)
        frames.append(frame.convert("P", palette=Image.ADAPTIVE, colors=256))
        buffer.unlink()
    gif = outdir / "cinestyle_reel.gif"
    frames[0].save(
        gif,
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=0,
        disposal=2,
        optimize=False,
    )
    return gif


def main() -> None:
    parser = argparse.ArgumentParser(description="Regenerate the cinestyle gallery.")
    parser.add_argument("-o", "--outdir", type=Path, default=_IMAGES_DIR)
    parser.add_argument("--dpi", type=int, default=130)
    parser.add_argument("--reel", action="store_true", help="also build the GIF")
    args = parser.parse_args()
    for path in render_all(args.outdir, dpi=args.dpi):
        print(f"wrote {path}")
    if args.reel:
        print(f"wrote {build_reel(args.outdir)}")


if __name__ == "__main__":
    main()
