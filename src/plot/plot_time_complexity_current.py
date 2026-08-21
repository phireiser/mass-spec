#!/usr/bin/env python3
"""Re-measure plot: computation time vs. molecular complexity, current pipeline.

Companion to ``plot_time_complexity.py``, which plots the 2026-04 table
(``MolecuelProcessingTimeTableComplexety.csv``). That table predates the three
optimisation commits on the ``sub_group`` hot path and the delocalized charge
model, so it no longer describes what the pipeline costs.

This script reads the per-molecule JSON written by
``run/hpc/bench_time_complexity.sh`` (one SLURM task per molecule, DG built
through ``strategy.make_fwd_strategy`` exactly as ``main.py`` builds it,
single-threaded, no dump writing), joins it to the old table by molecule name,
derives the same ForliLab bottchscore x-axis, and writes:

    METRICS_DIR/time_complexity_current.csv        the joined old/new table
    PLOTS_DIR/time_vs_complexity_current.pdf       new vs old, log time axis
    PLOTS_DIR/time_vs_complexity_current.svg

A molecule whose task is still running, exceeded the wall limit, or was rejected
by MOD (the old table carries one malformed SMILES) leaves no JSON; those are
listed on stdout rather than silently dropped.

Run inside the container (bottchscore3 and matplotlib live there):

    run/analysis/time_complex_plots_current.sh
"""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Dict, List

import numpy as np
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from bottchscore3 import calculate_bottchscore_from_smiles

from src.project_paths import shared_path

INPUT_CSV = shared_path("METRICS_DIR_REL", "time_complexity_bench_input.csv")
JSON_DIR = shared_path("METRICS_DIR_REL", "time_complexity_new")
OUT_CSV = shared_path("METRICS_DIR_REL", "time_complexity_current.csv")
FIG_STEM = shared_path("PLOTS_DIR_REL", "time_vs_complexity_current")

NEW_COLOR = "#e08b00"     # amber, as in the slide figures
OLD_COLOR = "#b0b0b0"
FIT_COLOR = "#3b6fb0"
FIGURE_FORMATS = (".pdf", ".svg")
WALL_LIMIT_S = 3600.0      # --time=0-01:00:00 in run/hpc/bench_time_complexity.sh


def load_rows():
    """Join the bench JSONs onto the old table by molecule name.

    Returns (measured_rows, censored_rows). A censored row is a molecule whose
    task produced no JSON but whose SMILES does yield a complexity score, i.e.
    it ran past the wall limit rather than being rejected as malformed input.
    """
    measured: Dict[str, dict] = {}
    for path in sorted(Path(JSON_DIR).glob("*.json")):
        text = path.read_text().strip()
        if not text:
            continue
        try:
            rec = json.loads(text)
        except json.JSONDecodeError:
            continue
        measured[rec["molecule"]] = rec

    rows: List[Dict[str, float]] = []
    censored: List[Dict[str, float]] = []
    rejected: List[str] = []
    for r in csv.DictReader(Path(INPUT_CSV).open()):
        name, smiles = r["name"], r["smiles"]
        rec = measured.get(name)
        try:
            complexity = float(calculate_bottchscore_from_smiles(smiles))
        except Exception:
            rejected.append(name)
            continue
        if math.isnan(complexity):
            rejected.append(name)
            continue
        if rec is None:
            censored.append({"name": name, "complexity": complexity,
                             "old_s": float(r["old_s"])})
            continue
        rows.append({
            "name": name,
            "smiles": smiles,
            "complexity": complexity,
            "old_s": float(r["old_s"]),
            "new_s": float(rec["wall_s"]),
            "species": int(rec["species"]),
            "derivations": int(rec["derivations"]),
        })
    if censored:
        print(f"censored, still running or past the wall limit ({len(censored)}): "
              + ", ".join(sorted(c["name"] for c in censored)))
    if rejected:
        print(f"no complexity score, input rejected ({len(rejected)}): "
              + ", ".join(sorted(rejected)))
    return rows, censored


