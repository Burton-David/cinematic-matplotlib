"""Tests for the Theme engine, the catalog, brands, and fonts."""

from __future__ import annotations

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.colors import to_hex

import cinestyle as cs
from cinestyle import Theme, available_fonts, define_brand, get_theme, list_themes


def _hex(color: object) -> str:
    return to_hex(color)


def test_catalog_themes() -> None:
    names = list_themes()
    assert len(names) == 18
    assert {"noir", "ghibli", "wes_anderson", "blade_runner", "star_wars"} <= set(names)
    assert {"matrix", "dune", "fury_road", "kill_bill", "in_the_mood"} <= set(names)
    assert {"sin_city", "akira", "the_fall"} <= set(names)
    assert {"tron", "amelie", "the_shining", "drive", "grand_budapest"} <= set(names)


def test_get_theme_unknown_raises() -> None:
    with pytest.raises(KeyError):
        get_theme("not_a_film")


@pytest.mark.parametrize("name", list_themes())
def test_theme_builds_and_applies(name: str) -> None:
    theme = get_theme(name)
    rc = theme.as_rc()
    # prop_cycle carries the derived palette and the default cmap is the theme's.
    assert rc["axes.prop_cycle"].by_key()["color"] == theme.palette
    assert rc["image.cmap"] == theme.sequential_name
    # as_rc is a valid rcParams mapping (rc_context would raise on a bad key).
    before = mpl.rcParams["axes.facecolor"]
    with theme.use():
        assert _hex(mpl.rcParams["axes.facecolor"]) == _hex(theme.surface)
        assert mpl.rcParams["axes.prop_cycle"].by_key()["color"] == theme.palette
        assert theme.sequential_name in mpl.colormaps
    assert mpl.rcParams["axes.facecolor"] == before  # leak-free


@pytest.mark.parametrize("name", list_themes())
def test_theme_font_is_bundled_or_generic(name: str) -> None:
    theme = get_theme(name)
    assert theme.font_family in available_fonts() or theme.font_family in {
        "DejaVu Sans",
        "serif",
        "sans-serif",
    }


def test_register_adds_styles_and_colormaps() -> None:
    names = cs.register()
    assert len(names) == 18
    assert all(n in plt.style.available for n in names)
    assert "cinestyle:dune" in mpl.colormaps
    assert "cinestyle:dune_div" in mpl.colormaps
    with plt.style.context("cinestyle-matrix"):
        assert _hex(mpl.rcParams["figure.facecolor"]) == _hex(
            get_theme("matrix").background
        )


def test_theme_renders_many_chart_types_headless() -> None:
    rng = np.random.default_rng(0)
    with cs.use("blade_runner"):
        fig, ax = plt.subplots(2, 2)
        ax[0, 0].plot(np.sin(np.linspace(0, 6, 50)))
        ax[0, 1].bar(["a", "b", "c"], [3, 1, 2])
        ax[1, 0].boxplot([rng.normal(size=50), rng.normal(size=50)])
        ax[1, 1].imshow(rng.random((6, 6)))
        fig.canvas.draw()  # exercises the full render path
    plt.close(fig)


def test_accessible_variant_theme_is_safe() -> None:
    safe = get_theme("blade_runner").accessible()
    report = cs.check_accessibility(safe.palette)
    assert report.safe


def test_define_brand_builds_usable_theme() -> None:
    brand = define_brand(
        "acme",
        palette=["#0B5FFF", "#FF6B00", "#00B5AD"],
        background="#FBFBFD",
        foreground="#1A1A2E",
    )
    assert isinstance(brand, Theme)
    with brand.use():
        assert _hex(mpl.rcParams["figure.facecolor"]) == _hex("#FBFBFD")


def test_brand_matplotlibrc_roundtrip(tmp_path: object) -> None:
    brand = define_brand("acme", palette=["#0B5FFF", "#FF6B00"], background="#FBFBFD")
    path = brand.to_matplotlibrc(tmp_path / "acme.mplstyle")  # type: ignore[operator]
    assert "FBFBFD" in path.read_text()
    with plt.style.context(str(path)):
        assert _hex(mpl.rcParams["figure.facecolor"]) == _hex("#FBFBFD")
