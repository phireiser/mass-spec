#!/usr/bin/env python3
"""Plot computation time vs. molecule bond count with weighted regression.

- Reads MolecuelProcessingTimeTableComplexety.csv
- Computes weighted linear and cubic regressions (weights inversely proportional to data density)
- Saves scatter plot with fitted lines to outputs/plots/time_vs_complexity.png
- Accounts for varying uncertainty in sparse vs dense bond count regions
"""
from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import List, Tuple
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = ROOT / "outputs" / "metrics" / "MolecuelProcessingTimeTableComplexety.csv"
PLOT_DIR = ROOT / "outputs" / "plots"
PLOT_PATH = PLOT_DIR / "time_vs_complexity.png"
PLOT_PATH_OVER40 = PLOT_DIR / "time_vs_complexity_over40.png"
PLOT_PATH_LOGY = PLOT_DIR / "time_vs_complexity_logy.png"
PLOT_PATH_LOGY_OVER40 = PLOT_DIR / "time_vs_complexity_logy_over40.png"


def load_points(csv_path: Path) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    xs: List[float] = []
    ys: List[float] = []
    names: List[str] = []
    with csv_path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                x_raw = row.get("MoleculeComplexety", "").strip()
                y_raw = row.get(" Time (seconds)", "").strip()
                name = row.get("MoleculeName", "").strip()
                if not x_raw or not y_raw:
                    continue
                x = float(x_raw)
                y = float(y_raw)
            except Exception:
                continue
            if math.isnan(x) or math.isnan(y):
                continue
            xs.append(x)
            ys.append(y)
            names.append(name)
    return np.array(xs, dtype=float), np.array(ys, dtype=float), names


def filter_over_threshold(xs: np.ndarray, ys: np.ndarray, names: List[str], threshold: float):
    mask = ys >= threshold
    return xs[mask], ys[mask], [names[i] for i, m in enumerate(mask) if m]


def compute_weights(xs: np.ndarray) -> np.ndarray:
    """Compute weights inversely proportional to data density.

    Points at bond counts with few measurements get higher weight,
    while points in dense regions get lower weight.
    """
    counts = defaultdict(int)
    for x in xs:
        counts[int(x)] += 1
    weights = np.array([1.0 / np.sqrt(counts[int(x)]) for x in xs])
    # Normalize so sum equals length (for fair R² comparison)
    weights = weights / np.sum(weights) * len(weights)
    return weights


