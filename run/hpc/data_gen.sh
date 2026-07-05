#!/bin/bash
#SBATCH --job-name=data_gen_fragment
#SBATCH --time=7-00:30:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --output=outputs/logs/data_gen/slurm/%A/%j.out

# Usage:
# sbatch run/hpc/data_gen.sh


set -euo pipefail

# Use SLURM_SUBMIT_DIR to find original location (works when SLURM copies script to compute node)
SUBMIT_DIR="${SLURM_SUBMIT_DIR:-.}"
REPO_ROOT="$(cd "$SUBMIT_DIR" && pwd)"
source "$REPO_ROOT/src/paths.env"

# Directories and files
DATADIR="$REPO_ROOT/$PROCESSED_DIR_REL"
# Definition CSV (name,smiles,category). Override with DEFINITION_FILE to run a
# different batch, e.g. the Phase-1 decoys:
#   DEFINITION_FILE=data/decoys_wave1.csv sbatch run/hpc/data_gen.sh
# A relative override is resolved against the repo root. Exported so the
# array self-resubmit below inherits it.
if [ -n "${DEFINITION_FILE:-}" ] && [ "${DEFINITION_FILE#/}" = "${DEFINITION_FILE}" ]; then
  DEFINITION_FILE="$REPO_ROOT/$DEFINITION_FILE"
fi
DEFINITION_FILE="${DEFINITION_FILE:-$REPO_ROOT/$CSV_PATH_REL}"
export DEFINITION_FILE
JOB_GROUP_ID="${SLURM_ARRAY_JOB_ID:-}"
if [ -z "$JOB_GROUP_ID" ]; then
  JOB_GROUP_ID="${SLURM_JOB_ID:-local}"
fi
LOG_DIR="$REPO_ROOT/$LOGS_DIR_REL/data_gen/slurm/${JOB_GROUP_ID}"

mkdir -p "$LOG_DIR"
mkdir -p "$DATADIR/fwd"
mkdir -p "$DATADIR/bwd"
# Bind-mount target must exist on host before apptainer mounts it
# (the Parquet store lives under outputs/, so the $C_OUTPUTS bind covers it)
mkdir -p "$REPO_ROOT/$PARQUET_DIR_REL"
mkdir -p "$REPO_ROOT/$OUTPUTS_DIR_REL"

# Count lines
TOTAL_LINES="$(wc -l < "$DEFINITION_FILE")"
DATA_LINES="$(( TOTAL_LINES - 1 ))"
if [ "$DATA_LINES" -le 0 ]; then
  echo "No data lines in $DEFINITION_FILE" >&2
  exit 1
fi

# Self-resubmit as array
if [ -z "${SLURM_ARRAY_TASK_ID:-}" ]; then
  echo "Submitting as array 1..${DATA_LINES}"
  sbatch --array=1-"${DATA_LINES}" "$0"
  exit 0
fi

# Parse CSV line for this task
LINE="$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" "$DEFINITION_FILE" | tr -d '\r')"
if [ -z "$LINE" ]; then
  echo "Empty line for task ${SLURM_ARRAY_TASK_ID}; skipping." >&2
  exit 0
fi

IFS=, read -r NAME SMILES CATEGORY <<< "$LINE"
if [ -z "${NAME:-}" ] || [ -z "${SMILES:-}" ]; then
  echo "Missing NAME or SMILES on line: $LINE" >&2
  exit 1
fi

slugify() {
  echo "$1" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/_/g; s/^_+|_+$//g'
}
NAME_SLUG="$(slugify "$NAME")"
OUTFILE="${LOG_DIR}/${SLURM_ARRAY_TASK_ID}__${NAME_SLUG}.out"

# Thread binding
THREADS="${SLURM_CPUS_PER_TASK:-1}"

/usr/bin/time -v \
srun --cpu-bind=cores \
apptainer exec \
    --bind "$REPO_ROOT/$SRC_DIR_REL:$C_SRC" \
    --bind "$REPO_ROOT/$PROCESSED_DIR_REL:$C_PROCESSED" \
    --bind "$REPO_ROOT/$OUTPUTS_DIR_REL:$C_OUTPUTS" \
    --bind "$REPO_ROOT/$CSV_PATH_REL:$C_CSV:ro" \
    --env PYTHONPATH="$C_APP" \
    --env OMP_NUM_THREADS="$THREADS" \
    --env MKL_NUM_THREADS="$THREADS" \
    --env OPENBLAS_NUM_THREADS="$THREADS" \
    --env NUMEXPR_NUM_THREADS="$THREADS" \
    "$SIF" \
    python "$C_SRC/data_generation/main.py" \
      --smiles "$SMILES" \
      --name "$NAME" \
      --output-dir "$C_PROCESSED" \
      --spectra-folder "$C_PARQUET" \
      --number-threads "$THREADS" \
      --subgroup-diag \
      --avoid-reprocessing \
      --name-by-cas \
  >"$OUTFILE" 2>&1
