"""Turn a handful of "hero" colors into principled palettes and colormaps.

A film gives us a few signature colors. To be usable in real charts those have
to become (1) a categorical cycle that stays distinguishable for many series,
(2) a sequential colormap with monotonic lightness, and (3) a diverging colormap
with symmetric arms. This module does that conversion in a perceptual color
space rather than by eye.

Design choices, grounded in color science:

* **Construct and interpolate in OKLCH.** It is smooth and hue-stable, so
  ramps do not drift (CIELAB's notorious blue->purple shift) and interpolation
  stays clean.
* **Measure distance with CIEDE2000.** Used to keep categorical colors apart
  and to validate that a sequential ramp steps evenly.
* **Preserve mood by lever priority.** When expanding an aesthetic, keep the
  hero colors' *hue identity* first and their *chroma band* second; re-space
  only *lightness*, the channel that legitimately encodes magnitude. The result
  is principled and still unmistakably the film.

Construction depends only on :mod:`coloraide` (a light, pure-Python dependency),
so themes can derive their palettes at author time or lazily at run time.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

import numpy as np
from coloraide import Color
from matplotlib.colors import Colormap, LinearSegmentedColormap

# Number of samples used to render a colormap to a fixed-size lookup table.
_LUT = 256
_SRGB = "srgb"


def _hex(color: Color) -> str:
    """Gamut-map *color* into sRGB and return an uppercase ``#RRGGBB`` string."""
    return color.convert(_SRGB).fit(_SRGB).to_string(hex=True, upper=True)


def _srgb(color: Color) -> tuple[float, float, float]:
    coords = color.convert(_SRGB).fit(_SRGB)[:-1]
    return (
        float(np.clip(coords[0], 0.0, 1.0)),
        float(np.clip(coords[1], 0.0, 1.0)),
        float(np.clip(coords[2], 0.0, 1.0)),
    )


def _oklch(color: str | Color) -> tuple[float, float, float]:
    """Return the OKLCH (lightness, chroma, hue) of *color*; hue 0 if undefined."""
    c = Color(color).convert("oklch")
    lightness = float(c["lightness"])
    chroma = float(c["chroma"])
    hue = c["hue"]
    return lightness, chroma, 0.0 if math.isnan(hue) else float(hue)


def _oklab_coords(color: Color) -> tuple[float, float, float]:
    lab = color.convert("oklab")
    return float(lab["lightness"]), float(lab["a"]), float(lab["b"])


def lightness(color: str | Color) -> float:
    """Return the OKLCH lightness (0..1) of *color*."""
    return _oklch(color)[0]


def delta_e2000(color1: str | Color, color2: str | Color) -> float:
    """Perceptual CIEDE2000 difference between two colors (0 == identical)."""
    return float(Color(color1).delta_e(Color(color2), method="2000"))


def min_pairwise_delta_e(palette: Sequence[str]) -> float:
    """Smallest CIEDE2000 distance between any two colors in *palette*.

    A larger value means the palette's colors are easier to tell apart; this is
    the core measure behind both categorical quality and colorblind-safety.
    """
    colors = [Color(c) for c in palette]
    if len(colors) < 2:
        return float("inf")
    return min(
        float(colors[i].delta_e(colors[j], method="2000"))
        for i in range(len(colors))
        for j in range(i + 1, len(colors))
    )


def categorical_cycle(
    heroes: Sequence[str],
    n: int,
    *,
    lightness: tuple[float, float] | None = None,
    chroma: tuple[float, float] | None = None,
) -> list[str]:
    """Expand *heroes* into an ``n``-color categorical cycle.

    The hero colors come first and are kept verbatim; additional colors are
    chosen by farthest-point sampling in OKLab (each new color maximizes the
    minimum perceptual distance to those already chosen). Candidates are drawn
    from a "mood box" (the lightness and chroma band of the heroes), so the
    additions stay on-brand while remaining distinguishable.

    Args:
        heroes: The signature colors, as hex strings.
        n: Desired number of colors.
        lightness: Optional ``(min, max)`` OKLCH lightness band; defaults to the
            heroes' own range, gently widened.
        chroma: Optional ``(min, max)`` OKLCH chroma band; defaults to the
            heroes' range.

    Returns:
        ``n`` hex color strings, the first ``len(heroes)`` being the heroes.
    """
    if n <= 0:
        return []
    heroes = list(heroes)
    if n <= len(heroes):
        return [_hex(Color(h)) for h in heroes[:n]]

    profiles = [_oklch(h) for h in heroes]
    ls = [p[0] for p in profiles]
    cs = [p[1] for p in profiles]
    if lightness is not None:
        lo_l, hi_l = lightness
    else:
        lo_l, hi_l = max(0.0, min(ls) - 0.08), min(1.0, max(ls) + 0.08)
        # Guarantee enough lightness spread that even single-hue ("mono") themes
        # yield distinguishable categorical colors; separation a constant-hue
        # palette can only get from lightness.
        if hi_l - lo_l < 0.55:
            mid = (lo_l + hi_l) / 2.0
            lo_l, hi_l = max(0.0, mid - 0.3), min(1.0, mid + 0.3)
    lo_c, hi_c = chroma if chroma else (min(cs), max(max(cs), 0.02))

    # Candidate hues stay within the heroes' own hue family (a window around each
    # hero hue, plus midpoints between them) so additions keep the film's mood.
    # For a single-hue theme this means extensions separate by lightness alone.
    # Candidate hues are sampled only in a window around each hero hue. We do NOT
    # add midpoints between heroes: when hero hues straddle a wide gap (e.g. a
    # red-and-purple palette), the arithmetic midpoint lands on a third,
    # off-mood hue (green), which breaks the film's identity.
    hero_hues = [p[2] for p in profiles]
    window = 22.0
    hues: set[float] = set()
    for hue in hero_hues:
        for offset in np.linspace(-window, window, 5):
            hues.add(round((hue + offset) % 360.0, 2))

    candidates: list[Color] = []
    for light in np.linspace(lo_l, hi_l, 9):
        for chrom in np.linspace(lo_c, hi_c, 4):
            for hue in hues:
                col = Color("oklch", [float(light), float(chrom), float(hue)])
                if col.in_gamut(_SRGB):
                    candidates.append(col)
    if not candidates:
        candidates = [Color(h) for h in heroes]

    chosen = [Color(h) for h in heroes]
    chosen_lab = np.array([_oklab_coords(c) for c in chosen])
    cand_lab = np.array([_oklab_coords(c) for c in candidates])
    used = np.zeros(len(candidates), dtype=bool)

    while len(chosen) < n:
        dists = np.sqrt(
            ((cand_lab[:, None, :] - chosen_lab[None, :, :]) ** 2).sum(axis=2)
        ).min(axis=1)
        dists[used] = -np.inf  # exclude already-chosen candidates from selection
        pick = int(np.argmax(dists))
        used[pick] = True
        chosen.append(candidates[pick])
        chosen_lab = np.vstack([chosen_lab, cand_lab[pick]])

    return [_hex(c) for c in chosen[:n]]


