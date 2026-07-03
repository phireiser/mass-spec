#!/usr/bin/env python3
"""Plot the MØD explainability-ceiling results (feasibility study).

Reads ``ceiling_per_molecule.csv`` (from ``run_ceiling.py``, under
``outputs/metrics``) and renders four panels: the ceiling distribution,
raw-explained vs formula-null, ceiling vs molecular mass, and the mean
odd/even-electron split of the unexplained intensity. Pure pandas/matplotlib --
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


def main() -> None:
    ap = argparse.ArgumentParser(description="Plot ceiling results (feasibility study)")
    ap.add_argument("--csv", default=str(ROOT / "outputs" / "metrics" / "ceiling_per_molecule.csv"))
    ap.add_argument("--out-dir", default=None, help="Default: outputs/plots")
    args = ap.parse_args()

    csv_path = Path(args.csv)
    out_dir = Path(args.out_dir) if args.out_dir else ROOT / "outputs" / "plots"
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(csv_path)
    df = df[df.get("status", "ok").astype(str) == "ok"].copy()
    for col in ["ceiling", "raw_int_hi", "null_formula", "null_uniform",
                "mplus_nominal", "unexpl_OE_frac", "unexpl_EE_frac"]:
        if col in df:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    fig, axes = plt.subplots(2, 2, figsize=(12, 9))

    # 1) Ceiling distribution
    ax = axes[0, 0]
    ceil = df["ceiling"].dropna()
    ax.hist(ceil, bins=20, color="steelblue", alpha=0.8, edgecolor="white")
    if len(ceil):
        ax.axvline(ceil.mean(), color="crimson", ls="--", label=f"mean {ceil.mean():.2f}")
        ax.axvline(ceil.median(), color="darkorange", ls=":", label=f"median {ceil.median():.2f}")
    ax.set_xlabel("null-subtracted ceiling")
    ax.set_ylabel("molecules")
    ax.set_title(f"Explainability ceiling (n={len(ceil)})")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 2) Raw vs formula-null (points above y=x are explained beyond chance)
    ax = axes[0, 1]
    ax.scatter(df["null_formula"], df["raw_int_hi"], s=28, alpha=0.7, c="seagreen")
    lim = [0, 1]
    ax.plot(lim, lim, color="gray", ls="--", lw=1, label="y = x (chance)")
    ax.set_xlim(lim)
    ax.set_ylim(lim)
    ax.set_xlabel("formula-null explained fraction")
    ax.set_ylabel("raw explained fraction (intensity)")
    ax.set_title("Raw explained vs random-formula null")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 3) Ceiling vs molecular mass
    ax = axes[1, 0]
    ax.scatter(df["mplus_nominal"], df["ceiling"], s=28, alpha=0.7, c="mediumpurple")
    ax.axhline(0, color="gray", lw=1)
    ax.set_xlabel("molecular ion m/z (M+•)")
    ax.set_ylabel("ceiling")
    ax.set_title("Ceiling vs molecule size")
    ax.grid(True, alpha=0.3)

    # 4) Mean OE/EE split of unexplained intensity
    ax = axes[1, 1]
    oe = df["unexpl_OE_frac"].mean(skipna=True)
    ee = df["unexpl_EE_frac"].mean(skipna=True)
    ax.bar(["odd-electron", "even-electron"], [oe, ee],
           color=["indianred", "steelblue"], alpha=0.85)
    ax.set_ylim(0, 1)
    ax.set_ylabel("mean fraction of unexplained intensity")
    ax.set_title("Unexplained peaks: nitrogen-rule parity split")
    for i, v in enumerate([oe, ee]):
        if not np.isnan(v):
            ax.text(i, v + 0.02, f"{v:.2f}", ha="center")
    ax.grid(True, alpha=0.3, axis="y")

    fig.tight_layout()
    out_path = out_dir / "ceiling.png"
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
