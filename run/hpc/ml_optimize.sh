#!/bin/bash
#SBATCH --job-name=hyper_optim
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=256G
#SBATCH --time=48:00:00
#SBATCH --output=data/outputs/logs/optim/%j.out
#SBATCH --error=data/outputs/logs/optim/%j.err

# Usage:
# sbatch run/hpc/ml_optimize.sh
# Optional overrides:
# sbatch --export=EPOCHS_FWD=1000,EPOCHS_BWD=1000,TRIAL_TIMEOUT=5400 run/hpc/ml_optimize.sh
#
# Epochs here are an HPO ranking budget, not a final-training budget: the
# curriculum saturates by ~epoch 15, so a few hundred epochs suffice to compare
# configs. Retrain the winner at full epochs with run/hpc/ml_train.sh afterwards.
# A trial exceeding TRIAL_TIMEOUT is pruned, so keep epochs small enough to finish.

set -euo pipefail

SUBMIT_DIR="${SLURM_SUBMIT_DIR:-.}"
REPO_ROOT="$(cd "$SUBMIT_DIR" && pwd)"
source "$REPO_ROOT/src/paths.env"

EPOCHS_FWD="${EPOCHS_FWD:-500}"
EPOCHS_BWD="${EPOCHS_BWD:-500}"
TRIAL_TIMEOUT="${TRIAL_TIMEOUT:-3600}"

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
echo "Per-trial timeout: ${TRIAL_TIMEOUT}s"
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
    --env TRIAL_TIMEOUT="$TRIAL_TIMEOUT" \
    "${WANDB_ENV[@]}" \
    "$SIF" \
    python "$C_SRC/machine_learning/optimization/hyperparameter_optimization.py" \
      --epochs_fwd "$EPOCHS_FWD" \
      --epochs_bwd "$EPOCHS_BWD" \
      --trial_timeout "$TRIAL_TIMEOUT" \
      --train_script "$C_SRC/machine_learning/main.py" \
      --output_dir "$C_OUTPUTS/best_params" \
      "${WANDB_ARGS[@]}"

echo "======================================================================"
echo "Bayesian optimization complete!"
echo "Artifacts written to $REPO_ROOT/$BEST_PARAMS_DIR_REL :"
echo "  best_params_<timestamp>.json       (full sweep record)"
echo "  best_hyperparams_<timestamp>.yaml  (winning config, dated)"
echo "  best_hyperparams_latest.yaml       (default consumed by ml_train.sh)"
echo ""
echo "Next: retrain the winner at full epochs with"
echo "  sbatch --export=EPOCHS_FWD=10000,EPOCHS_BWD=10000 run/hpc/ml_train.sh"
echo "Completed: $(date)"
echo "======================================================================"
