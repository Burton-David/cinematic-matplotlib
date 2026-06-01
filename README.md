# cinestyle

[![CI](https://github.com/Burton-David/cinematic-matplotlib/actions/workflows/ci.yml/badge.svg)](https://github.com/Burton-David/cinematic-matplotlib/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linter: ruff](https://img.shields.io/badge/linter-ruff-261230.svg)](https://github.com/astral-sh/ruff)

Cinematic matplotlib styling inspired by iconic films — Film Noir, Studio Ghibli,
Wes Anderson, Blade Runner, and Star Wars — plus a small API for defining and
reusing your own brand. Same data, cinematic finish:

![Before and after](images/hero_before_after.png)

## Why

Every style is just a bundle of matplotlib rcParams. cinestyle gives you that
bundle three ways — scoped to a `with` block, registered as a named style sheet,
or exported to a `matplotlibrc` file — so styling never leaks into the rest of
your session and a brand you define once works everywhere.

## Install

Not yet on PyPI. Install from the repository:

```bash
pip install git+https://github.com/Burton-David/cinematic-matplotlib.git
```

For development (tests, linters, type checker):

```bash
git clone https://github.com/Burton-David/cinematic-matplotlib.git
cd cinematic-matplotlib
pip install -e ".[dev]"
```

Requires Python 3.10+, matplotlib 3.6+, and numpy 1.23+.

## Quick start

**1. Scoped context manager** — the recommended path; global rcParams are
restored when the block exits:

```python
import matplotlib.pyplot as plt
import numpy as np
from cinestyle import BladeRunner

x = np.linspace(0, 12, 200)
with BladeRunner().use():
    fig, ax = plt.subplots()
    ax.plot(x, np.sin(x))
    ax.plot(x, np.cos(x))
    ax.set_title("CITY SIGNALS")
```

**2. Registered style sheet** — use the styles like any matplotlib style:

```python
import cinestyle
import matplotlib.pyplot as plt

cinestyle.register()                      # adds "cinestyle-noir", "cinestyle-ghibli", ...
plt.style.use("cinestyle-star_wars")
```

**3. Signature plotting helpers** — each style ships distinctive chart types:

```python
from cinestyle import FilmNoir

noir = FilmNoir()
noir.plot_shadows(["Opening", "Betrayal", "Finale"], [6, 8, 7], [3, 8, 5])
```

## Gallery

Every image below is regenerated from deterministic synthetic data by
`python scripts/generate_gallery.py` — there are no hand-edited screenshots.

| | |
|---|---|
| ![Film Noir](images/noir.png) | ![Studio Ghibli](images/ghibli.png) |
| ![Wes Anderson](images/wes_anderson.png) | ![Blade Runner](images/blade_runner.png) |
| ![Star Wars](images/star_wars.png) | |

## The styles

| Style | Look | Signature methods |
|---|---|---|
| `FilmNoir` | High-contrast reds and whites on near-black | `plot_shadows`, `plot_contrast` |
| `Ghibli` | Soft, pastoral palettes; serif type | `plot_landscape`, `plot_flow` |
| `WesAnderson` | Framed, symmetrical layouts in pastels | `plot_symmetry`, `plot_grid` |
| `BladeRunner` | Neon cyan and magenta on deep black | `plot_neon_lines`, `plot_matrix` |
| `StarWars` | Bold gold and blue on pure black | `plot_balance`, `plot_galaxy` |

Each instance exposes its semantic `colors` and the `palette` that drives the
color cycle, and every style provides the common helpers `plot_line`,
`plot_bar`, `plot_scatter`, `plot_histogram`, `plot_heatmap`, and `plot_area`.
Pass an existing `ax=` to style it in place, or omit it to get a fully styled
figure back.

## Define your own brand

A brand is the same rcParams idea, made yours. Describe it once, then scope it,
register it, or export it to a `matplotlibrc` file you can drop into any project.

```python
from cinestyle import define_brand

acme = define_brand(
    "acme",
    palette=["#0B5FFF", "#FF6B00", "#00B5AD"],
    background="#FBFBFD",
    foreground="#1A1A2E",
    grid_color="#E3E3EA",
)

with acme.use():                       # scoped styling
    ...

acme.register()                        # plt.style.use("cinestyle-acme")
acme.to_matplotlibrc("acme.mplstyle")  # reuse it anywhere matplotlib reads styles
```

`Brand.from_matplotlibrc(path)` reads an existing `matplotlibrc` back into a
brand, so the round-trip is lossless.

## Development

```bash
pip install -e ".[dev]"
black --check . && ruff check . && mypy cinestyle && pytest
python scripts/generate_gallery.py    # regenerate the gallery images
```

Tests run headless on the Agg backend and assert that styling is actually
applied — rcParams change, artist colors match the palette, the scoped context
restores global state — not merely that calls don't raise.

## Contributing

Contributions are welcome. Style ideas worth exploring: Tarantino (bold
typography, vintage color), Kubrick (symmetrical, minimal), Nolan (desaturated,
realistic).

## License

MIT — see [LICENSE](LICENSE).

## Author

David Burton — [databurton.com](https://databurton.com)

## Acknowledgments

Inspired by the visual language of Film Noir cinema, the films of Studio Ghibli
and Wes Anderson, Ridley Scott's *Blade Runner*, and the *Star Wars* saga.
