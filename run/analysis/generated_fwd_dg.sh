#!/bin/bash
source "$(dirname "$0")/../config/setup.sh"

python src/data_generation/analyze.py --name "toluene" \
  --smiles "CC1=CC=CC=C1" \
  --dir "$REPO_ROOT/$PROCESSED_DIR_REL/fwd"
