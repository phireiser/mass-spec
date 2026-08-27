#!/bin/bash
# Compile the curated data/mechanisms corpus into mod.Rule fragmentation
# rules and write them as a static .py module, in the same style as the
# hand-authored files in src/data_generation/rules.
#
# Writes src/data_generation/mechanisms/generated_rules.py, which
# src/data_generation/mechanisms/__init__.py imports (and therefore what
# `main.py --rule-source mechanisms` actually uses). Re-run this whenever
# data/mechanisms/records/*.json or src/data_generation/mechanisms/
# dfs_writer.py changes -- the output file is generated, never hand-edited.
#
# Needs `mod` (it is what actually validates every generated DFS string), so
# this runs inside mol-spectro.sif.
#
# Usage:
#   bash run/mechanisms/write_generated_rules.sh
#   bash run/mechanisms/write_generated_rules.sh --out /tmp/generated_rules.py
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
set -a; source "$REPO_ROOT/src/paths.env"; set +a

apptainer exec \
  --bind "$REPO_ROOT/$SRC_DIR_REL:$C_SRC" \
  --bind "$REPO_ROOT/$DATA_DIR_REL:$C_DATA" \
  --env PYTHONPATH="$C_APP" \
  "$REPO_ROOT/$SIF_REL" \
  python -m src.data_generation.mechanisms.write_generated_rules "$@"
