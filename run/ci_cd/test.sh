#!/bin/bash
source "$(dirname "$0")/src/path_setup.sh"

# execute tests
apptainer exec \
    --bind "$REPO_ROOT/$SRC_DIR_REL:$C_SRC" \
    "$SIF" \
    python3 -m unittest discover -s $C_SRC/tests -p 'test_*.py'
