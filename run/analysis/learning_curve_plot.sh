#!/bin/bash
set -euo pipefail

# Learning curve (training loss per epoch, Phase A and Phase B) from the newest
# training log under $TRAIN_LOG_DIR_REL. Pass a log path to plot a specific run:
#   run/analysis/learning_curve_plot.sh data/outputs/logs/train/4924313.out

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
set -a; source "$REPO_ROOT/src/paths.env"; set +a

LOG_ARG=()
if [[ $# -gt 0 ]]; then
  LOG_ARG=(--log "$C_APP/${1#"$REPO_ROOT/"}")
fi

# Two styles of the same curve: the report scales it to ~12.8 cm, a 16:9 beamer
# frame to ~11 cm, so each needs its own font size to stay legible.
for style in report slides; do
  apptainer exec \
    --bind "$REPO_ROOT/$SRC_DIR_REL:$C_SRC" \
    --bind "$REPO_ROOT/$OUTPUTS_DIR_REL:$C_OUTPUTS" \
    --bind "$REPO_ROOT/$DATA_DIR_REL:$C_DATA" \
    --env PYTHONPATH="$C_APP" \
  "$REPO_ROOT/$SIF_REL" \
    python "$C_SRC/plot/plot_learning_curve.py" \
      --style "$style" "${LOG_ARG[@]+"${LOG_ARG[@]}"}"
done

# The report and the slides read figures from thesis/shared/figures.
for stem in learning_curve learning_curve_slides; do
  cp "$REPO_ROOT/$PLOTS_DIR_REL/$stem.pdf" "$REPO_ROOT/$FIGURES_DIR_REL/$stem.pdf"
done
echo "copied into $FIGURES_DIR_REL/"
