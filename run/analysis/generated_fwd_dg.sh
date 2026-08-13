#!/bin/bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
set -a; source "$REPO_ROOT/src/paths.env"; set +a

# ensure data/outputs/mod_post/out exists
mkdir -p "$REPO_ROOT/$MOD_POST_DIR_REL/out"

apptainer exec \
  --pwd "$C_MOD_POST" \
  --bind "$REPO_ROOT/$SRC_DIR_REL:$C_SRC" \
  --bind "$REPO_ROOT/$OUTPUTS_DIR_REL:$C_OUTPUTS" \
  --bind "$REPO_ROOT/$DATA_DIR_REL:$C_DATA" \
  --env PYTHONPATH="$C_APP" \
  "$REPO_ROOT/$SIF_REL" \
  python "$C_SRC/data_generation/analyze.py" \
  --name "toluene" \
  --smiles "CC1=CC=CC=C1" \
  --dir "$C_FWD"
