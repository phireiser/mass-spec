#!/bin/bash
set -euo pipefail

# Re-measured time-vs-complexity plot (current pipeline). Run
# `sbatch run/hpc/bench_time_complexity.sh` first: this only collects and plots.

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
set -a; source "$REPO_ROOT/src/paths.env"; set +a

apptainer exec \
  --bind "$REPO_ROOT/$SRC_DIR_REL:$C_SRC" \
  --bind "$REPO_ROOT/$OUTPUTS_DIR_REL:$C_OUTPUTS" \
  --bind "$REPO_ROOT/$DATA_DIR_REL:$C_DATA" \
  --env PYTHONPATH="$C_APP:/opt/bottchscore" \
"$REPO_ROOT/$SIF_REL" \
  python $C_SRC/plot/plot_time_complexity_current.py

# The report and the slides read figures from thesis/shared/figures.
cp "$REPO_ROOT/$PLOTS_DIR_REL/time_vs_complexity_current.pdf" \
   "$REPO_ROOT/$FIGURES_DIR_REL/time_vs_complexity_current.pdf"
echo "copied into $FIGURES_DIR_REL/"
