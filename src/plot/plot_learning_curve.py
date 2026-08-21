#!/usr/bin/env python3
"""Learning curve of the two-phase training run: loss per epoch, Phase A and B.

``main.py`` prints one line per epoch to stdout, which SLURM captures in
``TRAIN_LOG_DIR_REL/<jobid>.out``:

    [A] epoch 01 loss 4.7088 | frac 0.73
    [B] epoch 01 loss 2.9035 | frac 0.73

``frac`` is the hard-negative curriculum fraction, which ramps from
``--curriculum_start`` to 1.0 over the first few epochs. The two phases train
different objectives (A: forward spectrum prediction; B: latent alignment plus
spectrum reconstruction), so their losses are not comparable and each gets its
own panel rather than a shared axis.

No validation loss is logged per epoch -- ``main.py`` evaluates retrieval once,
after Phase B -- so this is a training-loss curve. The final validation and test
numbers live in ``METRICS_DIR_REL/metrics_main.csv``.

Inputs
------
The newest ``*.out`` under ``TRAIN_LOG_DIR_REL``, or an explicit ``--log``.

Outputs
-------
    METRICS_DIR_REL/learning_curve.csv          epoch, phase, loss, frac
    PLOTS_DIR_REL/learning_curve.pdf/.svg       --style report (the default)
    PLOTS_DIR_REL/learning_curve_slides.pdf/.svg  --style slides

The two styles differ only in drawn size and font size. A figure is scaled to
the width of whatever includes it, so its fonts must be sized for that target:
the report is a4 with 2.5 cm margins and includes plots at ``0.8\\textwidth``
(~12.8 cm), a 16:9 beamer frame gives ~11 cm, and the same PDF cannot serve
both without one of them coming out unreadable.

Run inside the container (matplotlib lives there):

    run/analysis/learning_curve_plot.sh
"""
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path
from typing import Dict, List

import numpy as np
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

from src.project_paths import shared_path

TRAIN_LOG_DIR = shared_path("TRAIN_LOG_DIR_REL")
OUT_CSV = shared_path("METRICS_DIR_REL", "learning_curve.csv")
PLOTS_DIR = shared_path("PLOTS_DIR_REL")

# Same amber/blue as the other slide and report figures.
PHASE_COLOR = {"A": "#e08b00", "B": "#3b6fb0"}
# Kept short enough to fit a half-slide panel at slide font size; what the two
# objectives actually are is the caption's job, not the title's.
PHASE_TITLE = {
    "A": "Phase A — forward model",
    "B": "Phase B — alignment + recon.",
}
PHASE_YLABEL = {
    "A": "Forward loss (weighted)",
    "B": "Alignment + recon. loss",
}
RAMP_COLOR = "#c8c8c8"
FIGURE_FORMATS = (".pdf", ".svg")
INSET_EPOCHS = 100          # x-range of the per-panel zoom on the early epochs

# Per-panel size and font sizes, chosen so that after the including document
# scales the figure to its text width the fonts land near its body size.
STYLES = {
    "report": {
        "stem": "learning_curve",
        "panel": (6.0, 4.2),
        "title": 11.0, "label": 11.0, "tick": 10.0, "note": 9.5, "inset": 8.0,
    },
    "slides": {
        "stem": "learning_curve_slides",
        # Deliberately short: a beamer frame constrains the figure by height, so
        # the on-screen font size scales with 1/height, not with width.
        "panel": (4.1, 3.2),
        "title": 17.0, "label": 16.0, "tick": 14.0, "note": 13.5, "inset": 13.0,
    },
}

EPOCH_LINE = re.compile(
    r"^\[([AB])\]\s+epoch\s+(\d+)\s+loss\s+([-\d.eE+]+)\s+\|\s+frac\s+([\d.]+)"
)


def newest_train_log() -> Path:
    """The most recently modified SLURM stdout file in the training log dir."""
    candidates = sorted(Path(TRAIN_LOG_DIR).glob("*.out"),
                        key=lambda p: p.stat().st_mtime, reverse=True)
    for path in candidates:
        if any(EPOCH_LINE.match(line) for line in path.read_text(errors="replace").splitlines()):
            return path
    raise SystemExit(f"no training log with epoch lines under {TRAIN_LOG_DIR}")


def parse_log(path: Path) -> Dict[str, List[dict]]:
    """Pull the per-epoch loss lines out of a training log, keyed by phase.

    A run that was resumed or restarted into the same file would repeat epoch
    numbers; the last block wins, which is what a resumed run means.
    """
    phases: Dict[str, Dict[int, dict]] = {"A": {}, "B": {}}
    for line in path.read_text(errors="replace").splitlines():
        m = EPOCH_LINE.match(line)
        if not m:
            continue
        phase, epoch, loss, frac = m.group(1), int(m.group(2)), float(m.group(3)), float(m.group(4))
        phases[phase][epoch] = {"epoch": epoch, "loss": loss, "frac": frac}
    return {p: [rows[e] for e in sorted(rows)] for p, rows in phases.items() if rows}


def write_csv(curves: Dict[str, List[dict]]) -> None:
    Path(OUT_CSV).parent.mkdir(parents=True, exist_ok=True)
    with Path(OUT_CSV).open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["phase", "epoch", "loss", "frac"])
        for phase in sorted(curves):
            for row in curves[phase]:
                w.writerow([phase, row["epoch"], f"{row['loss']:.6f}", f"{row['frac']:.4f}"])


def tail_drop(loss: np.ndarray, fraction: float) -> float:
    """How much the loss still fell over the last ``fraction`` of the run."""
    return float(loss[int((1.0 - fraction) * len(loss))] - loss[-1])


