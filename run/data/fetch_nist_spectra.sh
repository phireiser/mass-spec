#!/bin/bash
source "$(dirname "$0")/src/path_setup.sh"

apptainer exec \
  --bind "$REPO_ROOT/$SRC_DIR_REL:$C_SRC" \
  --bind "$REPO_ROOT/$DATA_DIR_REL:$C_DATA" \
  --env PYTHONPATH="$C_APP:$C_SRC" \
  "$SIF" \
  python $C_SRC/data_generation/nist_fetcher.py \
  --csv "$C_CSV" \
  --output "$C_NIST"
