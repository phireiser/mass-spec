#!/bin/bash



if [ -d /lisc/data ]; then # if execution happens @ LISC
  module load Conda
  CONDA_ENV_PATH="/lisc/data/scratch/tbi/reiser/pyenv"
elif [ -d /scratch/reiserp/ ]; then # if execution happens @ TBI
  CONDA_ENV_PATH="/scratch/reiserp/env"
fi

# Check if conda command is available, if not, error out
if command -v conda &> /dev/null; then
	conda activate "$CONDA_ENV_PATH"
else
    echo "Conda command not found"
    exit 1
fi


# execute tests

python3 -m unittest discover -s tests -p 'test_*.py'
