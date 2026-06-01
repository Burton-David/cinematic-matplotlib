"""Tests for the cross-backend adapters and the audit/repair headline API."""

from __future__ import annotations

import pytest

import cinestyle as cs
from cinestyle.color import min_pairwise_delta_e


def test_colormap_hex_bridge() -> None:
    stops = cs.get_theme("dune").colormap_hex("sequential", 7)
    assert len(stops) == 7
    assert all(s.startswith("#") and len(s) == 7 for s in stops)
    # The diverging map differs from the sequential one.
    assert cs.get_theme("dune").colormap_hex("diverging", 7) != stops


# --------------------------------------------------------------------- plotly
def test_plotly_template_carries_tokens() -> None:
    pytest.importorskip("plotly")
    theme = cs.get_theme("blade_runner")
    template = cs.to_plotly_template("blade_runner")
    assert [c.lower() for c in template.layout.colorway] == [
        c.lower() for c in theme.palette
    ]
    assert template.layout.paper_bgcolor == theme.background
    assert template.layout.plot_bgcolor == theme.surface
    assert len(template.layout.colorscale.sequential) > 1
    assert len(template.layout.colorscale.diverging) > 1


def test_register_plotly_adds_all_templates() -> None:
    pytest.importorskip("plotly")
    import plotly.io as pio

    names = cs.register_plotly()
    assert len(names) == len(cs.list_themes())
    assert "cinestyle-dune" in pio.templates
    assert cs.use_plotly("matrix") == "cinestyle-matrix"
    assert pio.templates.default == "cinestyle-matrix"


# --------------------------------------------------------------------- altair
def test_altair_theme_carries_palette() -> None:
    pytest.importorskip("altair")
    theme = cs.get_theme("blade_runner")
    config = cs.to_altair_theme("blade_runner")
    assert config["background"] == theme.background
    assert config["config"]["range"]["category"] == list(theme.palette)
    assert config["config"]["view"]["fill"] == theme.surface


def test_register_altair_registers_and_enables() -> None:
    alt = pytest.importorskip("altair")
    names = cs.register_altair(enable="dune")
    assert len(names) == len(cs.list_themes())
    assert "cinestyle-dune" in alt.theme.names()
    assert alt.theme.active == "cinestyle-dune"


# ------------------------------------------------------------------ audit/repair
def test_audit_accepts_name_palette_and_theme() -> None:
    pytest.importorskip("daltonlens")
    by_name = cs.audit("blade_runner")
    by_theme = cs.audit(cs.get_theme("blade_runner"))
    assert by_name.cvd_min_delta_e == by_theme.cvd_min_delta_e
    assert cs.audit(["#D62728", "#2CA02C", "#1F77B4"]).safe is False


def test_repair_returns_safe_palette() -> None:
    pytest.importorskip("daltonlens")
    repaired = cs.repair("blade_runner")
    assert len(repaired) == len(cs.get_theme("blade_runner").palette)
    assert cs.audit(repaired).safe
    assert min_pairwise_delta_e(repaired) >= min_pairwise_delta_e(
        cs.get_theme("blade_runner").palette
    )
