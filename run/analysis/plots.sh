#!/bin/bash
source "$(dirname "$0")/src/path_setup.sh"

apptainer exec \
  --bind "$REPO_ROOT/$SRC_DIR_REL:$C_SRC" \
  --bind "$REPO_ROOT/$OUTPUTS_DIR_REL:$C_OUTPUTS" \
  --bind "$REPO_ROOT/$DATA_DIR_REL:$C_DATA" \
"$SIF" \
  python $C_SRC/plot/plot_time_complexity.py
