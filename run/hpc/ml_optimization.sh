#!/usr/bin/env bash
#SBATCH --job-name=hyper_optim
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=100G
#SBATCH --time=40:00:00
#SBATCH --output=outputs/logs/optim/%j.out
#SBATCH --error=outputs/logs/optim/%j.err

# run this script from the project root directory to ensure correct paths
# Usage:
# sbatch run/hpc/ml_optimization.sh
# Optional: override default epochs with:
# sbatch --export=EPOCHS_FWD=5000,EPOCHS_BWD=5000 run/hpc/ml_optimization.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
source "$REPO_ROOT/run/config/paths.env"

# if execution @ LISC
if [ -d /lisc/data ]; then
  module load Conda
  conda activate /lisc/data/scratch/tbi/reiser/pyenv
  home_dir="/lisc/home/user/reiser/"
elif [ -d /scratch/reiserp/ ]; then # if execution happens @ TBI
  conda activate /scratch/reiserp/env
  home_dir="/home/mescalin/reiserp/"
fi

PROJ_DIR="$REPO_ROOT"

if [[ "$PWD" != "$PROJ_DIR" ]]; then
    echo "Run this script from $PROJ_DIR" >&2
    exit 1
fi

# Ensure imports  resolve correctly
export PYTHONPATH="$REPO_ROOT${PYTHONPATH:+:$PYTHONPATH}"

# Default optimization mode (can be overridden with: sbatch --export=VARIABLE_NAME=value optimization_slurm.sh)
EPOCHS_FWD="${EPOCHS_FWD:-10000}"
EPOCHS_BWD="${EPOCHS_BWD:-10000}"

echo "======================================================================"
echo "Hyperparameter Optimization Job with Optuna"
echo "======================================================================"
echo "Epochs (forward): $EPOCHS_FWD"
echo "Epochs (backward): $EPOCHS_BWD"
echo "Started: $(date)"
echo "======================================================================"
echo ""

echo "Intelligent exploration of high dimensional hyperparameter space"
echo ""

# Check if optuna is installed
if ! python -c "import optuna" 2>/dev/null; then
    echo "Error: Optuna not installed"
    echo "Install with: pip install optuna pyyaml"
    exit 1
fi

# Allow caller to specify n_trials/epochs via EXTRA_ARGS
python "$REPO_ROOT/$SRC_DIR_REL/machine_learning/optimization/hyperparameter_optimization.py" \
  --epochs_fwd "$EPOCHS_FWD" \
  --epochs_bwd "$EPOCHS_BWD" \
  --train_script "$REPO_ROOT/$SRC_DIR_REL/machine_learning/main.py" \
  --output_dir "$REPO_ROOT/$BEST_PARAMS_DIR_REL"

echo "Bayesian optimization complete!"
echo "Results saved to: best_hyperparams.json"
echo ""
echo "Formatting Results:"
python "$REPO_ROOT/$SRC_DIR_REL/machine_learning/optimization/format_best_params.py" --input "$REPO_ROOT/$BEST_PARAMS_DIR_REL/best_hyperparams.json" --format txt
python "$REPO_ROOT/$SRC_DIR_REL/machine_learning/optimization/format_best_params.py" --input "$REPO_ROOT/$BEST_PARAMS_DIR_REL/best_hyperparams.json" --format sh

echo "Best parameters formatted!"
echo ""
echo "Next Steps:"
echo "1. Review text report: cat $REPO_ROOT/$BEST_PARAMS_DIR_REL/best_hyperparams.txt"
echo "2. Run final training: $REPO_ROOT/$BEST_PARAMS_DIR_REL/best_hyperparams.sh --epochs_fwd 100 --epochs_bwd 100"

echo ""
echo "======================================================================"
echo "Completed: $(date)"
echo "======================================================================"
echo ""

