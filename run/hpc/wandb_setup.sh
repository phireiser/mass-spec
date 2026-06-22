# Shared Weights & Biases setup, sourced by the HPC launch scripts.
#
# Strategy: prefer ONLINE logging; automatically fall back to OFFLINE if this
# node cannot reach the W&B API (then flush later with run/ci_cd/sync_wand.sh).
#
# Requires (already set by the caller, via src/paths.env):
#   REPO_ROOT, OUTPUTS_DIR_REL, C_OUTPUTS
# Optional inputs:
#   WANDB_GROUP_PREFIX  run-group prefix, e.g. "train" or "optuna" (default "run")
#   USE_WANDB           auto (default) | 0 (force off) | 1 (require, fail if no key)
#   WANDB_SECRET_FILE   file that exports WANDB_API_KEY (default .secrets/wandb.env)
#   WANDB_MODE          force "online"/"offline" and skip the connectivity probe
# Produces (bash arrays for the caller to splice into the apptainer command):
#   WANDB_ARGS   CLI flags for the python entrypoint (e.g. --wandb)
#   WANDB_ENV    --env flags for `apptainer exec`

USE_WANDB="${USE_WANDB:-auto}"
WANDB_SECRET_FILE="${WANDB_SECRET_FILE:-$REPO_ROOT/.secrets/wandb.env}"
WANDB_GROUP_PREFIX="${WANDB_GROUP_PREFIX:-run}"
WANDB_ARGS=()
WANDB_ENV=()

if [ "$USE_WANDB" = "0" ]; then
  echo "wandb: disabled (USE_WANDB=0)"
  return 0
fi

if [ ! -f "$WANDB_SECRET_FILE" ]; then
  if [ "$USE_WANDB" = "1" ]; then
    echo "wandb: USE_WANDB=1 but secret file '$WANDB_SECRET_FILE' not found" >&2
    exit 1
  fi
  echo "wandb: no secret file at '$WANDB_SECRET_FILE'; tracking disabled" >&2
  return 0
fi

# shellcheck disable=SC1090
source "$WANDB_SECRET_FILE"   # must export WANDB_API_KEY

# Online-first: probe the W&B API and fall back to offline if unreachable.
if [ -z "${WANDB_MODE:-}" ]; then
  if command -v curl >/dev/null 2>&1 && curl -s --max-time 5 -o /dev/null https://api.wandb.ai; then
    WANDB_MODE="online"
    echo "wandb: api.wandb.ai reachable -> online mode"
  else
    WANDB_MODE="offline"
    echo "wandb: api.wandb.ai unreachable -> offline mode (flush later: run/ci_cd/sync_wand.sh)"
  fi
fi

# Runs land in $OUTPUTS_DIR_REL/wandb/ on the host (WANDB_DIR + wandb's own subdir).
mkdir -p "$REPO_ROOT/$OUTPUTS_DIR_REL/wandb"
WANDB_ARGS=(--wandb)
WANDB_ENV=(
  --env WANDB_API_KEY="${WANDB_API_KEY:-}"
  --env WANDB_MODE="$WANDB_MODE"
  --env WANDB_PROJECT="${WANDB_PROJECT:-mol-spectro}"
  --env WANDB_RUN_GROUP="${WANDB_GROUP_PREFIX}-${SLURM_JOB_ID:-local}"
  --env WANDB_DIR="$C_OUTPUTS"
  --env WANDB_CONFIG_DIR="$C_OUTPUTS/wandb"
  --env WANDB_CACHE_DIR="$C_OUTPUTS/wandb/.cache"
)
