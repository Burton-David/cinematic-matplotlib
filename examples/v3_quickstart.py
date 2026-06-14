#!/usr/bin/env python3
"""A tour of the v3 additions: subject themes, chart idioms, scaffolding, motion.

Run headless with ``python examples/v3_quickstart.py``; it writes a few files to
the current directory. The animation needs no system ffmpeg (it falls back to a
gif), and the choropleth is skipped unless the [geo] extra is installed.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

import cinestyle as cs  # noqa: E402
from cinestyle import anim, charts  # noqa: E402


def finished_chart() -> None:
    """A markets P&L bar chart, finished with the editorial scaffolding."""
    rng = np.random.default_rng(11)
    pnl = rng.normal(0.4, 2.3, 30)
    down, up = cs.get_theme("terminal").div_pair  # subject-word alias resolves
    with cs.theme("terminal"):
        fig, ax = plt.subplots(figsize=(9, 5))
        ax.bar(np.arange(30), pnl, color=[up if v >= 0 else down for v in pnl])
        cs.currency(ax, "y", "$")
        cs.finish(
            ax,
            "Green days are common, the red days are the ones that matter",
            "Desk P&L, last 30 sessions, USD millions",
            source="Source: synthetic",
        )
        assert not cs.lint_text(fig)  # no em or en dashes slipped in
        cs.save(fig, "v3_finished.png")


def signature_mountain() -> None:
    """The mountain idiom: a topographic silhouette with marked peaks."""
    rng = np.random.default_rng(11)
    x = np.linspace(0, 1, 280)
    ridge = (
        2.0
        + 2.4 * np.exp(-((x - 0.6) ** 2) / 0.02)
        + 1.5 * np.exp(-((x - 0.3) ** 2) / 0.015)
        + np.cumsum(rng.normal(0, 0.02, x.size))
    )
    with cs.theme("altitude"):
        fig, ax = plt.subplots(figsize=(11, 5))
        charts.mountain(ridge, ax=ax, layers=4, label_fmt="{:.1f} km")
        cs.finish(ax, "Two summits, one ridgeline")
        ax.set_xticks([])
        cs.save(fig, "v3_mountain.png")


def motion() -> None:
    """Animate a counting-up reveal in the terminal theme's ticker preset."""
    x = np.linspace(0, 12, 160)
    nav = 100 * np.cumprod(1 + np.random.default_rng(11).normal(0.006, 0.02, x.size))
    frames = 36
    with cs.theme("terminal"):
        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.set_xlim(0, 12)
        ax.set_ylim(nav.min() * 0.95, nav.max() * 1.05)
        (line,) = ax.plot([], [], color=cs.get_theme("terminal").primary, lw=2.2)

        def update(frame: object) -> object:
            t = anim.progress(int(frame), frames, anim.ease_out_cubic)  # type: ignore[arg-type]
            return (anim.reveal_line(line, x, nav, t),)

        out = anim.animate(fig, frames, update, preset="ticker", out="v3_reveal.mp4")
        print(f"wrote {out}")


if __name__ == "__main__":
    finished_chart()
    signature_mountain()
    motion()
    print("wrote v3_finished.png, v3_mountain.png, and the reveal")
