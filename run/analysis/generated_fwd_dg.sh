#!/bin/bash
source "$(cd "$(dirname "$0")/../.." && pwd)/src/path_setup.sh"

# ensure outputs/mod_post/out exists
mkdir -p "$REPO_ROOT/$OUTPUTS_DIR_REL/mod_post/out"

apptainer exec \
  --pwd "$C_MOD_POST" \
  --bind "$REPO_ROOT/$SRC_DIR_REL:$C_SRC" \
  --bind "$REPO_ROOT/$OUTPUTS_DIR_REL:$C_OUTPUTS" \
  --bind "$REPO_ROOT/$DATA_DIR_REL:$C_DATA" \
  "$SIF" \
  python $C_SRC/data_generation/analyze.py \
  --name "toluene" \
  --smiles "CC1=CC=CC=C1" \
  --dir "$C_PROCESSED/fwd"
