"""Chart-idiom builders: the right picture for the question, in the house style.

Each builder takes tidy data and an axes, applies the active theme, and returns
the axes (or the primary artist where one object is the natural handle). They are
an opt-in layer; a theme alone styles any plot, and these are here for the
idioms matplotlib has no shorthand for.

The two map and flow idioms have heavier needs: :func:`choropleth` requires the
``[geo]`` extra (geopandas, shapely), and :func:`sankey` reads a pandas frame
when given one (the ``[flow]`` extra) though it renders without it.
"""

from __future__ import annotations

from .distribution import beeswarm, hexbin_density, ridgeline
from .flow import sankey
from .geo import choropleth, natural_earth
from .mountain import mountain
from .ranking import bump, dumbbell, lollipop, slope
from .timeseries import rolling_corr_heatmap, streamgraph, underwater

__all__ = [
    "beeswarm",
    "bump",
    "choropleth",
    "dumbbell",
    "hexbin_density",
    "lollipop",
    "mountain",
    "natural_earth",
    "ridgeline",
    "rolling_corr_heatmap",
    "sankey",
    "slope",
    "streamgraph",
    "underwater",
]
