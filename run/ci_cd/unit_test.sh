#!/bin/bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
set -a; source "$REPO_ROOT/src/paths.env"; set +a

# execute tests
apptainer exec \
    --bind "$REPO_ROOT/$SRC_DIR_REL:$C_SRC" \
    "$REPO_ROOT/$SIF_REL" \
    python3 -m unittest discover -s $C_TESTS -p 'unit_test_*.py'
