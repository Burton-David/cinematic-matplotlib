# cinestyle

[![CI](https://github.com/Burton-David/cinematic-matplotlib/actions/workflows/ci.yml/badge.svg)](https://github.com/Burton-David/cinematic-matplotlib/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linter: ruff](https://img.shields.io/badge/linter-ruff-261230.svg)](https://github.com/astral-sh/ruff)

Cinematic data-viz theming, done with color science. Twenty-four film-inspired
themes that are **beautiful, correct, and accessible**, defined once and applied
to **matplotlib, Plotly, or Altair**, plus an API for defining your own brand.
Same data, cinematic finish:

![Before and after](images/hero_before_after.png)

## Why this exists

Most "pretty matplotlib" packages pick colors by eye and only look right on the
one chart in their README. cinestyle is built differently:

- **Perceptually derived.** Each theme's categorical palette and its sequential
  and diverging colormaps are computed in a perceptual color space (OKLCH /
  CAM02-UCS) from a few sourced "hero" colors, not hand-waved. Sequential maps
  have monotonic lightness; diverging maps are symmetric.
- **One spec, three backends.** Define a theme once and apply it to matplotlib,
  Plotly, or Altair. The palette, the sequential/diverging colormaps, and the
  chrome all travel; you stop caring which plotting library wins.
- **Works on every chart type.** On matplotlib it only sets rcParams and registers
  colormaps. Lines, bars, scatter, hist, boxplots, pies, heatmaps, errorbars:
  all themed. You never switch themes mid-deck.
- **Accessible by design.** `audit()` any palette (or theme) for color-vision
  deficiency and contrast; `repair()` turns it into a colorblind-safe variant.
- **Reproducible.** Themes ship their fonts (SIL OFL), so a matplotlib chart
  looks the same on every machine.
- **Cinematic extras (matplotlib).** A neon glow for the dark themes, and
  film-look LUTs you can apply to image plots and export as `.cube`.

## Install

```bash
pip install git+https://github.com/Burton-David/cinematic-matplotlib.git
```

Optional extras: `cinestyle[plotly]`, `cinestyle[altair]` (the other backends),
`cinestyle[a11y]` (color-vision checks), `cinestyle[luts]` (reading external
`.cube` LUTs). For development: `pip install -e ".[dev]"`. Requires Python 3.10+.

## Quick start

```python
import matplotlib.pyplot as plt
import numpy as np
import cinestyle

x = np.linspace(0, 12, 200)

# 1. Scoped: styling is restored when the block exits
with cinestyle.use("blade_runner"):
    fig, ax = plt.subplots()
    for i in range(4):
        ax.plot(x, np.sin(x + i * 0.6) + i * 0.4)
    cinestyle.add_glow(ax)          # the neon glow

# 2. Registered style sheet: use it like any matplotlib style
cinestyle.register()
plt.style.use("cinestyle-dune")

# 3. The Theme object itself: palette, colormaps, and more
theme = cinestyle.get_theme("ghibli")
plt.imshow(data, cmap=theme.sequential)
```

## Other backends

The same theme drives Plotly and Altair. The palette, colormaps, and chrome
carry over; glow and LUTs stay matplotlib-only.

```python
import cinestyle

# Plotly
cinestyle.register_plotly()
fig.update_layout(template="cinestyle-blade_runner")   # or use_plotly("dune")

# Altair
cinestyle.register_altair(enable="dune")               # enables the theme
```

See [docs/gallery.md](docs/gallery.md) for the same theme rendered across all
three backends side by side.

## Gallery

Every image is regenerated from deterministic data by
`python scripts/generate_gallery.py`. No hand-edited screenshots.

| | |
|---|---|
| ![noir](images/noir.png) | ![ghibli](images/ghibli.png) |
| ![wes_anderson](images/wes_anderson.png) | ![blade_runner](images/blade_runner.png) |
| ![star_wars](images/star_wars.png) | ![matrix](images/matrix.png) |
| ![dune](images/dune.png) | ![fury_road](images/fury_road.png) |
| ![kill_bill](images/kill_bill.png) | ![in_the_mood](images/in_the_mood.png) |
| ![sin_city](images/sin_city.png) | ![akira](images/akira.png) |
| ![the_fall](images/the_fall.png) | ![tron](images/tron.png) |
| ![amelie](images/amelie.png) | ![the_shining](images/the_shining.png) |
| ![drive](images/drive.png) | ![grand_budapest](images/grand_budapest.png) |
| ![nolan](images/nolan.png) | ![hero](images/hero.png) |
| ![suspiria](images/suspiria.png) | ![moonlight](images/moonlight.png) |
| ![blade_runner_2049](images/blade_runner_2049.png) | ![her](images/her.png) |

## The themes

| Theme | Film | Font |
|---|---|---|
| `noir` | Film noir / chiaroscuro | Oswald |
| `ghibli` | Studio Ghibli | EB Garamond |
| `wes_anderson` | Wes Anderson | Jost |
| `blade_runner` | Blade Runner (neon-noir) | Orbitron |
| `star_wars` | Star Wars | Oswald |
| `matrix` | The Matrix | Share Tech Mono |
| `dune` | Dune (Villeneuve) | Space Grotesk |
| `fury_road` | Mad Max: Fury Road | Anton |
| `kill_bill` | Kill Bill | Bebas Neue |
| `in_the_mood` | In the Mood for Love | EB Garamond |
| `sin_city` | Sin City | Anton |
| `akira` | Akira | Orbitron |
| `the_fall` | The Fall (Tarsem) | EB Garamond |
| `tron` | Tron: Legacy | Orbitron |
| `amelie` | Amélie | EB Garamond |
| `the_shining` | The Shining (Kubrick) | Bebas Neue |
| `drive` | Drive | Share Tech Mono |
| `grand_budapest` | The Grand Budapest Hotel | Jost |
| `nolan` | Nolan (Interstellar, Inception) | Space Grotesk |
| `hero` | Hero (Zhang Yimou) | Oswald |
| `suspiria` | Suspiria | Anton |
| `moonlight` | Moonlight | Jost |
| `blade_runner_2049` | Blade Runner 2049 | Orbitron |
| `her` | Her | EB Garamond |

Each `Theme` exposes its `palette`, `sequential` and `diverging` colormaps,
`heroes`, and chrome. `cinestyle.list_themes()` lists them all.

## Color, done right

The palette and colormaps are derived from the hero colors, preserving the
film's mood (hue identity and chroma) while spacing colors perceptually:

```python
theme = cinestyle.get_theme("dune")
theme.palette       # categorical cycle, perceptually separated
theme.sequential    # monotonic-lightness sequential colormap
theme.diverging     # symmetric diverging colormap
```

## Accessibility

`audit()` and `repair()` work on any palette, theme name, or Theme, not just
ours:

```python
cinestyle.audit("blade_runner").summary()   # CIEDE2000 under protan/deutan/tritan + contrast
cinestyle.audit(["#D62728", "#2CA02C"])      # check your own colors
safe = cinestyle.repair("blade_runner")      # a colorblind-safe version
```

![accessibility](images/accessibility.png)

Checks simulate the palette under each color-vision deficiency and flag any pair
that *collapses* (CIEDE2000), plus WCAG non-text contrast against the background.
The repair keeps the film's mood where it can and borrows from known-safe
palettes (Okabe-Ito, Paul Tol) where it must.

## Film looks

```python
look = cinestyle.get_look("teal_orange")
im = ax.imshow(image)
look.apply_to_image(im)          # grade an image plot / heatmap
look.to_cube("teal_orange.cube") # export a 3D LUT for video tools
```

Looks are original parametric grades (lift/gamma/gain, saturation, split-tone).
They matter most for image and heatmap plots; flat bar/line charts are carried
by the palette and chrome.

## Define your own brand

```python
brand = cinestyle.define_brand(
    "acme",
    palette=["#0B5FFF", "#FF6B00", "#00B5AD"],
    background="#FBFBFD",
    foreground="#1A1A2E",
)
with brand.use():
    ...
brand.register()                  # plt.style.use("cinestyle-acme")
brand.to_matplotlibrc("acme.mplstyle")
```

## Development

```bash
pip install -e ".[dev]"
black --check . && ruff check . && mypy cinestyle && pytest
python scripts/generate_gallery.py   # regenerate the gallery
```

Tests run headless (Agg) and assert that styling is actually applied: rcParams
change, artist colors match the palette, colormaps are monotonic/symmetric, the
scoped context restores global state, palettes pass the accessibility checks.

## Credits

cinestyle is an independent, inspired-by tribute and is not affiliated with or
endorsed by any rights holder; film titles are trademarks of their owners. See
[NOTICE.md](NOTICE.md) for palette sources (incl. the `wesanderson` and `ghibli`
palette projects) and bundled-font licenses.

## License

MIT. See [LICENSE](LICENSE).

## Author

David Burton, [databurton.com](https://databurton.com)
