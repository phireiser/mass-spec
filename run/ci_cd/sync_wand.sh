#!/bin/bash
# Upload W&B runs that were recorded in offline mode.
#
# Training jobs log online when the compute node has internet and fall back to
# offline otherwise (see run/hpc/wandb_setup.sh). Run this afterwards from a shell
# WITH internet (e.g. a login node) to flush any leftover offline runs to the cloud.
#
# Usage:
#   run/ci_cd/sync_wand.sh        # sync every offline run under outputs/wandb

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
source "$REPO_ROOT/src/paths.env"

WANDB_SECRET_FILE="${WANDB_SECRET_FILE:-$REPO_ROOT/.secrets/wandb.env}"
if [ -f "$WANDB_SECRET_FILE" ]; then
  # shellcheck disable=SC1090
  source "$WANDB_SECRET_FILE"   # must export WANDB_API_KEY
else
  echo "No secret file at '$WANDB_SECRET_FILE'; export WANDB_API_KEY first." >&2
  exit 1
fi

WANDB_RUNS_DIR="$REPO_ROOT/$OUTPUTS_DIR_REL/wandb"
if [ ! -d "$WANDB_RUNS_DIR" ]; then
  echo "No wandb directory at $WANDB_RUNS_DIR; nothing to sync."
  exit 0
fi

shopt -s nullglob
runs=("$WANDB_RUNS_DIR"/offline-run-*)
if [ "${#runs[@]}" -eq 0 ]; then
  echo "No offline runs found in $WANDB_RUNS_DIR; nothing to sync."
  exit 0
fi

echo "Syncing ${#runs[@]} offline W&B run(s) from $WANDB_RUNS_DIR ..."

# wandb lives inside the image; run the CLI there. The login node has internet,
# so force online mode regardless of how the run was originally recorded.
apptainer exec \
    --bind "$REPO_ROOT/$OUTPUTS_DIR_REL:$C_OUTPUTS" \
    --env WANDB_API_KEY="${WANDB_API_KEY:-}" \
    --env WANDB_MODE=online \
    --env WANDB_DIR="$C_OUTPUTS" \
    "$REPO_ROOT/$SIF" \
    wandb sync --sync-all "$C_OUTPUTS/wandb"

echo "Sync complete."
