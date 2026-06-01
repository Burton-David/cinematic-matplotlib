"""Check and repair palettes for color-vision deficiency and contrast.

Cinematic palettes are chosen for mood; this module makes them defensible. It
simulates a palette under the common CVD types and measures whether any two
colors *collapse* (become perceptually close) under that simulation, which is
exactly what "colorblind-safe" guards against. It also checks WCAG non-text
contrast against the theme background, and can synthesize a colorblind-safe
variant that stays as close to the original as possible.

Distinguishing data colors is a perceptual-distance question (CIEDE2000 after
CVD simulation), not a luminance-contrast one; WCAG ratios answer the
different question of whether an element is legible against its background.

Simulation uses :mod:`daltonlens` (the ``[a11y]`` extra): Machado (2009) for
protan/deutan, Brettel (1997) for tritan, which the Machado model does not cover
well. Perceptual distance uses CIEDE2000 from :mod:`cinestyle.color`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from coloraide import Color
from matplotlib import colors as mcolors

from .color import delta_e2000

# Red-green CVD affects ~8% of men; protan/deutan therefore matter most. These
# are known colorblind-safe donor palettes (Okabe-Ito, then Paul Tol "bright"),
# used to fill in when an original color cannot be kept safely.
OKABE_ITO: tuple[str, ...] = (
    "#E69F00",
    "#56B4E9",
    "#009E73",
    "#F0E442",
    "#0072B2",
    "#D55E00",
    "#CC79A7",
    "#000000",
)
TOL_BRIGHT: tuple[str, ...] = (
    "#4477AA",
    "#EE6677",
    "#228833",
    "#CCBB44",
    "#66CCEE",
    "#AA3377",
    "#BBBBBB",
)
_SAFE_DONORS: tuple[str, ...] = OKABE_ITO[:-1] + TOL_BRIGHT

_DEFICIENCIES = ("protan", "deutan", "tritan")

# Default CIEDE2000 separation a palette must keep under simulation to count as
# safe. Red-green (protan/deutan) deficiencies are common (~8% of men), so they
# get the real bar; tritan is vanishingly rare (~0.003%) and harder for any
# palette (even Okabe-Ito drops to ~8 under it), so it gets a lenient bar.
DEFAULT_THRESHOLD = 11.0
TRITAN_THRESHOLD = 8.0


def _bar(deficiency: str, threshold: float, tritan_threshold: float) -> float:
    return tritan_threshold if deficiency == "tritan" else threshold


def _require_daltonlens() -> Any:
    try:
        from daltonlens import simulate
    except ImportError as exc:  # pragma: no cover - exercised only without extra
        raise ImportError(
            "Color-vision simulation needs the optional dependency 'daltonlens'. "
            "Install it with: pip install 'cinestyle[a11y]'"
        ) from exc
    return simulate


def simulate_palette(
    palette: list[str], deficiency: str, severity: float = 1.0
) -> list[str]:
    """Return *palette* as seen under a color-vision deficiency.

    Args:
        palette: Hex colors.
        deficiency: One of ``"protan"``, ``"deutan"``, ``"tritan"``.
        severity: 0 (none) to 1 (full dichromacy).
    """
    simulate = _require_daltonlens()
    rgb = np.array([mcolors.to_rgb(c) for c in palette])
    image = (rgb.reshape(1, -1, 3) * 255).astype(np.uint8)
    if deficiency == "tritan":
        simulator = simulate.Simulator_Brettel1997()
        kind = simulate.Deficiency.TRITAN
    else:
        simulator = simulate.Simulator_Machado2009()
        kind = (
            simulate.Deficiency.PROTAN
            if deficiency == "protan"
            else simulate.Deficiency.DEUTAN
        )
    out = simulator.simulate_cvd(image, kind, severity=severity)
    flat = out.reshape(-1, 3) / 255.0
    return [mcolors.to_hex(c) for c in flat]


def relative_luminance(color: str) -> float:
    """WCAG relative luminance of an sRGB color."""
    channels = []
    for c in mcolors.to_rgb(color):
        channels.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
    r, g, b = channels
    return float(0.2126 * r + 0.7152 * g + 0.0722 * b)


def contrast_ratio(color1: str, color2: str) -> float:
    """WCAG contrast ratio between two colors (1.0 to 21.0)."""
    lum1, lum2 = relative_luminance(color1), relative_luminance(color2)
    lighter, darker = max(lum1, lum2), min(lum1, lum2)
    return (lighter + 0.05) / (darker + 0.05)


def _min_delta_e_with_pair(palette: list[str]) -> tuple[float, tuple[int, int]]:
    best = float("inf")
    pair = (0, 0)
    for i in range(len(palette)):
        for j in range(i + 1, len(palette)):
            d = delta_e2000(palette[i], palette[j])
            if d < best:
                best, pair = d, (i, j)
    return best, pair


@dataclass
class AccessibilityReport:
    """Result of :func:`check_accessibility`.

    Attributes:
        safe: True if the palette stays distinguishable under every tested CVD
            type and (if a background was given) meets non-text contrast.
        threshold: The CIEDE2000 collapse threshold used.
        normal_min_delta_e: Minimum pairwise CIEDE2000 in normal vision.
        cvd_min_delta_e: Minimum pairwise CIEDE2000 per deficiency.
        collapsing_pairs: Per deficiency, the closest pair (palette indices).
        min_contrast: Smallest contrast ratio vs the background (if given).
        low_contrast_indices: Palette indices below 3:1 contrast.
    """

    safe: bool
    threshold: float
    normal_min_delta_e: float
    cvd_min_delta_e: dict[str, float]
    collapsing_pairs: dict[str, tuple[int, int]]
    min_contrast: float | None = None
    low_contrast_indices: list[int] = field(default_factory=list)

    def summary(self) -> str:
        verdict = "SAFE" if self.safe else "AT RISK"
        worst = (
            min(self.cvd_min_delta_e.values()) if self.cvd_min_delta_e else float("inf")
        )
        lines = [
            f"Accessibility: {verdict} (CIEDE2000 threshold {self.threshold:g})",
            f"  normal-vision min ΔE: {self.normal_min_delta_e:.1f}",
            f"  worst CVD min ΔE:     {worst:.1f}",
        ]
        for kind, value in self.cvd_min_delta_e.items():
            flag = "" if value >= self.threshold else "  <- collapses"
            lines.append(f"    {kind:7s}: {value:.1f}{flag}")
        if self.min_contrast is not None:
            lines.append(f"  min contrast vs background: {self.min_contrast:.2f}:1")
        return "\n".join(lines)


def check_accessibility(
    palette: list[str],
    background: str | None = None,
    threshold: float = DEFAULT_THRESHOLD,
    tritan_threshold: float = TRITAN_THRESHOLD,
    contrast_min: float = 3.0,
) -> AccessibilityReport:
    """Assess a palette for colorblind-safety and (optionally) contrast.

    Args:
        palette: Hex colors to assess.
        background: If given, each color's WCAG contrast against it is checked
            (non-text 3:1 by default).
        threshold: Minimum acceptable CIEDE2000 between any two colors under
            red-green (protan/deutan) simulation. ~11 is a sound categorical
            bar (the Okabe-Ito reference clears it).
        tritan_threshold: The (more lenient) bar for the rare tritan deficiency.
        contrast_min: Minimum acceptable contrast ratio vs the background.

    Returns:
        An :class:`AccessibilityReport`.
    """
    normal_min, _ = _min_delta_e_with_pair(palette)
    cvd_min: dict[str, float] = {}
    pairs: dict[str, tuple[int, int]] = {}
    for deficiency in _DEFICIENCIES:
        simulated = simulate_palette(palette, deficiency)
        value, pair = _min_delta_e_with_pair(simulated)
        cvd_min[deficiency] = value
        pairs[deficiency] = pair

    min_contrast: float | None = None
    low_contrast: list[int] = []
    if background is not None:
        ratios = [contrast_ratio(c, background) for c in palette]
        min_contrast = min(ratios)
        low_contrast = [i for i, r in enumerate(ratios) if r < contrast_min]

    safe = (
        all(cvd_min[d] >= _bar(d, threshold, tritan_threshold) for d in _DEFICIENCIES)
        and not low_contrast
    )
    return AccessibilityReport(
        safe=safe,
        threshold=threshold,
        normal_min_delta_e=normal_min,
        cvd_min_delta_e=cvd_min,
        collapsing_pairs=pairs,
        min_contrast=min_contrast,
        low_contrast_indices=low_contrast,
    )


def _lightness(color: str) -> float:
    return float(Color(color).convert("oklch")["lightness"])


def _cvd_safe_against(
    candidate: str, accepted: list[str], threshold: float, tritan_threshold: float
) -> bool:
    if not accepted:
        return True
    for deficiency in _DEFICIENCIES:
        bar = _bar(deficiency, threshold, tritan_threshold)
        simulated = simulate_palette([*accepted, candidate], deficiency)
        cand_sim = simulated[-1]
        if any(delta_e2000(cand_sim, other) < bar for other in simulated[:-1]):
            return False
    return True


def accessible_variant(
    palette: list[str],
    threshold: float = DEFAULT_THRESHOLD,
    tritan_threshold: float = TRITAN_THRESHOLD,
) -> list[str]:
    """Return a colorblind-safe palette the same length as *palette*.

    A color is accepted only if it stays distinct from every color already
    chosen under each CVD type, so the result is safe by construction: nothing
    is ever padded in unchecked (the bug that let an unsafe palette be reported
    safe). Original colors are kept where they survive; the rest come from
    known-safe donors (Okabe-Ito, Paul Tol). If kept originals leave it short of
    the target, it rebuilds from the donors alone, which can always supply a safe
    set of up to eight colors. The result is lightness-ordered so it also
    degrades gracefully to grayscale and print.
    """
    target = len(palette)

    def fill(pool: list[str]) -> list[str]:
        chosen: list[str] = []
        for candidate in pool:
            if len(chosen) >= target:
                break
            if candidate not in chosen and _cvd_safe_against(
                candidate, chosen, threshold, tritan_threshold
            ):
                chosen.append(candidate)
        return chosen

    accepted = fill([*palette, *_SAFE_DONORS])
    if len(accepted) < target:
        # Kept originals can block donors; rebuild from the donors alone, now
        # including Okabe-Ito's black so eight mutually distinct colors exist.
        accepted = fill([*OKABE_ITO, *TOL_BRIGHT])
    accepted.sort(key=_lightness)
    return accepted
