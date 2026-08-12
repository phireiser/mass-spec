#!/bin/bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
set -a; source "$REPO_ROOT/src/paths.env"; set +a

apptainer exec \
  --bind "$REPO_ROOT/$SRC_DIR_REL:$C_SRC" \
  --bind "$REPO_ROOT/$OUTPUTS_DIR_REL:$C_OUTPUTS" \
  --bind "$REPO_ROOT/$DATA_DIR_REL:$C_DATA" \
"$REPO_ROOT/$SIF_REL" \
  python $C_SRC/plot/plot_time_complexity.py
