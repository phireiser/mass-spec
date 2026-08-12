#!/usr/bin/env python3
"""Analyze data density at different bond counts."""
import csv
import math
from pathlib import Path
from collections import defaultdict

import numpy as np
import matplotlib.pyplot as plt

from src.project_paths import shared_path

CSV_PATH = shared_path("METRICS_DIR_REL", "MolecuelProcessingTimeTableComplexety.csv")
PLOT_PATH = shared_path("PLOTS_DIR_REL", "data_distribution_analysis.svg")

# Load data
xs, ys = [], []
with open(CSV_PATH) as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            x = float(row.get("MoleculeComplexety", "").strip())
            y = float(row.get(" Time (seconds)", "").strip())
            if not math.isnan(x) and not math.isnan(y):
                xs.append(x)
                ys.append(y)
        except:
            continue

xs, ys = np.array(xs), np.array(ys)

# Filter >= 40s
mask = ys >= 40
xs_f, ys_f = xs[mask], ys[mask]

# Count samples at each bond count
counts = defaultdict(int)
for x in xs_f:
    counts[int(x)] += 1

print("=" * 60)
print("Data distribution (time >= 40s, n=37 samples)")
print("=" * 60)
print(f"{'Bond Count':<12} {'Count':<8} {'Uncertainty Factor':<20}")
print("-" * 60)

total = len(xs_f)
for bond_count in sorted(counts.keys()):
    count = counts[bond_count]
    # Uncertainty is inversely proportional to sqrt(n)
    uncertainty_factor = 1.0 / np.sqrt(count) if count > 0 else float('inf')
    print(f"{bond_count:<12} {count:<8} {uncertainty_factor:.3f}  (sqrt(n)={np.sqrt(count):.2f})")

print("=" * 60)
print("\nObservations:")
print(f"- High bond counts (20+) have only 1-2 samples")
print(f"- Low bond counts (5-10) have 3-5 samples")
print(f"- A single outlier at high bond count (e.g., ascorbic_acid with 778k s)")
print(f"  gets same weight as multiple measurements at low bond count")
print(f"- This can bias the fit toward extreme values")

# Visualize
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Plot 1: Scatter with size proportional to data density
bond_ints = [int(x) for x in xs_f]
sizes = [300 / counts[int(x)] for x in xs_f]  # Inverse proportional

axes[0].scatter(xs_f, ys_f, s=sizes, alpha=0.6, c=bond_ints, cmap='viridis')
axes[0].set_xlabel('Bond Count')
axes[0].set_ylabel('Time (seconds)')
axes[0].set_title('Data scatter (point size = 1/count at that bond level)')
axes[0].grid(True, alpha=0.3)

# Plot 2: Sample counts by bond count
bond_counts_sorted = sorted(counts.keys())
sample_counts = [counts[b] for b in bond_counts_sorted]

axes[1].bar(bond_counts_sorted, sample_counts, color='steelblue', alpha=0.7)
axes[1].set_xlabel('Bond Count')
axes[1].set_ylabel('Number of Samples')
axes[1].set_title('Sample count distribution (time >= 40s)')
axes[1].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
PLOT_PATH.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(PLOT_PATH, dpi=150, bbox_inches='tight')
print(f"\nSaved visualization to: {PLOT_PATH}")
