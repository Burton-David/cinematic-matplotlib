#!/usr/bin/env python3
"""Regenerate the v3 gallery: the four subject themes, the idiom sheet, the
signature mountain, and a short animated reveal.

Each subject theme is shown doing the job it was designed for (a trading P&L, an
oil field's output, an alpine ascent, a map), drawn with the v3 chart builders
and finished with the editorial scaffolding. Everything is built from seeded
synthetic data so the committed images regenerate exactly. The choropleth card
needs the [geo] extra; it is skipped with a note if geopandas is absent.

    python scripts/generate_v3_gallery.py            # stills
    python scripts/generate_v3_gallery.py --reveal   # also the animated gif
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402

import cinestyle as cs  # noqa: E402
from cinestyle import anim, charts  # noqa: E402

SEED = 11
_ROOT = Path(__file__).resolve().parent.parent
_IMAGES = _ROOT / "images"


def _guard_clean(fig: Figure) -> None:
    """Fail loudly if any chart text smuggled in an em or en dash."""
    offenders = cs.lint_text(fig)
    if offenders:
        raise AssertionError(f"house-style dashes in a gallery figure: {offenders}")


def margin_call_card() -> Figure:
    rng = np.random.default_rng(SEED)
    pnl = rng.normal(0.4, 2.3, 30)
    pnl[17] = -6.8  # the one session that ruins a quarter
    down, up = cs.get_theme("margin_call").div_pair
    with cs.theme("margin_call"):
        fig, ax = plt.subplots(figsize=(8.0, 5.0))
        ax.bar(np.arange(30), pnl, color=[up if v >= 0 else down for v in pnl])
        ax.axhline(0, color=cs.get_theme("margin_call").foreground, linewidth=1.0)
        cs.currency(ax, "y", "$")
        cs.finish(
            ax,
            "Green days are common, the red days are the ones that matter",
            "Desk P&L, last 30 sessions, USD millions",
            source="Source: synthetic",
        )
    return fig


def there_will_be_blood_card() -> Figure:
    rng = np.random.default_rng(SEED)
    t = np.linspace(0, 30, 60)
    fields = ["Little Boston", "Coyote Hills", "Bandy", "Sunday Ranch"]
    base = np.array([np.exp(-((t - p) ** 2) / 40) for p in (6, 14, 20, 26)])
    output = np.abs(base * rng.uniform(3, 9, (4, 1)) + rng.normal(0, 0.2, base.shape))
    with cs.theme("there_will_be_blood"):
        fig, ax = plt.subplots(figsize=(8.0, 5.0))
        charts.streamgraph(output, x=t, labels=fields, ax=ax)
        ax.legend(loc="upper left", ncols=2)
        cs.finish(
            ax,
            "The wells that built a fortune, and ran dry",
            "Daily output by field, thousands of barrels",
            source="Source: synthetic",
        )
    return fig


def the_revenant_card() -> Figure:
    rng = np.random.default_rng(SEED)
    x = np.linspace(0, 1, 240)
    ridge = (
        2600
        + 1500 * np.sin(x * 5.5) ** 2
        + 900 * np.sin(x * 2.1)
        + np.cumsum(rng.normal(0, 12, x.size))
    )
    with cs.theme("the_revenant"):
        fig, ax = plt.subplots(figsize=(8.0, 5.0))
        charts.mountain(
            ridge,
            ax=ax,
            zone=(4000, ridge.max() + 100),
            zone_label="death zone",
            label_fmt="{:.0f} m",
        )
        cs.finish(
            ax,
            "Above the death zone, every step is borrowed time",
            "Elevation along the summit ridge, metres",
            source="Source: synthetic",
        )
        ax.set_xticks([])
    return fig


def raiders_card() -> Figure:
    rng = np.random.default_rng(SEED)
    grid = np.add.outer(np.linspace(0, 1, 36), np.cos(np.linspace(0, 3, 48)))
    grid += rng.normal(0, 0.08, grid.shape)
    with cs.theme("raiders"):
        fig, ax = plt.subplots(figsize=(8.0, 5.0))
        ax.imshow(grid, cmap=cs.get_theme("raiders").sequential, aspect="auto")
        ax.grid(True, color=cs.get_theme("raiders").muted, linewidth=0.6)
        ax.set_xticks(np.linspace(0, 48, 7))
        ax.set_yticks(np.linspace(0, 36, 5))
        cs.finish(
            ax,
            "The valley reads as terrain, not a table",
            "Surveyed elevation, metres above the river",
            source="Source: synthetic",
        )
    return fig


def idiom_sheet() -> Figure:
    rng = np.random.default_rng(SEED)
    with cs.theme("margin_call"):
        fig, axes = plt.subplots(2, 3, figsize=(13.5, 8.0))
        charts.beeswarm(rng.normal(size=160), ax=axes[0, 0])
        axes[0, 0].set_title("beeswarm")

        charts.dumbbell(
            ["NA", "EMEA", "APAC", "LatAm"],
            [42, 38, 21, 12],
            [55, 41, 47, 25],
            ax=axes[0, 1],
        )
        axes[0, 1].set_title("dumbbell")

        charts.ridgeline(
            [rng.normal(m, 1.0, 200) for m in range(5)],
            labels=[f"wk {i}" for i in range(5)],
            ax=axes[0, 2],
        )
        axes[0, 2].set_title("ridgeline")

        charts.slope(
            ["Alpha", "Beta", "Gamma"], [30, 22, 8], [18, 27, 24], ax=axes[1, 0]
        )
        axes[1, 0].set_title("slope")

        equity = np.cumprod(1 + rng.normal(0.004, 0.03, 250))
        charts.underwater(equity, ax=axes[1, 1])
        axes[1, 1].set_title("underwater")

        charts.sankey(
            [
                ("Revenue", "Gross", 100),
                ("Gross", "Opex", 55),
                ("Gross", "Margin", 45),
                ("Margin", "Tax", 12),
                ("Margin", "Net", 33),
            ],
            ax=axes[1, 2],
        )
        axes[1, 2].set_title("sankey")

        for ax in axes.flat:
            cs.despine(ax)
        fig.suptitle(
            "cinestyle.charts: idioms matplotlib has no shorthand for",
            fontweight="bold",
        )
        fig.tight_layout(rect=(0, 0, 1, 0.96))
    return fig


def mountain_hero() -> Figure:
    rng = np.random.default_rng(SEED)
    x = np.linspace(0, 1, 320)
    ridge = (
        1.5
        + 2.6 * np.exp(-((x - 0.62) ** 2) / 0.02)
        + 1.7 * np.exp(-((x - 0.31) ** 2) / 0.015)
        + 1.1 * np.exp(-((x - 0.83) ** 2) / 0.01)
        + np.cumsum(rng.normal(0, 0.02, x.size))
    )
    with cs.theme("the_revenant"):
        fig, ax = plt.subplots(figsize=(12.0, 5.2))
        charts.mountain(
            ridge,
            ax=ax,
            layers=4,
            peaks=[99, 198, 266],
            peak_labels=["North Tower", "Summit", "East Spur"],
            label_fmt="{:.1f} km",
        )
        cs.finish(
            ax,
            "Three summits, one ridgeline",
            "A topographic silhouette built from a single profile",
            source="cinestyle.charts.mountain",
        )
        ax.set_xticks([])
    return fig


def reveal_gif(out: Path) -> Path:
    x = np.linspace(0, 12, 160)
    equity = 100 * np.cumprod(
        1 + np.random.default_rng(SEED).normal(0.006, 0.02, x.size)
    )
    n_frames = 48
    with cs.theme("margin_call"):
        fig, ax = plt.subplots(figsize=(8.0, 4.5))
        ax.set_xlim(0, 12)
        ax.set_ylim(equity.min() * 0.95, equity.max() * 1.05)
        (line,) = ax.plot([], [], color=cs.get_theme("margin_call").primary, lw=2.2)
        readout = ax.text(
            0.02,
            0.9,
            "",
            transform=ax.transAxes,
            fontsize=20,
            color=cs.get_theme("margin_call").primary,
        )
        cs.finish(ax, "Net asset value", "Counting up, ticker style")

        def update(frame: object) -> object:
            t = anim.progress(int(frame), n_frames, anim.ease_out_cubic)  # type: ignore[arg-type]
            anim.reveal_line(line, x, equity, t)
            shown = equity[: max(1, int(t * x.size))][-1]
            readout.set_text(f"${shown:,.0f}")
            return line, readout

        cs.add_glow(line, intensity=0.3)
        return anim.animate(fig, n_frames, update, preset="ticker", out=out, dpi=90)


def choropleth_card() -> Figure | None:
    try:
        import geopandas as gpd
        from shapely.geometry import box
    except ImportError:
        print("skipping choropleth card: install cinestyle[geo]")
        return None
    rng = np.random.default_rng(SEED)
    cells = [box(i, j, i + 1, j + 1) for j in range(6) for i in range(9)]
    field = [
        np.exp(-((i - 4) ** 2 + (j - 3) ** 2) / 9) + rng.normal(0, 0.05)
        for j in range(6)
        for i in range(9)
    ]
    gdf = gpd.GeoDataFrame({"reach": field}, geometry=cells)
    with cs.theme("raiders"):
        fig, ax = plt.subplots(figsize=(8.0, 5.2))
        charts.choropleth(gdf, "reach", ax=ax, legend=True)
        cs.finish(ax, "Influence falls off with distance from the capital")
    return fig


_CARDS = {
    "margin_call": margin_call_card,
    "there_will_be_blood": there_will_be_blood_card,
    "the_revenant": the_revenant_card,
    "raiders": raiders_card,
    "v3_idioms": idiom_sheet,
    "mountain_hero": mountain_hero,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Regenerate the v3 gallery.")
    parser.add_argument("-o", "--outdir", type=Path, default=_IMAGES)
    parser.add_argument("--reveal", action="store_true", help="also build the gif")
    args = parser.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)

    for name, builder in _CARDS.items():
        fig = builder()
        _guard_clean(fig)
        path = cs.save(fig, args.outdir / f"{name}.png")
        print(f"wrote {path}")

    chart = choropleth_card()
    if chart is not None:
        _guard_clean(chart)
        print(f"wrote {cs.save(chart, args.outdir / 'choropleth.png')}")

    if args.reveal:
        print(f"wrote {reveal_gif(args.outdir / 'v3_reveal.gif')}")


if __name__ == "__main__":
    main()
