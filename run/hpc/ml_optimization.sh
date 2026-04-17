#!/usr/bin/env bash
#SBATCH --job-name=hyper_optim
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=100G
#SBATCH --time=40:00:00
#SBATCH --output=outputs/logs/optim/%j.out
#SBATCH --error=outputs/logs/optim/%j.err

set -e

# if execution @ LISC
if [ -d /lisc/data ]; then
  module load Conda
  conda activate /lisc/data/scratch/tbi/reiser/env
  home_dir="/lisc/home/user/reiser/"
elif [ -d /scratch/reiserp/ ]; then # if execution happens @ TBI
  conda activate /scratch/reiserp/env
  home_dir="/home/mescalin/reiserp/"
fi

PROJ_DIR="$home_dir""Nextcloud/studium/computationalScience/thesis/mol"

if [[ "$PWD" != "$PROJ_DIR" ]]; then
    echo "Run this script from $PROJ_DIR" >&2
    exit 1
fi

# Ensure imports  resolve correctly
export PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}"

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
python "$PWD/src/machine_learning/optimization/hyperparameter_optimization.py" \
  --epochs_fwd "$EPOCHS_FWD" \
  --epochs_bwd "$EPOCHS_BWD" \
  --train_script "$PWD/src/machine_learning/main.py" \
  --output_dir "$PWD/outputs/best_params"

echo "Bayesian optimization complete!"
echo "Results saved to: best_hyperparams.json"
echo ""
echo "Formatting Results:"
python "$PWD/src/machine_learning/optimization/format_best_params.py" --input outputs/best_params/best_hyperparams.json --format txt
python "$PWD/src/machine_learning/optimization/format_best_params.py" --input outputs/best_params/best_hyperparams.json --format sh

echo "Best parameters formatted!"
echo ""
echo "Next Steps:"
echo "1. Review text report: cat outputs/best_params/best_hyperparams.txt"
echo "2. Run final training: ./outputs/best_params/best_hyperparams.sh --epochs_fwd 100 --epochs_bwd 100"

echo ""
echo "======================================================================"
echo "Completed: $(date)"
echo "======================================================================"
echo ""