def draw_panel(ax, phase: str, rows: List[dict], style: dict, with_inset: bool) -> None:
    epochs = np.array([r["epoch"] for r in rows])
    loss = np.array([r["loss"] for r in rows])
    frac = np.array([r["frac"] for r in rows])
    color = PHASE_COLOR[phase]

    ax.plot(epochs, loss, color=color, lw=1.3, zorder=3)

    # The curriculum ramp: the loss rises while the hard-negative fraction grows,
    # so the peak is a property of the schedule, not of the optimisation.
    ramping = epochs[frac < 1.0]
    ramp_end = int(ramping.max()) if ramping.size else 0

    final = float(loss[-1])
    ax.scatter([epochs[-1]], [final], s=26, color=color, zorder=4)
    ax.annotate(f"{final:.2f}", xy=(epochs[-1], final), xytext=(-4, 8),
                textcoords="offset points", ha="right",
                fontsize=style["note"], color="#404040")

    ax.set_title(PHASE_TITLE[phase], fontsize=style["title"], pad=8)
    ax.set_xlabel("Epoch", fontsize=style["label"])
    ax.set_ylabel(PHASE_YLABEL[phase], fontsize=style["label"])
    ax.tick_params(labelsize=style["tick"])
    ax.grid(True, alpha=0.25, lw=0.4)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_xlim(0, epochs.max())

    # Peak -> final says how far it came; the tail drop says whether it had
    # stopped moving, which is the question 10 000 epochs actually raises.
    ax.annotate(
        f"peak {loss.max():.2f} $\\rightarrow$ final {final:.2f}\n"
        f"last 10% of epochs: $-${tail_drop(loss, 0.10):.3f}",
        xy=(0.99, 0.99), xycoords="axes fraction", ha="right", va="top",
        fontsize=style["note"], color="#404040",
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#d0d0d0", lw=0.6),
    )

    if not with_inset or epochs.max() <= INSET_EPOCHS:
        return

    # The ramp and the plateau it leaves behind occupy the first few dozen epochs
    # out of ten thousand, so they need their own axes to be readable at all.
    span = epochs <= INSET_EPOCHS
    # Upper right, clear of both the stat box above and the descending curve
    # below -- the inset is opaque, and the Phase A loss spikes reach into the
    # middle of the panel.
    inset = ax.inset_axes([0.48, 0.38, 0.50, 0.33])
    inset.plot(epochs[span], loss[span], color=color, lw=1.1)
    if ramp_end:
        inset.axvspan(0, ramp_end, color=RAMP_COLOR, alpha=0.45, lw=0)
        # Leader line into the band: it is three epochs wide out of a hundred, so
        # the label cannot sit next to it without landing on the curve.
        inset.annotate("curriculum ramp", xy=(ramp_end, loss[span][ramp_end - 1]),
                       xytext=(0.07, 0.06), textcoords="axes fraction",
                       ha="left", va="bottom", fontsize=style["inset"], color="#808080",
                       arrowprops=dict(arrowstyle="-", color="#b8b8b8", lw=0.7,
                                       shrinkA=1, shrinkB=2))
    inset.set_xlim(0, INSET_EPOCHS)
    inset.set_xticks([0, INSET_EPOCHS // 2, INSET_EPOCHS])
    inset.yaxis.set_major_locator(MaxNLocator(3))
    inset.tick_params(labelsize=style["inset"], length=2)
    inset.set_title(f"first {INSET_EPOCHS} epochs", fontsize=style["inset"],
                    color="#606060", pad=2)
    inset.grid(True, alpha=0.2, lw=0.3)
    for side in ("top", "right"):
        inset.spines[side].set_visible(False)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--log", type=Path, default=None,
                    help="training log to parse (default: newest *.out in the train log dir)")
    ap.add_argument("--style", choices=sorted(STYLES), default="report",
                    help="drawn size and font size of the figure (default: report)")
    ap.add_argument("--out-stem", type=Path, default=None,
                    help="output path without suffix (default: per --style)")
    ap.add_argument("--no-inset", action="store_true",
                    help="omit the early-epoch zoom inset")
    args = ap.parse_args()

    style = STYLES[args.style]
    out_stem = args.out_stem or Path(PLOTS_DIR) / style["stem"]

    log_path = args.log or newest_train_log()
    curves = parse_log(log_path)
    if not curves:
        raise SystemExit(f"{log_path}: no '[A]/[B] epoch ... loss ...' lines found")
    print(f"parsed {log_path}")

    write_csv(curves)

    phases = sorted(curves)
    panel_w, panel_h = style["panel"]
    fig, axes = plt.subplots(1, len(phases), figsize=(panel_w * len(phases), panel_h))
    for ax, phase in zip(np.atleast_1d(axes), phases):
        draw_panel(ax, phase, curves[phase], style, with_inset=not args.no_inset)
        rows = curves[phase]
        loss = np.array([r["loss"] for r in rows])
        print(f"  phase {phase}: {len(rows)} epochs, first {loss[0]:.4f}, "
              f"peak {loss.max():.4f}, final {loss[-1]:.4f}, "
              f"tail drop (last 10%) {tail_drop(loss, 0.10):.4f}")

    fig.tight_layout()
    out_stem.parent.mkdir(parents=True, exist_ok=True)
    for ext in FIGURE_FORMATS:
        fig.savefig(str(out_stem) + ext, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {OUT_CSV} and {out_stem}.pdf/.svg [{args.style}]")


if __name__ == "__main__":
    main()
