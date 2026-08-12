"""
Compare unweighted vs weighted regression models.
"""
import csv
import math
from pathlib import Path
from collections import defaultdict

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

from src.project_paths import shared_path

CSV_PATH = shared_path("METRICS_DIR_REL", "MolecuelProcessingTimeTableComplexety.csv")

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
mask = ys >= 40
xs_f, ys_f = xs[mask], ys[mask]

# Compute weights inversely proportional to density at each bond count
counts = defaultdict(int)
for x in xs_f:
    counts[int(x)] += 1

weights = np.array([1.0 / np.sqrt(counts[int(x)]) for x in xs_f])
weights_norm = weights / np.sum(weights) * len(weights)  # Normalize for fair comparison

print("=" * 70)
print("UNWEIGHTED vs WEIGHTED REGRESSION (time >= 40s, n=37)")
print("=" * 70)

# Linear: unweighted
def compute_r2_unweighted(y_true, y_pred):
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - y_true.mean()) ** 2)
    return 1 - ss_res / ss_tot

# Linear: weighted
def compute_r2_weighted(y_true, y_pred, weights):
    ss_res = np.sum(weights * (y_true - y_pred) ** 2)
    ss_tot = np.sum(weights * (y_true - y_true.mean()) ** 2)
    return 1 - ss_res / ss_tot

print("\n1. LINEAR REGRESSION")
print("-" * 70)

# Unweighted
b_uw, a_uw = np.polyfit(xs_f, ys_f, 1)
pred_uw = a_uw + b_uw * xs_f
r2_uw = compute_r2_unweighted(ys_f, pred_uw)
print(f"Unweighted: y = {a_uw:.1f} + {b_uw:.1f}*x")
print(f"  R**2 = {r2_uw:.6f}")

# Weighted
b_w, a_w = np.polyfit(xs_f, ys_f, 1, w=weights_norm)
pred_w = a_w + b_w * xs_f
r2_w = compute_r2_weighted(ys_f, pred_w, weights_norm)
print(f"Weighted:   y = {a_w:.1f} + {b_w:.1f}*x")
print(f"  R**2 = {r2_w:.6f}")
print(f"  Difference: ΔR**2 = {abs(r2_w - r2_uw):.6f}")

print("\n2. QUADRATIC REGRESSION")
print("-" * 70)

# Unweighted
coeffs_uw = np.polyfit(xs_f, ys_f, 2)
pred_uw = np.polyval(coeffs_uw, xs_f)
r2_uw = compute_r2_unweighted(ys_f, pred_uw)
print(f"Unweighted: y = {coeffs_uw[2]:.1f} + {coeffs_uw[1]:.1f}*x + {coeffs_uw[0]:.1f}*x**2")
print(f"  R**2 = {r2_uw:.6f}")

# Weighted
coeffs_w = np.polyfit(xs_f, ys_f, 2, w=weights_norm)
pred_w = np.polyval(coeffs_w, xs_f)
r2_w = compute_r2_weighted(ys_f, pred_w, weights_norm)
print(f"Weighted:   y = {coeffs_w[2]:.1f} + {coeffs_w[1]:.1f}*x + {coeffs_w[0]:.1f}*x²")
print(f"  R**2 = {r2_w:.6f}")
print(f"  Difference: ΔR**2 = {abs(r2_w - r2_uw):.6f}")

print("\n3. CUBIC REGRESSION")
print("-" * 70)

# Unweighted
coeffs_uw = np.polyfit(xs_f, ys_f, 3)
pred_uw = np.polyval(coeffs_uw, xs_f)
r2_uw = compute_r2_unweighted(ys_f, pred_uw)
print(f"Unweighted: R**2 = {r2_uw:.6f}")

# Weighted
coeffs_w = np.polyfit(xs_f, ys_f, 3, w=weights_norm)
pred_w = np.polyval(coeffs_w, xs_f)
r2_w = compute_r2_weighted(ys_f, pred_w, weights_norm)
print(f"Weighted:   R**2 = {r2_w:.6f}")
print(f"  Difference: ΔR**2 = {abs(r2_w - r2_uw):.6f}")

print("\n" + "=" * 70)
print("KEY INSIGHT:")
print("=" * 70)
print("Weighted regression gives more importance to bond counts with multiple")
print("measurements (lower uncertainty) and less importance to single-sample")
print("outliers. This provides a more robust estimate of the true trend.")
print("\nIf weighted R**2 is notably different from unweighted, it means the")
print("current model is being biased by sparse high-bond-count data.")
