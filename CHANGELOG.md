# Changelog

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and
this project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0]

A v3 that grows cinestyle from a theming library into a cinematic plotting
toolkit, while keeping the styling core pure. Nothing public was removed: existing
theme names, the `Theme` fields, and the function signatures all still work.

### Added

- **Four subject themes**, each a film tuned for a kind of data, with a
  subject-word alias: `margin_call` (`terminal`, markets and P&L),
  `there_will_be_blood` (`petroleum`, oil and energy), `the_revenant`
  (`altitude`, alpine and cold), `raiders` (`atlas`, choropleths and maps). The
  catalog grows from 24 to 28 themes.
- **`cinestyle.charts`**, high-level idiom builders that take tidy data and an
  axes: `beeswarm`, `dumbbell`, `lollipop`, `ridgeline`, `slope`, `bump`,
  `underwater`, `streamgraph`, `hexbin_density`, `rolling_corr_heatmap`, and the
  signature `mountain`. `choropleth` is gated behind the `[geo]` extra and
  `sankey` reads a pandas frame from the `[flow]` extra.
- **`cinestyle.anim`**, an animation engine over `FuncAnimation`: `animate()`
  renders to mp4 (ffmpeg) or gif (Pillow), headless and deterministic, and
  degrades an mp4 to a gif when no ffmpeg is found. Ships four motion presets
  (`ticker`, `flowing`, `ascending`, `map_fill`, one per subject theme) and the
  reveal helpers `progress`, `tween`, `count_up`, `reveal_line`, `grow_bars`.
- **Editorial scaffolding** in the top-level API: `finish` (finding-driven title,
  subtitle, source line, despined), `despine`, `value_labels`, `thousands`,
  `currency`, `save` (300 dpi, tight, parents made), and `lint_text` (flags em and
  en dashes in figure text).
- `Theme.motion`, a default animation preset per theme.
- `theme(name)` context manager, `THEME_ALIASES`, and the subject-word aliases
  resolving through `get_theme`, `apply`, and `use`.
- Extras `[geo]` (geopandas, shapely, mapclassify), `[flow]` (pandas), and
  `[anim]` (imageio-ffmpeg, which supplies an ffmpeg binary for mp4).

### Changed

- `add_glow` now accepts a single artist or a whole axes as its first argument,
  so you can spotlight one hero element; defaults are `intensity=0.4`, `layers=5`.

## [0.2.0]

- Twenty-four film themes with a perceptual color engine (OKLCH, CIEDE2000),
  colorblind-safety auditing and repair, film-look LUTs, a neon glow, bundled OFL
  fonts, and Plotly and Altair adapters from one theme spec.
