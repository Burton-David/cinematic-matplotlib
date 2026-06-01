"""Edge cases and guarantees: repair safety, helpful errors, adapter guards."""

from __future__ import annotations

from typing import Any

import pytest

import cinestyle as cs


@pytest.mark.parametrize("name", cs.list_themes())
def test_repair_is_safe_and_full_length(name: str) -> None:
    pytest.importorskip("daltonlens")
    safe = cs.repair(name)
    # The headline guarantee: repair never returns a palette it would call unsafe,
    # and it keeps the theme's color count.
    assert len(safe) == len(cs.get_theme(name).palette)
    assert cs.audit(safe).safe


def test_get_look_unknown_name_is_helpful() -> None:
    with pytest.raises(KeyError, match="Unknown look"):
        cs.get_look("not_a_look")


def test_colormap_hex_rejects_unknown_kind() -> None:
    with pytest.raises(ValueError, match="sequential"):
        cs.get_theme("dune").colormap_hex("sequental")  # deliberate typo


def test_look_rejects_nonpositive_gamma() -> None:
    with pytest.raises(ValueError, match="gamma"):
        cs.Look("bad", gamma=0.0)


def test_plotly_adapter_missing_dependency_message(monkeypatch: Any) -> None:
    from cinestyle.adapters import plotly as adapter

    monkeypatch.setattr(adapter, "find_spec", lambda _name: None)
    with pytest.raises(ImportError, match=r"cinestyle\[plotly\]"):
        adapter.register_plotly()


def test_altair_adapter_missing_dependency_message(monkeypatch: Any) -> None:
    from cinestyle.adapters import altair as adapter

    monkeypatch.setattr(adapter, "find_spec", lambda _name: None)
    with pytest.raises(ImportError, match=r"cinestyle\[altair\]"):
        adapter.register_altair()


def test_plotly_apply_and_restore() -> None:
    pytest.importorskip("plotly")
    import plotly.io as pio

    before = pio.templates.default
    name = cs.use_plotly("dune")
    try:
        assert pio.templates.default == name
        colorway = pio.templates[name].layout.colorway
        assert colorway[0].lower() == cs.get_theme("dune").palette[0].lower()
    finally:
        pio.templates.default = before
    assert pio.templates.default == before


def test_altair_enable_and_restore() -> None:
    alt = pytest.importorskip("altair")

    before = alt.theme.active
    cs.use_altair("dune")
    try:
        assert alt.theme.active == "cinestyle-dune"
    finally:
        alt.theme.enable(before)
    assert alt.theme.active == before