def fit_linear(xs: np.ndarray, ys: np.ndarray) -> Tuple[float, float, float]:
    weights = compute_weights(xs)
    b, a = np.polyfit(xs, ys, 1, w=weights)
    pred = a + b * xs
    ss_res = np.sum(weights * (ys - pred) ** 2)
    ss_tot = np.sum(weights * (ys - ys.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot != 0 else float("nan")
    return a, b, r2


def fit_logy(xs: np.ndarray, ys: np.ndarray) -> Tuple[float, float, float]:
    mask = ys > 0
    xs_sel = xs[mask]
    ys_sel = ys[mask]
    logy = np.log10(ys_sel)
    b, a = np.polyfit(xs_sel, logy, 1)
    pred_logy = a + b * xs_sel
    pred = 10 ** pred_logy
    ss_res = np.sum((ys_sel - pred) ** 2)
    ss_tot = np.sum((ys_sel - ys_sel.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot != 0 else float("nan")
    return a, b, r2


def fit_cubic(xs: np.ndarray, ys: np.ndarray) -> Tuple[float, float, float, float, float]:
    """Fit cubic polynomial: y = a + bx + cx² + dx³ (weighted by data density)"""
    weights = compute_weights(xs)
    coeffs = np.polyfit(xs, ys, 3, w=weights)
    pred = np.polyval(coeffs, xs)
    ss_res = np.sum(weights * (ys - pred) ** 2)
    ss_tot = np.sum(weights * (ys - ys.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot != 0 else float("nan")
    return coeffs[0], coeffs[1], coeffs[2], coeffs[3], r2


def explain_datapoints(xs: np.ndarray, ys: np.ndarray, names: List[str]) -> str:
    n = len(xs)
    order = np.argsort(ys)[::-1]
    top5 = [(names[i], xs[i], ys[i]) for i in order[:5]]
    bottom5 = [(names[i], xs[i], ys[i]) for i in np.argsort(ys)[:5]]
    median_y = float(np.median(ys)) if n else float("nan")
    return (
        f"Datapoints: {n}\n"
        f"Time range: min={ys.min():.2f}s, median={median_y:.2f}s, max={ys.max():.2f}s\n"
        f"Bond count range: min={xs.min():.0f}, max={xs.max():.0f}\n"
        "Top 5 slowest (name, bonds, seconds): "
        + ", ".join(f"{nm} ({bx:.0f}, {ty:.0f}s)" for nm, bx, ty in top5)
        + "\nTop 5 fastest (name, bonds, seconds): "
        + ", ".join(f"{nm} ({bx:.0f}, {ty:.2f}s)" for nm, bx, ty in bottom5)
    )


def main() -> None:
    xs, ys, names = load_points(CSV_PATH)
    if xs.size == 0:
        raise SystemExit("No usable data points found.")

    a_lin, b_lin, r2_lin = fit_linear(xs, ys)
    a_logy, b_logy, r2_logy = fit_logy(xs, ys)

    # Plot 1: Linear axes
    plt.figure(figsize=(8, 6))
    plt.scatter(xs, ys, alpha=0.6, s=20, label="data")

    x_plot = np.linspace(xs.min(), xs.max(), 200)
    plt.plot(x_plot, a_lin + b_lin * x_plot, color="red",
             label=f"linear (R²={r2_lin:.3f})")

    plt.plot(x_plot, 10 ** (a_logy + b_logy * x_plot), color="purple",
             label=f"log(y) (R²={r2_logy:.3f})")

    plt.xlabel("MoleculeComplexety (number of bonds)")
    plt.ylabel("Computation time (seconds)")
    plt.title("Computation time vs. bond count")
    plt.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2)
    plt.grid(True, alpha=0.3)

    PLOT_DIR.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(PLOT_PATH, dpi=150, bbox_inches="tight")

    print(f"Wrote plot: {PLOT_PATH}")
    print(f"Linear R2={r2_lin:.3f}, LogY R2={r2_logy:.3f}")
    print(explain_datapoints(xs, ys, names))

    # Plot 2: Logarithmic time axis (y-axis log10)
    plt.figure(figsize=(8, 6))
    plt.scatter(xs, ys, alpha=0.6, s=20, label="data")

    x_plot = np.linspace(xs.min(), xs.max(), 200)
    plt.plot(x_plot, a_lin + b_lin * x_plot, color="red",
             label=f"linear (R²={r2_lin:.3f})")

    plt.plot(x_plot, 10 ** (a_logy + b_logy * x_plot), color="purple",
             label=f"log(y) (R²={r2_logy:.3f})")

    plt.xlabel("MoleculeComplexety (number of bonds)")
    plt.ylabel("Computation time (seconds, log scale)")
    plt.title("Computation time vs. bond count (log time axis)")
    plt.yscale("log")
    plt.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2)
    plt.grid(True, which="both", alpha=0.3)

    PLOT_DIR.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(PLOT_PATH_LOGY, dpi=150, bbox_inches="tight")

    print(f"Wrote plot: {PLOT_PATH_LOGY}")

    # Plot subset with times >= 40 seconds to focus on slower cases
    xs_over, ys_over, names_over = filter_over_threshold(xs, ys, names, threshold=40.0)
    if xs_over.size:
        a_lin_o, b_lin_o, r2_lin_o = fit_linear(xs_over, ys_over)
        a_logy_o, b_logy_o, r2_logy_o = fit_logy(xs_over, ys_over)
        d_cub, c_cub, b_cub, a_cub, r2_cub = fit_cubic(xs_over, ys_over)

        # Plot 3: >=40s linear axes
        plt.figure(figsize=(8, 6))
        plt.scatter(xs_over, ys_over, alpha=0.6, s=20, label="data (>=40s)")

        x_plot = np.linspace(xs_over.min(), xs_over.max(), 200)
        plt.plot(x_plot, a_lin_o + b_lin_o * x_plot, color="red",
                 label=f"linear (R²={r2_lin_o:.3f})")

        plt.plot(x_plot, 10 ** (a_logy_o + b_logy_o * x_plot), color="purple",
                 label=f"log(y) (R²={r2_logy_o:.3f})")

        plt.plot(x_plot, a_cub + b_cub * x_plot + c_cub * x_plot**2 + d_cub * x_plot**3,
                 color="green", linewidth=2, label=f"cubic (R²={r2_cub:.3f})")


        plt.xlabel("MoleculeComplexety (number of bonds)")
        plt.ylabel("Computation time (seconds)")
        plt.title("Computation time vs. bond count (>= 40s)")
        plt.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2)
        plt.grid(True, alpha=0.3)

        PLOT_DIR.mkdir(parents=True, exist_ok=True)
        plt.tight_layout()
        plt.savefig(PLOT_PATH_OVER40, dpi=150, bbox_inches="tight")

        print(f"Wrote plot: {PLOT_PATH_OVER40}")
        print(f"Linear R2 (>=40s)={r2_lin_o:.3f}, LogY R2 (>=40s)={r2_logy_o:.3f}, Cubic R2 (>=40s)={r2_cub:.3f}")
        print(explain_datapoints(xs_over, ys_over, names_over))

        # Plot 4: >=40s log-scale time axis
        plt.figure(figsize=(8, 6))
        plt.scatter(xs_over, ys_over, alpha=0.6, s=20, label="data (>=40s)")

        x_plot = np.linspace(xs_over.min(), xs_over.max(), 200)
        plt.plot(x_plot, a_lin_o + b_lin_o * x_plot, color="red",
                 label=f"linear (R²={r2_lin_o:.3f})")

        plt.plot(x_plot, 10 ** (a_logy_o + b_logy_o * x_plot), color="purple",
                 label=f"log(y) (R²={r2_logy_o:.3f})")

        plt.plot(x_plot, a_cub + b_cub * x_plot + c_cub * x_plot**2 + d_cub * x_plot**3,
                 color="green", linewidth=2, label=f"cubic (R²={r2_cub:.3f})")


        plt.xlabel("MoleculeComplexety (number of bonds)")
        plt.ylabel("Computation time (seconds, log scale)")
        plt.title("Computation time vs. bond count (>= 40s, log time axis)")
        plt.yscale("log")
        plt.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2)
        plt.grid(True, which="both", alpha=0.3)

        PLOT_DIR.mkdir(parents=True, exist_ok=True)
        plt.tight_layout()
        plt.savefig(PLOT_PATH_LOGY_OVER40, dpi=150, bbox_inches="tight")

        print(f"Wrote plot: {PLOT_PATH_LOGY_OVER40}")


if __name__ == "__main__":
    main()
