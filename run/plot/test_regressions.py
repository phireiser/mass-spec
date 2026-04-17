#!/usr/bin/env python3
"""Test multiple regression models on filtered data (time >= 40s)."""
from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import List, Tuple

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "MolecuelProcessingTimeTableComplexety.csv"


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


def filter_over_threshold(xs: np.ndarray, ys: np.ndarray, threshold: float):
    mask = ys >= threshold
    return xs[mask], ys[mask]


def compute_r2(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - y_true.mean()) ** 2)
    return 1 - ss_res / ss_tot if ss_tot != 0 else float("nan")


# Regression models
def fit_linear(xs: np.ndarray, ys: np.ndarray) -> Tuple[float, float, float]:
    b, a = np.polyfit(xs, ys, 1)
    pred = a + b * xs
    r2 = compute_r2(ys, pred)
    return a, b, r2


def fit_logy(xs: np.ndarray, ys: np.ndarray) -> Tuple[float, float, float]:
    mask = ys > 0
    xs_sel = xs[mask]
    ys_sel = ys[mask]
    logy = np.log10(ys_sel)
    b, a = np.polyfit(xs_sel, logy, 1)
    pred_logy = a + b * xs_sel
    pred = 10 ** pred_logy
    r2 = compute_r2(ys_sel, pred)
    return a, b, r2


def fit_loglog(xs: np.ndarray, ys: np.ndarray) -> Tuple[float, float, float]:
    """Power law: log10(y) = a + b*log10(x) => y = 10^a * x^b"""
    mask = (xs > 0) & (ys > 0)
    xs_sel = xs[mask]
    ys_sel = ys[mask]
    logx = np.log10(xs_sel)
    logy = np.log10(ys_sel)
    b, a = np.polyfit(logx, logy, 1)
    pred_logy = a + b * logx
    pred = 10 ** pred_logy
    r2 = compute_r2(ys_sel, pred)
    return a, b, r2


def fit_quadratic(xs: np.ndarray, ys: np.ndarray) -> Tuple[float, float, float, float]:
    """y = a + bx + cx²"""
    coeffs = np.polyfit(xs, ys, 2)
    pred = np.polyval(coeffs, xs)
    r2 = compute_r2(ys, pred)
    return coeffs[0], coeffs[1], coeffs[2], r2


def fit_cubic(xs: np.ndarray, ys: np.ndarray) -> Tuple[float, float, float, float, float]:
    """y = a + bx + cx² + dx³"""
    coeffs = np.polyfit(xs, ys, 3)
    pred = np.polyval(coeffs, xs)
    r2 = compute_r2(ys, pred)
    return coeffs[0], coeffs[1], coeffs[2], coeffs[3], r2


def fit_sqrt(xs: np.ndarray, ys: np.ndarray) -> Tuple[float, float, float]:
    """y = a + b*sqrt(x)"""
    sqrtx = np.sqrt(xs)
    b, a = np.polyfit(sqrtx, ys, 1)
    pred = a + b * sqrtx
    r2 = compute_r2(ys, pred)
    return a, b, r2


def fit_power_simple(xs: np.ndarray, ys: np.ndarray) -> Tuple[float, float, float]:
    """y = a * x^b"""
    mask = (xs > 0) & (ys > 0)
    xs_sel = xs[mask]
    ys_sel = ys[mask]
    try:
        def power_func(x, a, b):
            return a * np.power(x, b)
        popt, _ = curve_fit(power_func, xs_sel, ys_sel, p0=[1, 1], maxfev=5000)
        pred = power_func(xs_sel, *popt)
        r2 = compute_r2(ys_sel, pred)
        return popt[0], popt[1], r2
    except Exception:
        return float("nan"), float("nan"), float("nan")


