#!/usr/bin/env python3
"""Render the multi-backend proof gallery.

One theme spec drives three plotting libraries: matplotlib (native), Plotly,
and Altair. These figures are the visible proof that the same theme produces a
matching look across all three. Every figure is built from a fixed seed so
running ``python scripts/multibackend_gallery.py`` recreates the committed PNGs.

Plotly export uses kaleido (``fig.write_image``) and Altair export uses
vl-convert (``chart.save``); both run headless. The bundled display fonts
(Orbitron and friends) are only loaded into matplotlib, so the Plotly and
Altair renderers fall back to a system sans font for text. That is expected:
the proof is the palette, background, and grid, which match across backends.
"""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import altair as alt  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import plotly.graph_objects as go  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

import cinestyle as cs  # noqa: E402

SEED = 19
_IMAGES_DIR = Path(__file__).resolve().parent.parent / "images"

# Shared figure geometry so the three backends montage cleanly. Pixel sizes are
# matched by rendering matplotlib at the same point size and DPI used here.
_THUMB_W = 460
_THUMB_H = 340
_DPI = 100

# The hero and strip use plain ASCII labels because the Plotly and Altair text
# falls back to a system font; ASCII keeps that fallback legible.
_SERIES = ("alpha", "beta", "gamma")


def _line_data() -> pd.DataFrame:
    """Three deterministic cumulative-walk series shared by every backend."""
    rng = np.random.default_rng(SEED)
    x = np.arange(12)
    rows: list[dict[str, float | int | str]] = []
    for i, name in enumerate(_SERIES):
        y = np.cumsum(rng.normal(0.0, 1.0, x.size)) + i * 3.0
        for xi, yi in zip(x, y, strict=True):
            rows.append({"x": int(xi), "value": float(yi), "series": name})
    return pd.DataFrame(rows)


def _mpl_thumb(
    theme_name: str, df: pd.DataFrame, *, glow: bool, title: str | None = None
) -> Image.Image:
    """Render the shared line chart in native matplotlib for *theme_name*."""
    theme = cs.get_theme(theme_name)
    with cs.use(theme_name):
        fig, ax = plt.subplots(figsize=(_THUMB_W / _DPI, _THUMB_H / _DPI))
        for name in _SERIES:
            sub = df[df["series"] == name]
            ax.plot(sub["x"], sub["value"], linewidth=2.4, label=name)
        # Glow is a matplotlib-only effect; the other backends cannot reproduce
        # it, so it stays off for the side-by-side strip to keep the comparison
        # fair, and on only for the hero where matplotlib is allowed to shine.
        if glow and theme.glow:
            cs.add_glow(ax, intensity=theme.glow)
        if title:
            ax.set_title(title)
        ax.set_xlabel("week")
        ax.set_ylabel("value")
        ax.legend(loc="upper left", fontsize=8)
        fig.tight_layout()
        img = _fig_to_image(fig)
        plt.close(fig)
    return img


def _plotly_thumb(theme_name: str, df: pd.DataFrame, tmp: Path) -> Image.Image:
    """Render the shared line chart in Plotly using the registered template."""
    fig = go.Figure()
    for name in _SERIES:
        sub = df[df["series"] == name]
        fig.add_trace(go.Scatter(x=sub["x"], y=sub["value"], mode="lines", name=name))
    fig.update_layout(
        template=f"cinestyle-{theme_name}",
        width=_THUMB_W,
        height=_THUMB_H,
        margin={"l": 50, "r": 20, "t": 20, "b": 40},
    )
    fig.update_xaxes(title_text="week")
    fig.update_yaxes(title_text="value")
    out = tmp / f"plotly_{theme_name}.png"
    fig.write_image(out, scale=1)
    return _open_resized(out)


