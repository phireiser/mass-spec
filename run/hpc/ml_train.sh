#!/bin/bash
#SBATCH --job-name=mol_train
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=256G
#SBATCH --time=48:00:00
#SBATCH --output=data/outputs/logs/train/%j.out
#SBATCH --error=data/outputs/logs/train/%j.err

# Usage:
# sbatch run/hpc/ml_train.sh
# Optional overrides:
# sbatch --export=EPOCHS_FWD=5000,EPOCHS_BWD=5000 run/hpc/ml_train.sh
#
# By default this trains the most recent sweep's best config
# (best_hyperparams_latest.yaml, written by ml_optimize.sh). Override with
# HPARAMS_HOST=/path/to/best_hyperparams_<stamp>.yaml to pin a specific sweep,
# or point it at a missing path to train main.py's built-in default hyperparameters.

set -euo pipefail

SUBMIT_DIR="${SLURM_SUBMIT_DIR:-.}"
REPO_ROOT="$(cd "$SUBMIT_DIR" && pwd)"
source "$REPO_ROOT/src/paths.env"

EPOCHS_FWD="${EPOCHS_FWD:-10000}"
EPOCHS_BWD="${EPOCHS_BWD:-10000}"

# Tuned hyperparameters from the sweep. Check existence on the host path, but
# pass main.py the in-container path (data/outputs is bound to $C_OUTPUTS).
HPARAMS_HOST="${HPARAMS_HOST:-$REPO_ROOT/$BEST_PARAMS_DIR_REL/best_hyperparams_latest.yaml}"
HPARAMS_CONTAINER="$C_OUTPUTS/best_params/$(basename "$HPARAMS_HOST")"
HPARAMS_ARGS=()
if [[ -f "$HPARAMS_HOST" ]]; then
    HPARAMS_ARGS=(--hparams "$HPARAMS_CONTAINER")
fi

# Optional Weights & Biases tracking (online-first, offline fallback).
WANDB_GROUP_PREFIX="train"
source "$REPO_ROOT/run/hpc/wandb_setup.sh"

mkdir -p "$REPO_ROOT/$LOGS_DIR_REL/train"
mkdir -p "$REPO_ROOT/$CHECKPOINT_DIR_REL"
mkdir -p "$REPO_ROOT/$OUTPUTS_DIR_REL"

echo "======================================================================"
echo "Model Training Job"
echo "======================================================================"
echo "Epochs (forward): $EPOCHS_FWD"
echo "Epochs (backward): $EPOCHS_BWD"
if [[ -f "$HPARAMS_HOST" ]]; then
    echo "Hyperparameters: $HPARAMS_HOST"
else
    echo "Hyperparameters: NONE FOUND at $HPARAMS_HOST -> using main.py defaults"
fi
echo "SIF: $SIF"
echo "Node: $(hostname)"
echo "GPU: $CUDA_VISIBLE_DEVICES"
echo "Started: $(date)"
echo "======================================================================"

apptainer exec --nv \
    --bind "$REPO_ROOT/$SRC_DIR_REL:$C_SRC" \
    --bind "$REPO_ROOT/$DATA_DIR_REL:$C_DATA" \
    --bind "$REPO_ROOT/$OUTPUTS_DIR_REL:$C_OUTPUTS" \
    --env PYTHONPATH="$C_APP" \
    --env CUDA_VISIBLE_DEVICES=0 \
    --env EPOCHS_FWD="$EPOCHS_FWD" \
    --env EPOCHS_BWD="$EPOCHS_BWD" \
    "${WANDB_ENV[@]}" \
    "$SIF" \
    python "$C_SRC/machine_learning/main.py" \
      --epochs_fwd "$EPOCHS_FWD" \
      --epochs_bwd "$EPOCHS_BWD" \
      --output_dir "$C_OUTPUTS/checkpoints" \
      "${HPARAMS_ARGS[@]}" \
      "${WANDB_ARGS[@]}"

echo "======================================================================"
echo "Training complete!"
echo "Checkpoints saved to: $REPO_ROOT/$CHECKPOINT_DIR_REL"
echo "Completed: $(date)"
echo "======================================================================"
