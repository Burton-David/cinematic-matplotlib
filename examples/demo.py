import matplotlib.pyplot as plt
import numpy as np
from cinestyle import FilmNoir, Ghibli, WesAnderson, BladeRunner, StarWars

data = np.random.randn(100)

noir = FilmNoir()
noir.apply_style()
fig, ax = plt.subplots(figsize=(10, 6))
noir.style_axes(ax)
ax.hist(data, bins=20, color=noir.colors['primary'], alpha=0.8)
ax.set_title("FILM NOIR DISTRIBUTION", fontsize=16, fontweight='bold')
ax.set_xlabel("Value")
ax.set_ylabel("Frequency")
plt.savefig('noir_demo.png', dpi=300, bbox_inches='tight')
plt.close()

ghibli = Ghibli()
ghibli.apply_style()
fig, ax = plt.subplots(figsize=(10, 6))
ghibli.style_axes(ax)
ax.plot(data, color=ghibli.colors['forest'], linewidth=2)
ax.set_title("Flowing Data", fontsize=16)
ax.set_xlabel("Index")
ax.set_ylabel("Value")
plt.savefig('ghibli_demo.png', dpi=300, bbox_inches='tight')
plt.close()

wes = WesAnderson()
wes.apply_style()
fig, ax = plt.subplots(figsize=(10, 6))
wes.style_axes(ax)
categories = ['A', 'B', 'C', 'D']
values = [23, 45, 56, 78]
ax.barh(categories, values, color=wes.palette[:4])
ax.set_title("Symmetrical Analysis", fontsize=16)
plt.savefig('wes_anderson_demo.png', dpi=300, bbox_inches='tight')
plt.close()

blade = BladeRunner()
blade.apply_style()
fig, ax = plt.subplots(figsize=(10, 6))
blade.style_axes(ax)
x = np.linspace(0, 10, 100)
y1 = np.sin(x)
y2 = np.cos(x)
ax.plot(x, y1, color=blade.colors['neon_cyan'], linewidth=2, label='Signal A')
ax.plot(x, y2, color=blade.colors['neon_magenta'], linewidth=2, label='Signal B')
ax.set_title("CYBERPUNK WAVEFORMS", fontsize=16, fontweight='bold')
ax.legend()
plt.savefig('blade_runner_demo.png', dpi=300, bbox_inches='tight')
plt.close()

starwars = StarWars()
starwars.apply_style()
fig, ax = plt.subplots(figsize=(10, 6))
starwars.style_axes(ax)
sides = ['Light', 'Dark']
power = [85, 92]
ax.bar(sides, power, color=[starwars.colors['light_side'], starwars.colors['dark_side']])
ax.set_title("THE FORCE BALANCE", fontsize=16, fontweight='bold')
ax.set_ylabel("Power Level")
plt.savefig('star_wars_demo.png', dpi=300, bbox_inches='tight')
plt.close()

print("All demos created successfully!")
