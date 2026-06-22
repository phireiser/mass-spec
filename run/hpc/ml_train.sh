#!/bin/bash
#SBATCH --job-name=mol_train
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=256G
#SBATCH --time=40:00:00
#SBATCH --output=outputs/logs/train/%j.out
#SBATCH --error=outputs/logs/train/%j.err

# Usage:
# sbatch run/hpc/train.sh
# Optional overrides:
# sbatch --export=EPOCHS_FWD=5000,EPOCHS_BWD=5000 run/hpc/train.sh

set -euo pipefail

SUBMIT_DIR="${SLURM_SUBMIT_DIR:-.}"
REPO_ROOT="$(cd "$SUBMIT_DIR" && pwd)"
source "$REPO_ROOT/src/paths.env"

EPOCHS_FWD="${EPOCHS_FWD:-10000}"
EPOCHS_BWD="${EPOCHS_BWD:-10000}"

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
      "${WANDB_ARGS[@]}"

echo "======================================================================"
echo "Training complete!"
echo "Checkpoints saved to: $REPO_ROOT/$CHECKPOINT_DIR_REL"
echo "Completed: $(date)"
echo "======================================================================"