def _ramp(stops: list[Color], name: str) -> LinearSegmentedColormap:
    return LinearSegmentedColormap.from_list(name, [_srgb(c) for c in stops], N=_LUT)


def sequential_cmap(
    anchor: str,
    name: str,
    *,
    light: float = 0.97,
    dark: float = 0.18,
    hue_shift: float = 0.0,
) -> LinearSegmentedColormap:
    """Build a single-hue sequential colormap anchored on *anchor*.

    Lightness decreases monotonically from ``light`` to ``dark`` (the
    correctness criterion for a sequential map) while chroma grows toward the
    dark, saturated end.

    Args:
        anchor: The hue-defining color.
        name: Colormap name.
        light: OKLCH lightness of the low (pale) end.
        dark: OKLCH lightness of the high (saturated) end.
        hue_shift: Optional degrees of hue rotation across the ramp for richness.
    """
    _, chroma, hue = _oklch(anchor)
    stops = []
    for t in np.linspace(0.0, 1.0, 12):
        lightness = light - (light - dark) * t
        chrom = chroma * (0.15 + 0.85 * t)
        stops.append(Color("oklch", [lightness, chrom, hue + hue_shift * t]))
    return _ramp(stops, name)


def diverging_cmap(
    low: str,
    high: str,
    name: str,
    *,
    pivot_lightness: float = 0.95,
    end_lightness: float = 0.32,
) -> LinearSegmentedColormap:
    """Build a diverging colormap between two hero hues.

    Two single-hue arms meet at a pale, near-neutral pivot, with symmetric
    lightness so neither side reads as "heavier". This is the structure behind
    the cinematic teal-and-orange complementary grade.

    Args:
        low: Color of the low end.
        high: Color of the high end.
        name: Colormap name.
        pivot_lightness: OKLCH lightness at the center.
        end_lightness: OKLCH lightness at both saturated ends.
    """
    _, low_c, low_h = _oklch(low)
    _, high_c, high_h = _oklch(high)
    stops = []
    for t in np.linspace(0.0, 1.0, 6):  # low arm: saturated -> pivot
        stops.append(
            Color(
                "oklch",
                [
                    end_lightness + (pivot_lightness - end_lightness) * t,
                    low_c * (1.0 - t),
                    low_h,
                ],
            )
        )
    for t in np.linspace(0.0, 1.0, 6):  # high arm: pivot -> saturated
        stops.append(
            Color(
                "oklch",
                [
                    pivot_lightness - (pivot_lightness - end_lightness) * t,
                    high_c * t,
                    high_h,
                ],
            )
        )
    return _ramp(stops, name)


def lightness_profile(cmap: Colormap, samples: int = _LUT) -> np.ndarray:
    """Return the OKLCH lightness sampled evenly across *cmap*.

    Used to verify that sequential maps are monotonic and diverging maps are
    symmetric: the perceptual-correctness checks for a colormap.
    """
    values = np.linspace(0.0, 1.0, samples)
    out = np.empty(samples)
    for i, v in enumerate(values):
        r, g, b, _ = cmap(float(v))
        out[i] = Color("srgb", [r, g, b]).convert("oklch")["lightness"]
    return out


def is_monotonic_lightness(cmap: Colormap, tolerance: float = 0.02) -> bool:
    """True if *cmap*'s lightness is monotonic within *tolerance* (sequential)."""
    profile = lightness_profile(cmap)
    diffs = np.diff(profile)
    return bool(np.all(diffs <= tolerance) or np.all(diffs >= -tolerance))
