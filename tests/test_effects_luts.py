"""Tests for glow path-effects and the film-look LUT engine."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from cinestyle import Look, add_glow
from cinestyle.luts import Look as LookClass


def test_add_glow_attaches_path_effects() -> None:
    fig, ax = plt.subplots()
    (line,) = ax.plot([0, 1, 2], [0, 1, 0])
    assert line.get_path_effects() == []
    add_glow(ax, layers=5)
    effects = line.get_path_effects()
    # Five glow strokes plus the final Normal layer.
    assert len(effects) == 6
    plt.close(fig)


def test_look_apply_changes_image_and_keeps_alpha() -> None:
    look = Look(
        "t",
        saturation=1.4,
        shadow_tint="#003040",
        highlight_tint="#FF8000",
        tint_strength=0.4,
    )
    rng = np.random.default_rng(0)
    rgba = rng.random((8, 8, 4))
    rgba[..., 3] = 0.5
    out = look.apply(rgba)
    assert out.shape == rgba.shape
    assert not np.allclose(out[..., :3], rgba[..., :3])
    assert np.allclose(out[..., 3], 0.5)  # alpha preserved
    assert out.min() >= 0.0 and out.max() <= 1.0


def test_identity_look_is_noop() -> None:
    look = LookClass("identity")  # all defaults -> no change
    img = np.linspace(0, 1, 48).reshape(4, 4, 3)
    assert np.allclose(look.apply(img), img, atol=1e-6)


def test_to_cube_writes_valid_header(tmp_path: object) -> None:
    look = Look(
        "teal_orange",
        shadow_tint="#0E4D64",
        highlight_tint="#E0531F",
        tint_strength=0.3,
    )
    path = look.to_cube(tmp_path / "look.cube", size=17)  # type: ignore[operator]
    text = path.read_text()
    assert "LUT_3D_SIZE 17" in text
    assert text.count("\n") > 17**3  # one rgb line per grid point


def test_apply_to_imshow_result() -> None:
    look = Look("warm", highlight_tint="#F8C457", tint_strength=0.3)
    fig, ax = plt.subplots()
    im = ax.imshow(np.linspace(0, 1, 64).reshape(8, 8))
    before = im.get_array().copy()
    look.apply_to_image(im)
    after = im.get_array()
    assert after.shape[-1] == 4  # became RGBA after grading
    assert not np.allclose(after[..., 0], before)
    plt.close(fig)
