import numpy as np
import matplotlib.pyplot as plt
from cinestyle import FilmNoir, Ghibli, WesAnderson, BladeRunner, StarWars

np.random.seed(42)

print("Testing Cinestyle Library...")
print("=" * 50)

# Test FilmNoir
print("\n1. Testing FilmNoir...")
noir = FilmNoir()
x = np.linspace(0, 10, 100)
y = np.sin(x)
noir.plot_line(x, y)
plt.close()
print("   ✓ Common method (plot_line) works")

categories = ['Scene 1', 'Scene 2', 'Scene 3']
light_vals = [5, 8, 6]
dark_vals = [7, 4, 9]
noir.plot_shadows(categories, light_vals, dark_vals)
plt.close()
print("   ✓ Signature method (plot_shadows) works")

# Test Ghibli
print("\n2. Testing Ghibli...")
ghibli = Ghibli()
data = np.random.randn(50)
ghibli.plot_scatter(x[:50], data)
plt.close()
print("   ✓ Common method (plot_scatter) works")

landscape_data = np.sin(np.linspace(0, 4*np.pi, 100)) * 50 + 50
ghibli.plot_landscape(landscape_data)
plt.close()
print("   ✓ Signature method (plot_landscape) works")

# Test WesAnderson
print("\n3. Testing WesAnderson...")
wes = WesAnderson()
categories = ['A', 'B', 'C', 'D']
values = [10, 15, 7, 12]
wes.plot_bar(categories, values)
plt.close()
print("   ✓ Common method (plot_bar) works")

left_data = [5, 8, 6, 9]
right_data = [7, 4, 8, 5]
wes.plot_symmetry(left_data, right_data)
plt.close()
print("   ✓ Signature method (plot_symmetry) works")

# Test BladeRunner
print("\n4. Testing BladeRunner...")
blade = BladeRunner()
data = np.random.randn(1000)
blade.plot_histogram(data)
plt.close()
print("   ✓ Common method (plot_histogram) works")

signal1 = np.sin(np.linspace(0, 10, 100))
signal2 = np.cos(np.linspace(0, 10, 100))
blade.plot_neon_lines(signal1, signal2)
plt.close()
print("   ✓ Signature method (plot_neon_lines) works")

# Test StarWars
print("\n5. Testing StarWars...")
sw = StarWars()
matrix = np.random.rand(10, 10)
sw.plot_heatmap(matrix)
plt.close()
print("   ✓ Common method (plot_heatmap) works")

factions = ['Jedi', 'Sith', 'Rebels', 'Empire']
faction_vals = [75, 60, 85, 70]
sw.plot_galaxy(factions, faction_vals)
plt.close()
print("   ✓ Signature method (plot_galaxy) works")

print("\n" + "=" * 50)
print("All tests passed successfully! ✓")
print("=" * 50)
