# Cinestyle

A Python library for creating stylized data visualizations inspired by iconic film aesthetics.

## Installation

```bash
pip install cinestyle
```

## Quick Start

```python
import pandas as pd
from cinestyle import WesAnderson, BladeRunner, Ghibli, FilmNoir, StarWars

# Load your data
df = pd.read_csv('movies.csv')

# Create Wes Anderson style visualizations
wa = WesAnderson(df)
wa.plot_timeline()
wa.plot_genre_distribution()
wa.save('anderson_viz')

# Create Blade Runner style visualizations
br = BladeRunner(df)
br.plot_temporal_analysis()
br.plot_genre_matrix()
br.save('cyberpunk_viz')
```

## Styles

- WesAnderson: Symmetrical layouts with pastel colors
- BladeRunner: Cyberpunk aesthetics with neon accents
- Ghibli: Nature-inspired organic visualizations
- FilmNoir: High contrast black and white with dramatic shadows
- StarWars: Space-themed with sci-fi elements

## Requirements

- Python 3.7+
- pandas
- matplotlib
- seaborn
- numpy

## Example Output

![Wes Anderson Style](docs/images/anderson_example.png)
![Blade Runner Style](docs/images/cyberpunk_example.png)

## Contributing

Pull requests welcome. For major changes, open an issue first.