#!/bin/bash

# script to set up environment variables and paths for the project; should be sourced by other scripts

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
source "$REPO_ROOT/run/config/paths.env"

if [ -d /lisc/data ]; then # if execution happens @ LISC
  module load Conda
  conda activate $CONDA_ENV_LISC
elif [ -d /scratch/reiserp/ ]; then # if execution happens @ TBI
  conda activate $CONDA_ENV_TBI
fi


PROJ_DIR="$HOME/$PROJ_DIR_REL"

if [[ "$PWD" != "$HOME/$PROJ_DIR_REL" ]]; then
    echo "Run this script from $PROJ_DIR" >&2
    echo "you are here: $PWD" >&2
    echo "expected: $PROJ_DIR" >&2
    exit 1
fi

# Ensure imports  resolve correctly
export PYTHONPATH="$REPO_ROOT${PYTHONPATH:+:$PYTHONPATH}"
