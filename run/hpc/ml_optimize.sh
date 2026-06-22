#!/bin/bash
#SBATCH --job-name=hyper_optim
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=256G
#SBATCH --time=40:00:00
#SBATCH --output=outputs/logs/optim/%j.out
#SBATCH --error=outputs/logs/optim/%j.err

# Usage:
# sbatch run/hpc/ml_optimization.sh
# Optional: override default epochs with:
# sbatch --export=EPOCHS_FWD=5000,EPOCHS_BWD=5000 run/hpc/ml_optimization.sh

set -euo pipefail

SUBMIT_DIR="${SLURM_SUBMIT_DIR:-.}"
REPO_ROOT="$(cd "$SUBMIT_DIR" && pwd)"
source "$REPO_ROOT/src/paths.env"

EPOCHS_FWD="${EPOCHS_FWD:-10000}"
EPOCHS_BWD="${EPOCHS_BWD:-10000}"

# Optional Weights & Biases tracking: each Optuna trial becomes its own run
# (online-first, offline fallback), grouped together so the sweep is browsable.
WANDB_GROUP_PREFIX="optuna"
source "$REPO_ROOT/run/hpc/wandb_setup.sh"

mkdir -p "$REPO_ROOT/$BEST_PARAMS_DIR_REL"
mkdir -p "$REPO_ROOT/$LOGS_DIR_REL/optim"
mkdir -p "$REPO_ROOT/$OUTPUTS_DIR_REL"

echo "======================================================================"
echo "Hyperparameter Optimization Job with Optuna"
echo "======================================================================"
echo "Epochs (forward): $EPOCHS_FWD"
echo "Epochs (backward): $EPOCHS_BWD"
echo "SIF: $SIF"
echo "Started: $(date)"
echo "======================================================================"

apptainer exec --nv \
    --bind "$REPO_ROOT/$SRC_DIR_REL:$C_SRC" \
    --bind "$REPO_ROOT/$OUTPUTS_DIR_REL:$C_OUTPUTS" \
    --bind "$REPO_ROOT/$DATA_DIR_REL:$C_DATA" \
    --env PYTHONPATH="$C_APP" \
    --env CUDA_VISIBLE_DEVICES=0 \
    --env EPOCHS_FWD="$EPOCHS_FWD" \
    --env EPOCHS_BWD="$EPOCHS_BWD" \
    "${WANDB_ENV[@]}" \
    "$SIF" \
    python "$C_SRC/machine_learning/optimization/hyperparameter_optimization.py" \
      --epochs_fwd "$EPOCHS_FWD" \
      --epochs_bwd "$EPOCHS_BWD" \
      --train_script "$C_SRC/machine_learning/main.py" \
      --output_dir "$C_OUTPUTS/best_params" \
      "${WANDB_ARGS[@]}"

echo "Bayesian optimization complete!"
echo "Results saved to: best_hyperparams.json"
echo ""
echo "Formatting Results:"

apptainer exec --nv \
    --bind "$REPO_ROOT/$SRC_DIR_REL:$C_SRC" \
    --bind "$REPO_ROOT/$OUTPUTS_DIR_REL:$C_OUTPUTS" \
    --env PYTHONPATH="$C_APP" \
    "$SIF" \
    python "$C_SRC/machine_learning/optimization/format_best_params.py" \
      --input "$C_OUTPUTS/best_params/best_hyperparams.json" \
      --format txt

apptainer exec --nv \
    --bind "$REPO_ROOT/$SRC_DIR_REL:$C_SRC" \
    --bind "$REPO_ROOT/$OUTPUTS_DIR_REL:$C_OUTPUTS" \
    --env PYTHONPATH="$C_APP" \
    "$SIF" \
    python "$C_SRC/machine_learning/optimization/format_best_params.py" \
      --input "$C_OUTPUTS/best_params/best_hyperparams.json" \
      --format sh

echo "======================================================================"
echo "Next Steps:"
echo "1. Review: cat $REPO_ROOT/$BEST_PARAMS_DIR_REL/best_hyperparams.txt"
echo "2. Run training: $REPO_ROOT/$BEST_PARAMS_DIR_REL/best_hyperparams.sh"
echo "Completed: $(date)"
echo "======================================================================"
