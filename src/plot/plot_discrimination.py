#!/usr/bin/env python3
"""Plot the Phase-1 true-vs-decoy discrimination results.

Reads ``discrimination_per_target.csv`` (from ``discriminate.py``, under
``data/outputs/metrics``) and renders four panels: the best-decoy-cosine
distribution (the bar the forward model must beat), best-decoy cosine vs number
of decoys, the per-target margin, and the count of confusable decoys per target.
Pure pandas/matplotlib -- no ``mod`` -- but matplotlib lives in the container, so
run inside mol-spectro.sif.
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.project_paths import shared_path

DEFAULT_CSV = shared_path("METRICS_DIR_REL", "discrimination_per_target.csv")
DEFAULT_PLOTS_DIR = shared_path("PLOTS_DIR_REL")


def main() -> None:
    ap = argparse.ArgumentParser(description="Plot Phase-1 discrimination results")
    ap.add_argument("--csv", default=str(DEFAULT_CSV))
    ap.add_argument("--out-dir", default=None, help=f"Default: {DEFAULT_PLOTS_DIR}")
    args = ap.parse_args()

    out_dir = Path(args.out_dir) if args.out_dir else DEFAULT_PLOTS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(args.csv)
    df = df[df.get("status", "ok").astype(str) == "ok"].copy()
    for col in ["best_decoy_cosine", "mean_decoy_cosine", "n_decoys", "margin",
                "n_decoy_cos_gt_0.9"]:
        if col in df:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    fig, axes = plt.subplots(2, 2, figsize=(12, 9))

    # 1) Best-decoy cosine distribution -- the bar the forward model must beat.
    ax = axes[0, 0]
    best = df["best_decoy_cosine"].dropna()
    ax.hist(best, bins=20, range=(0, 1), color="steelblue", alpha=0.8, edgecolor="white")
    if len(best):
        ax.axvline(best.mean(), color="crimson", ls="--", label=f"mean {best.mean():.2f}")
        ax.axvline(best.median(), color="darkorange", ls=":", label=f"median {best.median():.2f}")
    ax.axvline(0.9, color="black", ls="-", lw=1, alpha=0.5, label="0.9 (near-degenerate)")
    ax.set_xlabel("best same-formula decoy cosine (real spectra)")
    ax.set_ylabel("targets")
    ax.set_title(f"Discrimination bar the forward model must beat (n={len(best)})")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # 2) Best-decoy cosine vs number of decoys (more isomers -> closer confuser?)
    ax = axes[0, 1]
    ax.scatter(df["n_decoys"], df["best_decoy_cosine"], s=28, alpha=0.7, c="seagreen")
    ax.axhline(0.9, color="gray", ls="--", lw=1)
    ax.set_xlabel("number of same-formula decoys")
    ax.set_ylabel("best-decoy cosine")
    ax.set_title("Confusability vs decoy-pool size")
    ax.set_ylim(0, 1.02)
    ax.grid(True, alpha=0.3)

    # 3) Per-target margin (1 - best-decoy cosine): oracle slack, sorted.
    ax = axes[1, 0]
    margin = df["margin"].dropna().sort_values().reset_index(drop=True)
    ax.bar(range(len(margin)), margin, color="mediumpurple", alpha=0.85)
    ax.set_xlabel("target (sorted by margin)")
    ax.set_ylabel("margin = 1 - best-decoy cosine")
    ax.set_title("Oracle discrimination margin per target")
    ax.grid(True, alpha=0.3, axis="y")

    # 4) How many targets have a near-degenerate decoy, by threshold.
    ax = axes[1, 1]
    thr = [0.7, 0.8, 0.9, 0.95, 0.99]
    counts = [int((best > t).sum()) for t in thr]
    ax.bar([f"> {t}" for t in thr], counts, color="indianred", alpha=0.85)
    ax.set_ylabel("targets with a decoy above threshold")
    ax.set_title(f"Targets with a hard same-formula decoy (of {len(best)})")
    for i, v in enumerate(counts):
        ax.text(i, v + 0.5, str(v), ha="center")
    ax.grid(True, alpha=0.3, axis="y")

    fig.tight_layout()
    out_path = out_dir / "discrimination.png"
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
