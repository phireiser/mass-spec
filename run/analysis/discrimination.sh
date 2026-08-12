#!/bin/bash
# Phase 1 — true-vs-same-formula-decoy discrimination gate.
#
# Uses only measured NIST spectra (the Parquet store, data/nist_spectra): for
# every target compound with a spectrum and at least one same-formula decoy, it
# scores each candidate by cosine(observed_true, observed_candidate) and reports
# the best-decoy cosine -- the bar the MØD forward model must beat to identify
# that molecule. Writes data/outputs/metrics/{discrimination_per_target.csv,
# discrimination_summary.json}. Needs pyarrow + rdkit (no `mod`), so it runs
# inside mol-spectro.sif.
#
# Usage:
#   bash run/analysis/discrimination.sh                       # all targets
#   bash run/analysis/discrimination.sh --names limonene,toluene   # smoke
#   (further args forwarded to discriminate.py, e.g. --max-group 40)
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
source "$REPO_ROOT/src/paths.env"

mkdir -p "$REPO_ROOT/$METRICS_DIR_REL"

apptainer exec \
  --bind "$REPO_ROOT/$SRC_DIR_REL:$C_SRC" \
  --bind "$REPO_ROOT/$DATA_DIR_REL:$C_DATA" \
  --bind "$REPO_ROOT/$OUTPUTS_DIR_REL:$C_OUTPUTS" \
  --env PYTHONPATH="$C_APP" \
  "$REPO_ROOT/$SIF" \
  python "$C_SRC/data_generation/analysis/discrimination/discriminate.py" "$@"