def fit_logy(xs: np.ndarray, ys: np.ndarray):
    """Least squares on log10(time); returns intercept, slope, R^2 in log space."""
    mask = ys > 0
    x, y = xs[mask], np.log10(ys[mask])
    b, a = np.polyfit(x, y, 1)
    pred = a + b * x
    ss_res = float(np.sum((y - pred) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    return a, b, (1 - ss_res / ss_tot if ss_tot else float("nan"))


def main() -> None:
    rows, censored = load_rows()
    if not rows:
        raise SystemExit("no measurements found -- has the SLURM array finished?")

    Path(OUT_CSV).parent.mkdir(parents=True, exist_ok=True)
    with Path(OUT_CSV).open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    xs = np.array([r["complexity"] for r in rows])
    new = np.array([r["new_s"] for r in rows])
    old = np.array([r["old_s"] for r in rows])
    a, b, r2 = fit_logy(xs, new)

    ratio_all = old / np.maximum(new, 1e-9)

    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    ax.scatter(xs, old, s=20, alpha=0.5, color=OLD_COLOR, label="2026-04 (old)")
    ax.scatter(xs, new, s=26, alpha=0.85, color=NEW_COLOR, label="current pipeline")

    grid = np.linspace(xs.min(), xs.max(), 200)
    ax.plot(grid, 10 ** (a + b * grid), color=FIT_COLOR, lw=1.8,
            label=f"log-linear fit ($R^2={r2:.2f}$)")

    if censored:
        cx = np.array([c["complexity"] for c in censored])
        ax.scatter(cx, np.full_like(cx, WALL_LIMIT_S), s=44, marker="^",
                   facecolors="none", edgecolors=NEW_COLOR, linewidths=1.2,
                   label=f"censored: $>{WALL_LIMIT_S/3600:.0f}$ h (n={len(censored)})")

    for seconds, text in ((60, "1 min"), (3600, "1 h"), (86400, "1 d")):
        ax.axhline(seconds, color="#c8c8c8", lw=0.7, ls=":", zorder=0)
        ax.annotate(text, xy=(xs.min(), seconds), xytext=(1, 2),
                    textcoords="offset points", fontsize=9, color="#909090")

    ax.set_yscale("log")
    ax.set_xlabel("ForliLab bottchscore (molecular complexity)", fontsize=11)
    ax.set_ylabel("Computation time (s, log scale)", fontsize=11)
    ax.tick_params(labelsize=10)
    ax.grid(True, which="both", alpha=0.25, lw=0.4)
    ax.legend(frameon=False, fontsize=10, loc="upper left")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.annotate(
        f"$n={len(rows)}$ molecules, same SMILES as the old table\n"
        f"median $ {np.median(old):.0f}$ s $\\rightarrow$ ${np.median(new):.2f}$ s "
        f"(median speed-up ${np.median(ratio_all):.0f}\\times$)\n"
        f"whole set: ${new.sum()/60:.1f}$ min of compute",
        xy=(0.985, 0.045), xycoords="axes fraction", ha="right", va="bottom",
        fontsize=9.5, color="#404040",
        bbox=dict(boxstyle="round,pad=0.4", fc="white", ec="#d0d0d0", lw=0.6),
    )

    fig.tight_layout()
    Path(FIG_STEM).parent.mkdir(parents=True, exist_ok=True)
    for ext in FIGURE_FORMATS:
        fig.savefig(str(FIG_STEM) + ext, dpi=300, bbox_inches="tight")
    plt.close(fig)

    ratio = ratio_all
    print(f"n={len(rows)}  new: min={new.min():.2f}s median={np.median(new):.2f}s "
          f"max={new.max():.2f}s  total={new.sum():.1f}s")
    print(f"speedup vs 2026-04: median x{np.median(ratio):.0f}  max x{ratio.max():.0f}")
    print(f"wrote {OUT_CSV} and {FIG_STEM}.pdf/.svg")


if __name__ == "__main__":
    main()
