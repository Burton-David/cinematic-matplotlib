"""Tests for the animation engine, presets, and reveal helpers."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pytest

import cinestyle as cs
from cinestyle import anim
from cinestyle.anim import engine


def test_get_preset_resolves_names_and_passthrough() -> None:
    assert anim.get_preset("ticker").name == "ticker"
    same = anim.PRESETS["flowing"]
    assert anim.get_preset(same) is same
    assert anim.get_preset(None) is None
    with pytest.raises(KeyError):
        anim.get_preset("nope")


@pytest.mark.parametrize(
    "ease",
    [anim.linear, anim.ease_out_cubic, anim.ease_in_out_sine, anim.ease_out_quad],
)
def test_easings_span_zero_to_one_monotonically(ease) -> None:
    assert ease(0.0) == pytest.approx(0.0, abs=1e-9)
    assert ease(1.0) == pytest.approx(1.0, abs=1e-9)
    samples = [ease(t) for t in np.linspace(0, 1, 21)]
    assert all(b >= a - 1e-9 for a, b in zip(samples, samples[1:], strict=False))


def test_progress_maps_frame_index_to_unit_interval() -> None:
    assert anim.progress(0, 10, None) == 0.0
    assert anim.progress(9, 10, None) == pytest.approx(1.0)
    # Easing is applied to the raw progress.
    assert anim.progress(9, 10, anim.ease_out_cubic) == pytest.approx(1.0)


def test_tween_and_count_up() -> None:
    assert anim.tween(0.0, 10.0, 0.5) == pytest.approx(5.0)
    np.testing.assert_allclose(anim.tween([0, 0], [10, 20], 0.25), [2.5, 5.0])
    assert anim.count_up(80.0, 0.5) == pytest.approx(40.0)


def test_reveal_line_unmasks_a_prefix() -> None:
    fig, ax = plt.subplots()
    (line,) = ax.plot([], [])
    x = np.arange(100)
    anim.reveal_line(line, x, x**2, 0.5)
    assert len(line.get_xdata()) == 50
    anim.reveal_line(line, x, x**2, 1.0)
    assert len(line.get_xdata()) == 100
    plt.close(fig)


def test_grow_bars_scales_heights() -> None:
    fig, ax = plt.subplots()
    bars = ax.bar(["a", "b"], [0, 0])
    anim.grow_bars(bars, [4, 8], 0.5)
    assert [b.get_height() for b in bars] == pytest.approx([2.0, 4.0])
    plt.close(fig)


def test_animate_writes_a_gif(tmp_path: Path) -> None:
    x = np.linspace(0, 10, 40)
    with cs.theme("margin_call"):
        fig, ax = plt.subplots()
        ax.set_xlim(0, 10)
        ax.set_ylim(-1, 1)
        (line,) = ax.plot([], [])

        def update(i: object) -> object:
            t = anim.progress(int(i), 6, anim.ease_out_cubic)  # type: ignore[arg-type]
            return (anim.reveal_line(line, x, np.sin(x), t),)

        out = anim.animate(
            fig, 6, update, preset="ticker", out=tmp_path / "a.gif", dpi=60
        )
    assert out.exists() and out.stat().st_size > 0
    assert out.suffix == ".gif"


def test_mp4_request_falls_back_to_gif_without_ffmpeg(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(engine, "_ffmpeg_ready", lambda: False)
    with cs.theme("margin_call"):
        fig, ax = plt.subplots()
        bars = ax.bar(["a", "b", "c"], [0, 0, 0])
        ax.set_ylim(0, 10)

        def update(i: object) -> object:
            t = anim.progress(int(i), 5, anim.ease_out_quad)  # type: ignore[arg-type]
            return anim.grow_bars(bars, [6, 9, 3], t)

        out = anim.animate(fig, 5, update, out=tmp_path / "bars.mp4", dpi=60)
    assert out.suffix == ".gif"  # degraded rather than failed
    assert out.exists()