def _altair_thumb(theme_name: str, df: pd.DataFrame, tmp: Path) -> Image.Image:
    """Render the shared line chart in Altair using the registered theme."""
    alt.theme.enable(f"cinestyle-{theme_name}")
    chart = (
        alt.Chart(df)
        .mark_line(strokeWidth=2.4)
        .encode(
            x=alt.X("x:Q", title="week"),
            y=alt.Y("value:Q", title="value"),
            color=alt.Color("series:N", title=None),
        )
        # Reserve room so the legend and axis titles are not clipped, then let
        # the montage step normalize every thumbnail to the same pixel box.
        .properties(width=_THUMB_W - 150, height=_THUMB_H - 90)
    )
    out = tmp / f"altair_{theme_name}.png"
    chart.save(out, ppi=_DPI)
    return _open_resized(out)


def _fig_to_image(fig: Figure) -> Image.Image:
    """Rasterize a matplotlib figure to a Pillow image at the shared box size."""
    fig.set_dpi(_DPI)
    fig.canvas.draw()
    data, (w, h) = fig.canvas.print_to_buffer()  # type: ignore[attr-defined]
    img = Image.frombuffer("RGBA", (w, h), data, "raw", "RGBA", 0, 1)
    return _resize_box(img.convert("RGB"))


def _open_resized(path: Path) -> Image.Image:
    return _resize_box(Image.open(path).convert("RGB"))


