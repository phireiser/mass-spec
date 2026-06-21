#!/bin/bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
source "$REPO_ROOT/src/paths.env"

# this script opts in via RUN_MOD_INTEGRATION_TESTS=1.
apptainer exec \
    --env RUN_MOD_INTEGRATION_TESTS=1 \
    --bind "$REPO_ROOT/$SRC_DIR_REL:$C_SRC" \
    --bind "$REPO_ROOT/$DATA_DIR_REL:$C_DATA" \
    "$SIF" \
    python3 -m unittest discover -s "$C_SRC/tests" -p 'integration_test_*.py' -v
