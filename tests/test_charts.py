"""Tests for the chart-idiom builders.

Each test checks a real property of the drawn result, not just that the call
returned: the shape of the data that reached the axes, a color the active theme
should have supplied, or the structural move the idiom is supposed to make.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.axes import Axes
from matplotlib.collections import PathCollection, PolyCollection
from matplotlib.colors import to_hex
from matplotlib.image import AxesImage

import cinestyle as cs
from cinestyle import charts


@pytest.fixture
def axes() -> Axes:
    fig, ax = plt.subplots()
    yield ax
    plt.close(fig)


def test_beeswarm_spreads_points_without_dropping_any(axes: Axes) -> None:
    rng = np.random.default_rng(0)
    values = rng.normal(size=200)
    with cs.theme("margin_call"):
        charts.beeswarm(values, ax=axes, span=0.4)
    offsets = axes.collections[0].get_offsets()
    assert len(offsets) == 200  # every observation is plotted
    x = offsets[:, 0]
    assert x.min() >= -0.5 and x.max() <= 0.5  # stays inside its slot
    assert np.ptp(x) > 0  # the swarm actually spread sideways


def test_beeswarm_groups_take_distinct_cycle_colors(axes: Axes) -> None:
    rng = np.random.default_rng(1)
    values = rng.normal(size=60)
    groups = np.repeat(["a", "b", "c"], 20)
    with cs.theme("margin_call"):
        charts.beeswarm(values, groups=groups, ax=axes)
        palette = cs.get_theme("margin_call").palette
    colors = {to_hex(c.get_facecolor()[0]) for c in axes.collections}
    assert {palette[0].lower(), palette[1].lower(), palette[2].lower()} <= {
        c.lower() for c in colors
    }


def test_ridgeline_draws_one_ridge_per_distribution(axes: Axes) -> None:
    rng = np.random.default_rng(2)
    dists = [rng.normal(m, 1, 150) for m in range(4)]
    with cs.theme("the_revenant"):
        charts.ridgeline(dists, labels=list("WXYZ"), ax=axes)
    fills = [c for c in axes.collections if isinstance(c, PolyCollection)]
    assert len(fills) == 4
    assert [t.get_text() for t in axes.get_yticklabels()] == list("WXYZ")


def test_hexbin_density_returns_binned_collection(axes: Axes) -> None:
    rng = np.random.default_rng(3)
    with cs.theme("raiders"):
        coll = charts.hexbin_density(
            rng.normal(size=1000), rng.normal(size=1000), ax=axes
        )
    assert isinstance(coll, PolyCollection)
    assert coll.get_array().sum() > 0  # counts landed in cells


def test_dumbbell_end_dot_uses_primary(axes: Axes) -> None:
    with cs.theme("margin_call"):
        charts.dumbbell(["x", "y"], [1, 2], [4, 3], ax=axes)
        primary = cs.get_theme("margin_call").primary
    end = axes.collections[-1]
    assert to_hex(end.get_facecolor()[0]).lower() == primary.lower()
    assert [t.get_text() for t in axes.get_yticklabels()] == ["x", "y"]


def test_lollipop_places_a_dot_per_category(axes: Axes) -> None:
    with cs.theme("there_will_be_blood"):
        charts.lollipop(list("abcde"), [3, 1, 4, 1, 5], ax=axes)
    dots = axes.collections[-1].get_offsets()
    assert len(dots) == 5


def test_slope_connects_each_series_across_two_columns(axes: Axes) -> None:
    with cs.theme("raiders"):
        charts.slope(["A", "B", "C"], [1, 2, 3], [3, 1, 2], ax=axes)
    series_lines = [ln for ln in axes.lines if len(ln.get_xdata()) == 2]
    assert len(series_lines) == 3
    assert list(series_lines[0].get_xdata()) == [0, 1]


def test_bump_assigns_rank_one_to_the_largest(axes: Axes) -> None:
    values = np.array([[10, 10, 10], [5, 5, 5], [1, 1, 1]])
    with cs.theme("margin_call"):
        charts.bump(values, periods=["t1", "t2", "t3"], ax=axes)
    # Series 0 is largest in every period, so its line rides rank 1 throughout.
    assert list(axes.lines[0].get_ydata()) == [1, 1, 1]
    bottom, top = axes.get_ylim()
    assert bottom > top  # y inverted so rank 1 sits on top


def test_underwater_never_rises_above_zero(axes: Axes) -> None:
    rng = np.random.default_rng(5)
    series = np.cumprod(1 + rng.normal(0.01, 0.05, 250))
    with cs.theme("margin_call"):
        charts.underwater(series, ax=axes)
    drawdown = axes.lines[0].get_ydata()
    assert drawdown.max() <= 1e-9  # at a new high it touches zero, never above
    assert drawdown.min() < 0  # and it does go underwater


def test_streamgraph_hides_the_meaningless_axis(axes: Axes) -> None:
    rng = np.random.default_rng(6)
    data = np.abs(rng.normal(3, 1, (4, 30)))
    with cs.theme("there_will_be_blood"):
        charts.streamgraph(data, labels=list("ABCD"), ax=axes)
    assert len([c for c in axes.collections if isinstance(c, PolyCollection)]) == 4
    assert not axes.yaxis.get_visible()  # wiggle baseline has no fixed zero


def test_rolling_corr_heatmap_is_bounded_and_shaped(axes: Axes) -> None:
    rng = np.random.default_rng(7)
    series = rng.normal(size=(120, 4))
    with cs.theme("margin_call"):
        image = charts.rolling_corr_heatmap(series, window=20, ax=axes)
    assert isinstance(image, AxesImage)
    data = image.get_array()
    assert data.shape == (6, 101)  # 4 choose 2 pairs, 120 - 20 + 1 windows
    assert data.min() >= -1.0 and data.max() <= 1.0


def test_mountain_marks_peaks_with_glyphs(axes: Axes) -> None:
    x = np.linspace(0, 6 * np.pi, 300)
    profile = np.abs(np.sin(x)) * np.linspace(1, 3, x.size)
    with cs.theme("the_revenant"):
        charts.mountain(profile, ax=axes, zone=(2.0, 2.5), zone_label="danger")
    glyphs = [c for c in axes.collections if isinstance(c, PathCollection)]
    assert glyphs and len(glyphs[0].get_offsets()) >= 1
    # The receding ranges plus the front ridge are filled areas.
    fills = [c for c in axes.collections if isinstance(c, PolyCollection)]
    assert len(fills) >= 3


def test_sankey_conserves_a_ribbon_per_link(axes: Axes) -> None:
    links = [("A", "X", 5), ("A", "Y", 3), ("B", "X", 2), ("X", "Z", 6)]
    with cs.theme("there_will_be_blood"):
        charts.sankey(links, ax=axes)
    # One patch per node bar plus one per ribbon: 5 nodes + 4 links.
    assert len(axes.patches) == 9
    assert not axes.axison


def test_choropleth_requires_the_geo_extra_or_runs() -> None:
    gpd = pytest.importorskip("geopandas", reason="choropleth needs the [geo] extra")
    from shapely.geometry import box

    gdf = gpd.GeoDataFrame(
        {"value": [1.0, 2.0, 3.0]},
        geometry=[box(0, 0, 1, 1), box(1, 0, 2, 1), box(2, 0, 3, 1)],
    )
    fig, ax = plt.subplots()
    with cs.theme("raiders"):
        charts.choropleth(gdf, "value", ax=ax)
    assert not ax.axison  # a map drops its frame
    assert len(ax.collections) >= 1
    plt.close(fig)
