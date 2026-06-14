"""Choropleth maps (the ``[geo]`` extra).

A choropleth fills geographic areas by a value. Geometry handling is genuinely
heavy, so this idiom is gated: it needs geopandas and shapely from the ``[geo]``
extra. The drawing itself is thin; the work is letting the active theme's ramps
and chrome carry a filled map, which is a different visual problem from a chart
(no axes, equal aspect, a legend that reads against dark ground).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from matplotlib.axes import Axes

from . import _base

logger = logging.getLogger("cinestyle")

# Natural Earth serves its public-domain vectors from this CDN; the 1:110m
# countries layer is the standard low-detail basemap for a world choropleth.
_NATURAL_EARTH = (
    "https://naturalearth.s3.amazonaws.com/{scale}_cultural/"
    "ne_{scale}_admin_0_countries.zip"
)


def _require_geopandas() -> Any:
    try:
        import geopandas
    except ImportError as exc:  # pragma: no cover - exercised only without extra
        raise ImportError(
            "Choropleths need the optional dependencies geopandas and shapely. "
            "Install them with: pip install 'cinestyle[geo]'"
        ) from exc
    return geopandas


def natural_earth(scale: str = "110m", cache_dir: str | Path | None = None) -> Any:
    """Load the Natural Earth countries layer, downloading and caching it once.

    Natural Earth data is public domain. The first call fetches the zip to a
    cache directory; later calls read it locally.

    Args:
        scale: Map resolution, one of ``"110m"``, ``"50m"``, ``"10m"``.
        cache_dir: Where to cache the download; defaults to a user cache dir.

    Returns:
        A ``GeoDataFrame`` of world countries.
    """
    geopandas = _require_geopandas()
    cache = Path(cache_dir) if cache_dir else Path.home() / ".cache" / "cinestyle"
    cache.mkdir(parents=True, exist_ok=True)
    local = cache / f"ne_{scale}_admin_0_countries.zip"
    if not local.exists():
        from urllib.request import urlretrieve

        url = _NATURAL_EARTH.format(scale=scale)
        logger.info("downloading Natural Earth %s to %s", scale, local)
        urlretrieve(url, local)  # noqa: S310 - fixed, trusted Natural Earth host
    return geopandas.read_file(local)


def choropleth(
    gdf: Any,
    column: str,
    ax: Axes | None = None,
    *,
    cmap: str | None = None,
    scheme: str | None = None,
    legend: bool = True,
    edgecolor: str | None = None,
    missing_color: str | None = None,
) -> Axes:
    """Fill the geometries in *gdf* by *column*, in the active theme's palette.

    Args:
        gdf: A GeoDataFrame.
        column: The column whose values set each area's fill.
        ax: Target axes (defaults to the current axes).
        cmap: Colormap name; defaults to the theme's sequential map.
        scheme: Optional mapclassify scheme (e.g. ``"quantiles"``) for binning.
        legend: Draw a colorbar / legend.
        edgecolor: Border color for the areas; defaults to the theme's muted hue.
        missing_color: Fill for areas with no value; defaults to the muted hue.

    Returns:
        The axes.
    """
    _require_geopandas()
    ax = _base.current_ax(ax)
    colormap = cmap if cmap is not None else _base.sequential_cmap()
    edge = edgecolor if edgecolor is not None else _base.muted()
    missing = missing_color if missing_color is not None else _base.muted()

    gdf.plot(
        column=column,
        ax=ax,
        cmap=colormap,
        scheme=scheme,
        legend=legend,
        edgecolor=edge,
        linewidth=0.4,
        missing_kwds={"color": missing, "label": "no data"},
    )
    # A map is not a chart: equal aspect keeps shapes true, and the lat/lon frame
    # is noise once the fill carries the value.
    ax.set_aspect("equal")
    ax.set_axis_off()
    return ax
