"""Tests for the user-defined brand API and matplotlibrc export/import."""

from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import to_hex

from cinestyle import Brand, define_brand


def _hex(color: object) -> str:
    return to_hex(color)


def _acme() -> Brand:
    return define_brand(
        "acme",
        palette=["#0B5FFF", "#FF6B00", "#00B5AD"],
        background="#FBFBFD",
        foreground="#1A1A2E",
        grid_color="#E3E3EA",
    )


def test_as_rc_carries_fields() -> None:
    brand = _acme()
    rc = brand.as_rc()
    assert rc["axes.prop_cycle"].by_key()["color"] == list(brand.palette)
    assert _hex(rc["figure.facecolor"]) == _hex("#FBFBFD")
    assert _hex(rc["axes.edgecolor"]) == _hex(
        "#1A1A2E"
    )  # edge falls back to foreground
    assert rc["axes.grid"] is True
    assert _hex(rc["grid.color"]) == _hex("#E3E3EA")


def test_surface_defaults_to_background() -> None:
    brand = _acme()
    assert _hex(brand.as_rc()["axes.facecolor"]) == _hex("#FBFBFD")


def test_use_scopes_and_restores() -> None:
    brand = _acme()
    before = mpl.rcParams["figure.facecolor"]
    with brand.use():
        assert _hex(mpl.rcParams["figure.facecolor"]) == _hex("#FBFBFD")
    assert mpl.rcParams["figure.facecolor"] == before


def test_register_makes_brand_available() -> None:
    name = _acme().register()
    assert name == "cinestyle-acme"
    assert name in plt.style.available
    with plt.style.context(name):
        assert _hex(mpl.rcParams["axes.facecolor"]) == _hex("#FBFBFD")


def test_extra_rc_overlays_last() -> None:
    brand = define_brand(
        "bold",
        palette=["#000000"],
        extra_rc={"lines.linewidth": 4.0, "axes.titlesize": 22},
    )
    rc = brand.as_rc()
    assert rc["lines.linewidth"] == 4.0
    assert rc["axes.titlesize"] == 22


def test_matplotlibrc_export_loads_with_plt_style(tmp_path: Path) -> None:
    brand = _acme()
    path = brand.to_matplotlibrc(tmp_path / "acme.mplstyle")
    assert path.exists()
    # Hex colors are written without '#', which would otherwise start a comment.
    assert "FBFBFD" in path.read_text()
    with plt.style.context(str(path)):
        assert _hex(mpl.rcParams["figure.facecolor"]) == _hex("#FBFBFD")
        loaded_cycle = [
            _hex(c) for c in mpl.rcParams["axes.prop_cycle"].by_key()["color"]
        ]
        assert loaded_cycle == [_hex("#0B5FFF"), _hex("#FF6B00"), _hex("#00B5AD")]


def test_matplotlibrc_roundtrip_reconstructs_brand(tmp_path: Path) -> None:
    original = _acme()
    path = original.to_matplotlibrc(tmp_path / "acme.mplstyle")
    loaded = Brand.from_matplotlibrc(path, name="acme2")
    assert [_hex(c) for c in loaded.palette] == [_hex(c) for c in original.palette]
    assert _hex(loaded.background) == _hex(original.background)
    assert _hex(loaded.foreground) == _hex(original.foreground)
    assert loaded.grid_color is not None
    assert _hex(loaded.grid_color) == _hex(original.grid_color)
    # The reconstructed brand produces the same key chrome.
    assert _hex(loaded.as_rc()["figure.facecolor"]) == _hex(
        original.as_rc()["figure.facecolor"]
    )
