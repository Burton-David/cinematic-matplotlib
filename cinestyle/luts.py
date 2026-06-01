"""Film-look color grades, applicable to image plots and exportable as 3D LUTs.

A :class:`Look` is a parametric color grade -- lift/gamma/gain, saturation, and
a shadow/highlight split-tone (the mechanism behind the cinematic teal-and-orange
grade). It applies to any RGB image array or to an ``imshow`` result, so heatmaps
and image plots can carry the same look as the rest of the theme. A look can also
be baked to a standard ``.cube`` 3D LUT for use in video tools, and external
``.cube`` files can be read back (with the optional ``[luts]`` extra).

Looks are most meaningful for photographic / continuous imagery; on flat-color
bar and line charts a grade has little to act on -- the palette and chrome carry
those. The honest place to reach for a look is ``imshow``/heatmap tone-mapping.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from matplotlib import colors as mcolors
from matplotlib.image import AxesImage

# Rec. 709 luma weights, used for saturation and split-tone blending.
_LUMA = np.array([0.2126, 0.7152, 0.0722])


@dataclass(frozen=True)
class Look:
    """A parametric film-look color grade.

    Attributes:
        name: Identifier (also the default LUT title).
        lift: Added to the (gained) signal -- raises/lowers the floor.
        gamma: Mid-tone curve; >1 brightens mids, <1 darkens.
        gain: Multiplies the signal -- scales the ceiling.
        saturation: 1.0 keeps saturation; <1 mutes; >1 boosts.
        shadow_tint: Color pulled into the shadows.
        highlight_tint: Color pulled into the highlights.
        tint_strength: How strongly the split-tone is applied, in [0, 1].
    """

    name: str
    lift: float = 0.0
    gamma: float = 1.0
    gain: float = 1.0
    saturation: float = 1.0
    shadow_tint: str = "#000000"
    highlight_tint: str = "#FFFFFF"
    tint_strength: float = 0.0

    def apply(self, image: np.ndarray) -> np.ndarray:
        """Apply the grade to an RGB(A) image array with values in [0, 1].

        Args:
            image: Array shaped ``(..., 3)`` or ``(..., 4)``; an alpha channel is
                passed through untouched.

        Returns:
            A new array of the same shape, values clipped to [0, 1].
        """
        arr = np.asarray(image, dtype=float)
        alpha = None
        if arr.shape[-1] == 4:
            alpha = arr[..., 3:]
            arr = arr[..., :3]

        graded = np.clip(arr * self.gain + self.lift, 0.0, 1.0)
        graded = graded ** (1.0 / self.gamma)

        luma = graded @ _LUMA
        graded = luma[..., None] + (graded - luma[..., None]) * self.saturation
        graded = np.clip(graded, 0.0, 1.0)

        if self.tint_strength > 0.0:
            shadow = np.array(mcolors.to_rgb(self.shadow_tint))
            highlight = np.array(mcolors.to_rgb(self.highlight_tint))
            weight = (graded @ _LUMA)[..., None]
            shadow_blend = self.tint_strength * (1.0 - weight)
            highlight_blend = self.tint_strength * weight
            graded = graded * (1.0 - shadow_blend) + shadow * shadow_blend
            graded = graded * (1.0 - highlight_blend) + highlight * highlight_blend

        graded = np.clip(graded, 0.0, 1.0)
        if alpha is not None:
            graded = np.concatenate([graded, alpha], axis=-1)
        return graded

    def apply_to_image(self, image: AxesImage) -> AxesImage:
        """Apply the look to a Matplotlib ``imshow`` result, in place."""
        data = image.get_array()
        if data is None:
            return image
        rgba = image.cmap(image.norm(data)) if data.ndim == 2 else np.asarray(data)
        image.set_data(self.apply(rgba))
        return image

    def to_cube(self, path: str | Path, size: int = 33) -> Path:
        """Bake the look to a standard ``.cube`` 3D LUT file.

        Args:
            path: Output path.
            size: LUT grid resolution per axis (33 is the common default).
        """
        axis = np.linspace(0.0, 1.0, size)
        # .cube ordering: red varies fastest, then green, then blue.
        blue, green, red = np.meshgrid(axis, axis, axis, indexing="ij")
        grid = np.stack([red, green, blue], axis=-1).reshape(-1, 3)
        graded = self.apply(grid)
        target = Path(path)
        lines = [f'TITLE "{self.name}"', f"LUT_3D_SIZE {size}", ""]
        lines += [f"{r:.6f} {g:.6f} {b:.6f}" for r, g, b in graded]
        target.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return target


def read_cube(path: str | Path) -> object:
    """Read an external ``.cube`` 3D LUT (requires the ``[luts]`` extra).

    Returns a :class:`colour.LUT3D` whose ``.apply`` method grades RGB arrays.
    """
    try:
        import colour
    except ImportError as exc:  # pragma: no cover - exercised only without extra
        raise ImportError(
            "Reading external .cube LUTs needs the optional dependency "
            "'colour-science'. Install it with: pip install 'cinestyle[luts]'"
        ) from exc
    return colour.io.read_LUT(str(path))