def fit_exponential(xs: np.ndarray, ys: np.ndarray) -> Tuple[float, float, float]:
    """y = a * exp(b*x)"""
    mask = ys > 0
    xs_sel = xs[mask]
    ys_sel = ys[mask]
    try:
        def exp_func(x, a, b):
            return a * np.exp(b * x)
        popt, _ = curve_fit(exp_func, xs_sel, ys_sel, p0=[1, 0.1], maxfev=5000)
        pred = exp_func(xs_sel, *popt)
        r2 = compute_r2(ys_sel, pred)
        return popt[0], popt[1], r2
    except Exception:
        return float("nan"), float("nan"), float("nan")


def main() -> None:
    xs, ys, names = load_points(CSV_PATH)
    xs_over, ys_over = filter_over_threshold(xs, ys, threshold=40.0)

    print(f"Testing {len(ys_over)} datapoints with time >= 40s\n")
    print("=" * 70)

    # Test all models
    results = []

    # Linear
    a, b, r2 = fit_linear(xs_over, ys_over)
    results.append(("Linear", f"y = {a:.3f} + {b:.3f}*x", r2))
    print(f"Linear:           R² = {r2:.6f}  |  y = {a:.3f} + {b:.3f}*x")

    # LogY
    a, b, r2 = fit_logy(xs_over, ys_over)
    results.append(("LogY", f"log10(y) = {a:.3f} + {b:.3f}*x", r2))
    print(f"LogY (log10):     R² = {r2:.6f}  |  log10(y) = {a:.3f} + {b:.3f}*x")

    # LogLog (Power law)
    a, b, r2 = fit_loglog(xs_over, ys_over)
    results.append(("LogLog (Power)", f"y = 10^{a:.3f} * x^{b:.3f}", r2))
    print(f"LogLog (Power):   R² = {r2:.6f}  |  y = 10^{a:.3f} * x^{b:.3f}")

    # Quadratic
    c, b, a, r2 = fit_quadratic(xs_over, ys_over)
    results.append(("Quadratic", f"y = {a:.3f} + {b:.3f}*x + {c:.3f}*x²", r2))
    print(f"Quadratic:        R² = {r2:.6f}  |  y = {a:.3f} + {b:.3f}*x + {c:.3f}*x²")

    # Cubic
    d, c, b, a, r2 = fit_cubic(xs_over, ys_over)
    results.append(("Cubic", f"y = {a:.3f} + {b:.3f}*x + {c:.3f}*x² + {d:.3f}*x³", r2))
    print(f"Cubic:            R² = {r2:.6f}  |  y = {a:.3f} + {b:.3f}*x + {c:.3f}*x² + {d:.3f}*x³")

    # Sqrt
    a, b, r2 = fit_sqrt(xs_over, ys_over)
    results.append(("Sqrt", f"y = {a:.3f} + {b:.3f}*sqrt(x)", r2))
    print(f"Sqrt:             R² = {r2:.6f}  |  y = {a:.3f} + {b:.3f}*sqrt(x)")

    # Power (simple)
    a, b, r2 = fit_power_simple(xs_over, ys_over)
    if not np.isnan(r2):
        results.append(("Power", f"y = {a:.3f} * x^{b:.3f}", r2))
        print(f"Power (fit):      R² = {r2:.6f}  |  y = {a:.3f} * x^{b:.3f}")

    # Exponential
    a, b, r2 = fit_exponential(xs_over, ys_over)
    if not np.isnan(r2):
        results.append(("Exponential", f"y = {a:.3f} * exp({b:.3f}*x)", r2))
        print(f"Exponential:      R² = {r2:.6f}  |  y = {a:.3f} * exp({b:.3f}*x)")

    print("=" * 70)

    # Sort by R² descending
    results.sort(key=lambda x: x[2], reverse=True)
    print("\nRanked by R²:")
    for i, (name, formula, r2) in enumerate(results, 1):
        print(f"{i}. {name:20s} R² = {r2:.6f}")
        print(f"   {formula}")


if __name__ == "__main__":
    main()
