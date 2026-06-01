"""Tests for the perceptual color pipeline."""

from __future__ import annotations

from coloraide import Color

from cinestyle import color


def _hue(hex_color: str) -> float:
    h = Color(hex_color).convert("oklch")["hue"]
    return 0.0 if h != h else float(h)  # NaN -> achromatic


def test_categorical_cycle_keeps_heroes_first() -> None:
    heroes = ["#08F7FE", "#FE53BB", "#F5D300"]
    cycle = color.categorical_cycle(heroes, 8)
    assert len(cycle) == 8
    assert cycle[:3] == [c.upper() for c in heroes]


def test_categorical_cycle_is_unique_and_separated() -> None:
    cycle = color.categorical_cycle(["#08F7FE", "#FE53BB", "#F5D300"], 8)
    assert len(set(cycle)) == len(cycle)
    # Distinct hues should separate well in CIEDE2000.
    assert color.min_pairwise_delta_e(cycle) > 10.0


def test_categorical_cycle_preserves_mood_for_mono_palette() -> None:
    # A single-hue (green) seed should extend within the green family, not jump
    # to off-mood hues; verify added colors stay near the seed hue.
    green = "#00C040"
    seed_hue = _hue(green)
    cycle = color.categorical_cycle([green], 6)
    for c in cycle[1:]:
        diff = abs((_hue(c) - seed_hue + 180) % 360 - 180)
        assert diff < 60.0, f"{c} drifted {diff:.0f}deg off the green family"


def test_sequential_is_monotonic_in_lightness() -> None:
    cmap = color.sequential_cmap("#08F7FE", "t-seq")
    assert color.is_monotonic_lightness(cmap)


def test_diverging_is_symmetric_and_lighter_in_middle() -> None:
    cmap = color.diverging_cmap("#0E4D64", "#E0531F", "t-div")
    profile = color.lightness_profile(cmap)
    mid = len(profile) // 2
    assert profile[mid] > profile[0]
    assert profile[mid] > profile[-1]
    assert abs(profile[0] - profile[-1]) < 0.1  # arms end at similar lightness


def test_delta_e_zero_for_identical() -> None:
    assert color.delta_e2000("#123456", "#123456") == 0.0
    assert color.delta_e2000("#000000", "#FFFFFF") > 50.0
