#!/usr/bin/env python3
"""Plot the MØD per-molecule cost / budget results (feasibility study).

Reads ``cost_per_molecule.csv`` (from ``cost_analysis.py``, under
``data/outputs/metrics``) and renders four
panels: the wall-time ECDF (log scale, censored tail marked), peak memory vs
wall time coloured by outcome, wall time vs output graph count (to show they do
*not* correlate), and the N* budget-crossover curve. Pure pandas/matplotlib --
no ``mod`` -- but matplotlib lives in the container, so run inside mol-spectro.sif.
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]

_BUCKET_COLOR = {
    "finished": "#2b7bba",
    "censored_timeout": "#d1495b",
    "oom_or_error": "#e08e0b",
    "infra_fail": "#8d8d8d",
}
_WALL_H = 72.0  # SLURM per-task wall the array ran under


def main() -> None:
    ap = argparse.ArgumentParser(description="Plot cost results (feasibility study)")
    ap.add_argument("--csv", default=str(ROOT / "data" / "outputs" / "metrics" / "cost_per_molecule.csv"))
    ap.add_argument("--out-dir", default=None, help="Default: data/outputs/plots")
    args = ap.parse_args()

    csv_path = Path(args.csv)
    out_dir = Path(args.out_dir) if args.out_dir else ROOT / "data" / "outputs" / "plots"
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(csv_path)
    for col in ["elapsed_s", "max_rss_mb", "sum_graphs", "max_round_graphs"]:
        df[col] = pd.to_numeric(df.get(col), errors="coerce")
    df["wall_h"] = df["elapsed_s"] / 3600.0
    df["rss_gb"] = df["max_rss_mb"] / 1024.0

    fig, axes = plt.subplots(2, 2, figsize=(12, 9))

    # 1) Wall-time ECDF (log x), finishers only, with censored count annotated.
    ax = axes[0, 0]
    fin = df[df["bucket"] == "finished"].dropna(subset=["wall_h"]).sort_values("wall_h")
    n_cens = int((df["bucket"] == "censored_timeout").sum())
    if len(fin):
        y = np.arange(1, len(fin) + 1) / len(fin)
        ax.step(fin["wall_h"], y, where="post", color=_BUCKET_COLOR["finished"])
    ax.axvline(_WALL_H, color=_BUCKET_COLOR["censored_timeout"], ls="--", lw=1,
               label=f"72 h wall ({n_cens} censored)")
    ax.set_xscale("log")
    ax.set_xlabel("wall time (h, log)")
    ax.set_ylabel("cumulative fraction of finishers")
    ax.set_title("Per-molecule cost ECDF")
    ax.legend(loc="lower right", fontsize=8)

    # 2) Peak RSS vs wall time, coloured by outcome; 16 G / 32 G lines.
    ax = axes[0, 1]
    for bucket, g in df.dropna(subset=["wall_h", "rss_gb"]).groupby("bucket"):
        ax.scatter(g["wall_h"], g["rss_gb"], s=22, alpha=0.8,
                   color=_BUCKET_COLOR.get(bucket, "#444"), label=bucket)
    ax.axhline(16, color="#e08e0b", ls=":", lw=1, label="16 G req")
    ax.axhline(32, color="#c0392b", ls=":", lw=1, label="32 G req")
    ax.set_xscale("log")
    ax.set_xlabel("wall time (h, log)")
    ax.set_ylabel("peak RSS (GB)")
    ax.set_title("Memory vs time (saturated aliphatics blow up both)")
    ax.legend(loc="upper left", fontsize=7)

    # 3) Wall time vs output graph count -- the anti-correlation panel.
    ax = axes[1, 0]
    sub = df.dropna(subset=["wall_h", "sum_graphs"])
    for bucket, g in sub.groupby("bucket"):
        ax.scatter(g["sum_graphs"], g["wall_h"], s=22, alpha=0.8,
                   color=_BUCKET_COLOR.get(bucket, "#444"), label=bucket)
    if len(sub) > 2:
        r = np.corrcoef(sub["sum_graphs"], sub["wall_h"])[0, 1]
        ax.set_title(f"Cost is NOT output size (Pearson r={r:.2f})")
    ax.set_yscale("log")
    ax.set_xlabel("output graphs (sum over rounds)")
    ax.set_ylabel("wall time (h, log)")
    ax.legend(loc="upper right", fontsize=7)

    # 4) N* budget crossover, both cost estimates.
    ax = axes[1, 1]
    budgets = np.array([100, 500, 1000, 5000, 10000], dtype=float)
    fin_mean_h = fin["wall_h"].mean() if len(fin) else np.nan
    cens = df[df["bucket"] == "censored_timeout"]["wall_h"].dropna()
    lb_mean_h = pd.concat([fin["wall_h"], cens]).mean()
    for mean_h, lbl, c in [
        (fin_mean_h, f"finishers-only ({fin_mean_h:.1f} h/mol)", _BUCKET_COLOR["finished"]),
        (lb_mean_h, f"censored-LB ({lb_mean_h:.1f} h/mol)", _BUCKET_COLOR["censored_timeout"]),
    ]:
        ax.plot(budgets, budgets / mean_h, "o-", color=c, label=lbl)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("budget (core-hours)")
    ax.set_ylabel("affordable corpus N* (upper bound)")
    ax.set_title("Full-enumeration budget crossover")
    ax.legend(loc="upper left", fontsize=8)

    fig.suptitle("MØD per-molecule cost and full-enumeration budget", fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    out_path = out_dir / "cost.png"
    fig.savefig(out_path, dpi=140)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
