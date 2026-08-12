#!/bin/bash
# Phase 1 — forward-discrimination scorer (the expensive half of the gate).
#
# For every target with a same-formula decoy, scores each candidate structure by
# cosine(observed_true, MØD-predicted(candidate)) using the forward DG dumps under
# data/processed/fwd, ranks the true molecule against its decoys, and compares to
# the oracle library-match bar from run/analysis/discrimination.sh. Coverage-aware:
# only complete (`.done`) decoy dumps are scored, so it can be run while the decoy
# generation batch is still filling in. Needs `mod`, so it runs inside mol-spectro.sif.
#
# Prereqs: run run/analysis/discrimination.sh first (writes the oracle CSV this
# joins against), and generate decoy dumps (DEFINITION_FILE=data/decoys_wave1.csv
# sbatch run/hpc/data_gen.sh).
#
# Usage:
#   bash run/analysis/score_forward.sh                     # all targets
#   bash run/analysis/score_forward.sh --names toluene,limonene
#   bash run/analysis/score_forward.sh --intensity binary  # ignore fragment counts
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
set -a; source "$REPO_ROOT/src/paths.env"; set +a

mkdir -p "$REPO_ROOT/$METRICS_DIR_REL"

apptainer exec \
  --bind "$REPO_ROOT/$SRC_DIR_REL:$C_SRC" \
  --bind "$REPO_ROOT/$DATA_DIR_REL:$C_DATA" \
  --bind "$REPO_ROOT/$OUTPUTS_DIR_REL:$C_OUTPUTS" \
  --env PYTHONPATH="$C_APP" \
  "$REPO_ROOT/$SIF_REL" \
  python "$C_SRC/data_generation/analysis/discrimination/score_forward.py" "$@"
