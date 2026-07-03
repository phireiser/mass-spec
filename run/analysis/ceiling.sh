#!/bin/bash
# Feasibility — MØD explainability ceiling over the corpus.
#
# Reads the existing forward DG dumps (data/processed/fwd) and NIST spectra
# (from the Parquet store, outputs/nist_spectra) and writes outputs/metrics/{ceiling_per_molecule.csv,
# ceiling_summary.json}. Needs `mod`, so it runs inside mol-spectro.sif.
#
# Usage:
#   bash run/analysis/ceiling.sh                      # full corpus
#   bash run/analysis/ceiling.sh --names acetone,toluene,aniline   # smoke
#   (any further args are forwarded to run_ceiling.py, e.g. --draws 200)
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
  python "$C_SRC/data_generation/analysis/feasibility/run_ceiling.py" "$@"
