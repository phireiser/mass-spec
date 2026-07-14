#!/usr/bin/env python3
from __future__ import annotations

"""
Mass-controlled retrieval figure for the report.

Reads the scorecard CSV written by ``src/machine_learning/main.py`` after the
held-out evaluation and renders the decisive "beyond mass" plot: for each mass
window, the learned within-window retrieval MRR next to the analytic
random-chance MRR. A learned bar standing above its chance reference is
structural signal that precursor mass alone cannot explain.

Input CSV (outputs/metrics/mass_controlled.csv), columns:
    split, window_da, learned_mrr, chance_mrr, delta_mrr, mean_pool, n

Output:
    mass_controlled_mrr.pdf (embedded by the report) and .svg (for previewing)

Example
-------
python src/plot/plot_mass_controlled.py \
    --csv outputs/metrics/mass_controlled.csv \
    --split test \
    --output-dir outputs/plots/
"""

import argparse
import csv
from pathlib import Path
from typing import Dict, List

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

LEARNED_COLOR = "#3b6fb0"
CHANCE_COLOR = "#b0b0b0"

# The report embeds figures as PDF (LISC has no Inkscape for the svg package);
# an SVG is kept alongside for quick previewing.
FIGURE_FORMATS = (".pdf", ".svg")


def load_rows(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="") as fh:
        return list(csv.DictReader(fh))


def plot_mass_controlled(rows: List[Dict[str, str]], split: str, output_path: Path) -> None:
    sel = [r for r in rows if r["split"].strip().lower() == split.lower()]
    if not sel:
        raise ValueError(
            f"no rows for split={split!r}; available splits: "
            f"{sorted({r['split'] for r in rows})}"
        )
    sel.sort(key=lambda r: float(r["window_da"]))

    windows = [float(r["window_da"]) for r in sel]
    learned = np.array([float(r["learned_mrr"]) for r in sel])
    chance = np.array([float(r["chance_mrr"]) for r in sel])
    deltas = learned - chance
    pools = [float(r["mean_pool"]) for r in sel]

    x = np.arange(len(windows))
    width = 0.38

    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    b_learned = ax.bar(x - width / 2, learned, width, label="Learned retrieval", color=LEARNED_COLOR)
    ax.bar(x + width / 2, chance, width, label="Random chance", color=CHANCE_COLOR)

    # Annotate the learned-over-chance margin above each learned bar.
    for xi, lv, dv in zip(x - width / 2, learned, deltas):
        ax.annotate(
            f"{dv:+.3f}",
            xy=(xi, lv),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
            color="black" if dv >= 0 else "#b00000",
        )

    ax.set_xticks(x)
    ax.set_xticklabels(
        [f"$\\pm${w:g} Da\n(pool $\\approx${p:.0f})" for w, p in zip(windows, pools)]
    )
    ax.set_ylabel("Within-window MRR")
    ax.set_title(f"Mass-controlled spectrum-to-structure retrieval ({split} split)")
    ax.set_ylim(0, max(1.0, float(learned.max()) * 1.25))
    ax.legend(frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    for ext in FIGURE_FORMATS:
        fig.savefig(output_path.with_suffix(ext), dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Plot mass-controlled learned-vs-chance retrieval MRR per mass window."
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=Path("outputs/metrics/mass_controlled.csv"),
        help="Path to the mass-controlled scorecard CSV.",
    )
    parser.add_argument(
        "--split",
        type=str,
        default="test",
        help="Which split to plot (test = held out, the headline figure).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/plots"),
        help="Directory for the output plot.",
    )
    args = parser.parse_args()

    rows = load_rows(args.csv)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    out = args.output_dir / "mass_controlled_mrr.pdf"
    plot_mass_controlled(rows, args.split, out)
    for ext in FIGURE_FORMATS:
        print(f"Saved: {out.with_suffix(ext).resolve()}")


if __name__ == "__main__":
    main()
