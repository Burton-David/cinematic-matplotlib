"""Tests that the gallery generator stays importable and renders."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

_GALLERY_PATH = (
    Path(__file__).resolve().parent.parent / "scripts" / "generate_gallery.py"
)


def _load_gallery() -> ModuleType:
    spec = importlib.util.spec_from_file_location("cinestyle_gallery", _GALLERY_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_gallery_exposes_all_figures() -> None:
    gallery = _load_gallery()
    assert set(gallery.FIGURES) == {
        "hero_before_after",
        "noir",
        "ghibli",
        "wes_anderson",
        "blade_runner",
        "star_wars",
    }


@pytest.mark.parametrize("name", ["hero_before_after", "noir", "star_wars"])
def test_gallery_renders_nonempty_png(name: str, tmp_path: Path) -> None:
    gallery = _load_gallery()
    path = gallery.render(name, tmp_path, dpi=80)
    assert path.exists()
    assert path.stat().st_size > 0
