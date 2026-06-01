"""Tests for the accessibility checks and the colorblind-safe variant."""

from __future__ import annotations

import pytest

from cinestyle import accessible_variant, check_accessibility
from cinestyle.accessibility import (
    OKABE_ITO,
    contrast_ratio,
    relative_luminance,
    simulate_palette,
)
from cinestyle.color import min_pairwise_delta_e

pytest.importorskip("daltonlens", reason="accessibility needs the [a11y] extra")


def test_contrast_ratio_bounds() -> None:
    assert contrast_ratio("#000000", "#FFFFFF") == pytest.approx(21.0, abs=0.1)
    assert contrast_ratio("#777777", "#777777") == pytest.approx(1.0, abs=0.01)
    assert relative_luminance("#FFFFFF") > relative_luminance("#000000")


def test_simulate_palette_preserves_length() -> None:
    palette = ["#FF0000", "#00FF00", "#0000FF"]
    for deficiency in ("protan", "deutan", "tritan"):
        out = simulate_palette(palette, deficiency)
        assert len(out) == 3


def test_okabe_ito_is_reported_safe() -> None:
    report = check_accessibility(list(OKABE_ITO[:-1]))
    assert report.safe
    assert "SAFE" in report.summary()


def test_collapsing_palette_is_flagged() -> None:
    # Red and green collapse under deuteranopia/protanopia.
    report = check_accessibility(["#D62728", "#2CA02C", "#1F77B4"])
    assert not report.safe
    assert min(report.cvd_min_delta_e.values()) < report.threshold


def test_accessible_variant_is_safe_and_same_length() -> None:
    risky = ["#08F7FE", "#FE53BB", "#F5D300", "#09FBD3", "#B537F2"]
    safe = accessible_variant(risky)
    assert len(safe) == len(risky)
    assert min_pairwise_delta_e(safe) >= min_pairwise_delta_e(risky)
    assert check_accessibility(safe).safe


def test_low_contrast_against_background_flagged() -> None:
    # A near-black series on a black background fails non-text contrast.
    report = check_accessibility(["#111111", "#F5D300"], background="#000000")
    assert 0 in report.low_contrast_indices