def _resize_box(img: Image.Image) -> Image.Image:
    """Fit an image into the shared thumbnail box, padding with its own corner.

    Padding uses the top-left pixel so the fill matches each theme background
    instead of forcing a generic color that would break dark or light themes.
    """
    if img.size == (_THUMB_W, _THUMB_H):
        return img
    bg = img.getpixel((0, 0))
    canvas = Image.new("RGB", (_THUMB_W, _THUMB_H), bg)
    scale = min(_THUMB_W / img.width, _THUMB_H / img.height)
    resized = img.resize(
        (max(1, int(img.width * scale)), max(1, int(img.height * scale))),
        Image.LANCZOS,
    )
    canvas.paste(
        resized,
        ((_THUMB_W - resized.width) // 2, (_THUMB_H - resized.height) // 2),
    )
    return canvas


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in (
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def _label_strip(width: int, text: str, *, height: int = 34) -> Image.Image:
    """A dark caption band with centered white text, used above thumbnails."""
    band = Image.new("RGB", (width, height), "#101218")
    draw = ImageDraw.Draw(band)
    font = _font(20)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(
        ((width - tw) // 2, (height - th) // 2 - bbox[1]),
        text,
        fill="#E9E9F0",
        font=font,
    )
    return band


def _row_label(text: str, *, width: int = 150, height: int = _THUMB_H) -> Image.Image:
    """A left-hand label cell naming the theme for a strip row."""
    cell = Image.new("RGB", (width, height), "#101218")
    draw = ImageDraw.Draw(cell)
    font = _font(22)
    bbox = draw.textbbox((0, 0), text, font=font)
    th = bbox[3] - bbox[1]
    draw.text((16, (height - th) // 2 - bbox[1]), text, fill="#E9E9F0", font=font)
    return cell


def _hconcat(images: list[Image.Image], *, gap: int = 8) -> Image.Image:
    """Concatenate images horizontally on a dark gutter."""
    height = max(im.height for im in images)
    width = sum(im.width for im in images) + gap * (len(images) - 1)
    strip = Image.new("RGB", (width, height), "#101218")
    x = 0
    for im in images:
        strip.paste(im, (x, 0))
        x += im.width + gap
    return strip


def _vconcat(images: list[Image.Image], *, gap: int = 8) -> Image.Image:
    """Concatenate images vertically on a dark gutter."""
    width = max(im.width for im in images)
    height = sum(im.height for im in images) + gap * (len(images) - 1)
    strip = Image.new("RGB", (width, height), "#101218")
    y = 0
    for im in images:
        strip.paste(im, (0, y))
        y += im.height + gap
    return strip


def _captioned(thumb: Image.Image, caption: str) -> Image.Image:
    return _vconcat([_label_strip(thumb.width, caption), thumb], gap=0)


def hero(tmp: Path) -> Image.Image:
    """Same blade_runner chart in matplotlib, Plotly, and Altair, side by side."""
    df = _line_data()
    cells = [
        _captioned(_mpl_thumb("blade_runner", df, glow=True), "matplotlib"),
        _captioned(_plotly_thumb("blade_runner", df, tmp), "Plotly"),
        _captioned(_altair_thumb("blade_runner", df, tmp), "Altair"),
    ]
    return _hconcat(cells)


def strip(tmp: Path) -> Image.Image:
    """Three themes, each a row of matplotlib | Plotly | Altair thumbnails."""
    df = _line_data()
    rows = []
    # One dark neon, one light, one muted: proves the spec generalizes.
    for theme_name in ("tron", "dune", "nolan"):
        thumbs = [
            _mpl_thumb(theme_name, df, glow=False),
            _plotly_thumb(theme_name, df, tmp),
            _altair_thumb(theme_name, df, tmp),
        ]
        rows.append(_hconcat([_row_label(theme_name), *thumbs]))
    header_cells = ["", "matplotlib", "Plotly", "Altair"]
    widths = [150, _THUMB_W, _THUMB_W, _THUMB_W]
    header = _hconcat(
        [_label_strip(w, t) for w, t in zip(widths, header_cells, strict=True)]
    )
    return _vconcat([header, *rows])


def accessibility_audit() -> Figure:
    """Prove audit and repair: original vs deuteranopia vs colorblind-safe.

    'her' is chosen because its warm palette collapses to near-identical olive
    tones under deuteranopia (min CIEDE2000 well under the safe threshold),
    which makes the repair an honest, visible improvement rather than cosmetic.
    """
    theme_name = "her"
    theme = cs.get_theme(theme_name)
    original = list(theme.palette)
    simulated = cs.accessibility.simulate_palette(original, "deutan")
    repaired = cs.repair(theme_name)
    report = cs.audit(theme_name)

    rows = (
        (original, f"{theme_name} palette (original)"),
        (simulated, "same palette as a deuteranope sees it"),
        (repaired, "cs.repair() output (colorblind safe)"),
    )
    fig, axes = plt.subplots(3, 1, figsize=(9.5, 5.2), facecolor="#101218")
    for ax, (palette, label) in zip(axes, rows, strict=True):
        for i, hex_color in enumerate(palette):
            ax.add_patch(plt.Rectangle((i, 0), 1, 1, facecolor=hex_color))
        ax.set_xlim(0, len(palette))
        ax.set_ylim(0, 1)
        ax.set_title(label, color="#E9E9F0", fontsize=12, loc="left")
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_facecolor("#101218")
        for spine in ax.spines.values():
            spine.set_visible(False)

    deutan = report.cvd_min_delta_e["deutan"]
    safe_deutan = cs.audit(repaired).cvd_min_delta_e["deutan"]
    fig.suptitle(
        f"cs.audit('{theme_name}'): deuteranopia min delta E {deutan:.1f} "
        f"(unsafe), repaired to {safe_deutan:.1f}",
        color="#E9E9F0",
        fontsize=13,
        fontweight="bold",
    )
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    return fig


def render_all(outdir: Path) -> list[Path]:
    """Render every proof figure into *outdir* and return the written paths."""
    outdir.mkdir(parents=True, exist_ok=True)
    cs.register_plotly()
    cs.register_altair()
    written: list[Path] = []
    with tempfile.TemporaryDirectory() as tmp_name:
        tmp = Path(tmp_name)
        hero_path = outdir / "multibackend_hero.png"
        hero(tmp).save(hero_path)
        written.append(hero_path)

        strip_path = outdir / "multibackend_strip.png"
        strip(tmp).save(strip_path)
        written.append(strip_path)

    audit_path = outdir / "accessibility_audit.png"
    fig = accessibility_audit()
    fig.savefig(
        audit_path,
        dpi=130,
        facecolor=fig.get_facecolor(),
        metadata={"Software": "cinestyle"},
    )
    plt.close(fig)
    written.append(audit_path)
    return written


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render the cinestyle multi-backend proof gallery."
    )
    parser.add_argument("-o", "--outdir", type=Path, default=_IMAGES_DIR)
    args = parser.parse_args()
    for path in render_all(args.outdir):
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
