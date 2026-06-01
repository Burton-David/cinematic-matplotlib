"""Tests for the built-in film styles.

Assertions check that styling is actually applied -- rcParams change, artist
colors match the declared palette, axes chrome is set -- rather than merely that
calls do not raise.
"""

from __future__ import annotations

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.colors import to_hex

import cinestyle
from cinestyle import (
    BladeRunner,
    CinematicStyle,
    FilmNoir,
    Ghibli,
    StarWars,
    WesAnderson,
)

ALL_STYLES: list[type[CinematicStyle]] = [
    FilmNoir,
    Ghibli,
    WesAnderson,
    BladeRunner,
    StarWars,
]


@pytest.fixture(params=ALL_STYLES, ids=[c.__name__ for c in ALL_STYLES])
def style(request: pytest.FixtureRequest) -> CinematicStyle:
    return request.param()


def _hex(color: object) -> str:
    return to_hex(color)


def test_as_rc_carries_palette_and_surface(style: CinematicStyle) -> None:
    rc = style.as_rc()
    cycle_colors = rc["axes.prop_cycle"].by_key()["color"]
    assert cycle_colors == list(style.palette)
    assert _hex(rc["axes.facecolor"]) == _hex(style.surface)
    assert _hex(rc["figure.facecolor"]) == _hex(style.background)


def test_use_scopes_and_restores(style: CinematicStyle) -> None:
    before = mpl.rcParams["axes.facecolor"]
    with style.use():
        assert _hex(mpl.rcParams["axes.facecolor"]) == _hex(style.surface)
        assert _hex(mpl.rcParams["text.color"]) == _hex(style.foreground)
    assert mpl.rcParams["axes.facecolor"] == before


def test_apply_then_restore_roundtrip(style: CinematicStyle) -> None:
    before = mpl.rcParams["axes.edgecolor"]
    style.apply()
    assert _hex(mpl.rcParams["axes.edgecolor"]) == _hex(style._edge)
    style.restore()
    assert mpl.rcParams["axes.edgecolor"] == before


def test_style_axes_applies_chrome(style: CinematicStyle) -> None:
    fig, ax = plt.subplots()
    style.style_axes(ax)
    assert _hex(ax.get_facecolor()) == _hex(style.surface)
    assert _hex(ax.spines["left"].get_edgecolor()) == _hex(style._edge)
    assert ax.spines["top"].get_visible() == style.framed
    plt.close(fig)


def test_plot_line_uses_primary_color(style: CinematicStyle) -> None:
    x = np.linspace(0, 10, 50)
    ax = style.plot_line(x, np.sin(x))
    assert len(ax.lines) == 1
    assert _hex(ax.lines[0].get_color()) == _hex(style.colors["primary"])
    plt.close(ax.figure)


def test_convenience_plots_render_and_do_not_leak(style: CinematicStyle) -> None:
    before = mpl.rcParams["axes.facecolor"]
    rng = np.random.default_rng(0)
    x = np.linspace(0, 10, 40)
    assert len(style.plot_bar(["a", "b", "c"], [3, 1, 2]).patches) == 3
    assert len(style.plot_scatter(x, np.cos(x)).collections) == 1
    assert len(style.plot_histogram(rng.standard_normal(200), bins=12).patches) == 12
    assert style.plot_area(x, np.abs(np.sin(x))).lines  # area draws an outline too
    heat_ax = style.plot_heatmap(rng.random((6, 6)))
    assert len(heat_ax.images) == 1
    # None of the convenience helpers leak global rcParams.
    assert mpl.rcParams["axes.facecolor"] == before
    plt.close("all")


def test_register_adds_named_style_sheets() -> None:
    names = cinestyle.register()
    assert names == [
        "cinestyle-noir",
        "cinestyle-ghibli",
        "cinestyle-wes_anderson",
        "cinestyle-blade_runner",
        "cinestyle-star_wars",
    ]
    assert all(name in plt.style.available for name in names)
    with plt.style.context("cinestyle-blade_runner"):
        assert _hex(mpl.rcParams["axes.facecolor"]) == _hex(BladeRunner.surface)


def test_noir_signature_methods() -> None:
    noir = FilmNoir()
    ax = noir.plot_shadows(["a", "b", "c"], [5, 8, 6], [7, 4, 9])
    assert len(ax.patches) == 6
    plt.close(ax.figure)
    ax = noir.plot_contrast([1, 3, 2, 4], [2, 1, 3, 1])
    assert len(ax.lines) == 2
    assert _hex(ax.lines[0].get_color()) == _hex(noir.colors["secondary"])
    plt.close(ax.figure)


def test_ghibli_signature_methods() -> None:
    ghibli = Ghibli()
    ax = ghibli.plot_landscape(np.abs(np.sin(np.linspace(0, 6, 60))) + 1)
    assert len(ax.collections) >= 2  # two stacked fills
    plt.close(ax.figure)
    ax = ghibli.plot_flow(np.cos(np.linspace(0, 6, 60)))
    assert len(ax.lines) == 2  # raw series + smoothed overlay
    plt.close(ax.figure)


def test_wes_anderson_signature_methods() -> None:
    wes = WesAnderson()
    ax = wes.plot_symmetry([5, 8, 6], [7, 4, 8], labels=["x", "y", "z"])
    assert len(ax.patches) == 6
    assert _hex(ax.patches[0].get_facecolor()) == _hex(wes.palette[0])
    plt.close(ax.figure)
    ax = wes.plot_grid(np.arange(9))
    assert len(ax.patches) == 9
    plt.close(ax.figure)


def test_blade_runner_signature_methods() -> None:
    blade = BladeRunner()
    ax = blade.plot_neon_lines(
        np.sin(np.linspace(0, 6, 50)), np.cos(np.linspace(0, 6, 50))
    )
    assert len(ax.lines) == 2
    assert _hex(ax.lines[0].get_color()) == _hex(blade.palette[0])
    plt.close(ax.figure)
    ax = blade.plot_matrix(np.random.default_rng(0).random((8, 8)))
    assert len(ax.images) == 1
    plt.close(ax.figure)


def test_star_wars_signature_methods() -> None:
    sw = StarWars()
    ax = sw.plot_balance(["x", "y"], [7, 5], [4, 8])
    assert len(ax.patches) == 4
    plt.close(ax.figure)
    ax = sw.plot_galaxy(["Jedi", "Sith", "Rebels"], [75, 60, 85])
    assert len(ax.patches) == 3
    assert len(ax.texts) == 3  # one value label per bar
    assert _hex(ax.patches[0].get_facecolor()) == _hex(sw.colors["light_side"])
    plt.close(ax.figure)


def test_explicit_axes_is_styled_in_place(style: CinematicStyle) -> None:
    fig, ax = plt.subplots()
    returned = style.plot_line([0, 1, 2], [0, 1, 0], ax=ax)
    assert returned is ax
    assert _hex(ax.get_facecolor()) == _hex(style.surface)
    plt.close(fig)
