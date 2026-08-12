#!/bin/bash
#SBATCH --job-name=data_gen_fragment
#SBATCH --time=0-23:30:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH --output=data/outputs/logs/data_gen/slurm/%A/%j.out

# Usage:
# sbatch run/hpc/data_gen.sh


set -euo pipefail

# Use SLURM_SUBMIT_DIR to find original location (works when SLURM copies script to compute node)
SUBMIT_DIR="${SLURM_SUBMIT_DIR:-.}"
REPO_ROOT="$(cd "$SUBMIT_DIR" && pwd)"
set -a; source "$REPO_ROOT/src/paths.env"; set +a

# Optional output-dir override, so an experimental ruleset can be rebuilt into a
# side directory without clobbering the baseline dumps in data/processed. Same
# pattern as DEFINITION_FILE below; exported so the array self-resubmit inherits it.
#   PROCESSED_DIR_OVERRIDE=data/processed_reauth sbatch run/hpc/data_gen.sh
if [ -n "${PROCESSED_DIR_OVERRIDE:-}" ]; then
  PROCESSED_DIR_REL="$PROCESSED_DIR_OVERRIDE"
  export PROCESSED_DIR_OVERRIDE
fi

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

# Extra arguments appended verbatim to the main.py call. Used to run a localized-charge
# baseline alongside the (default) fully delocalized rebuild for an A/B comparison:
#   MAIN_EXTRA_ARGS=--no-migration PROCESSED_DIR_OVERRIDE=data/processed_base \
#     DEFINITION_FILE=data/migration_subset.csv sbatch run/hpc/data_gen.sh
# Exported so the array self-resubmit inherits it. Intentionally word-split on use.
export MAIN_EXTRA_ARGS="${MAIN_EXTRA_ARGS:-}"
JOB_GROUP_ID="${SLURM_ARRAY_JOB_ID:-}"
if [ -z "$JOB_GROUP_ID" ]; then
  JOB_GROUP_ID="${SLURM_JOB_ID:-local}"
fi
LOG_DIR="$REPO_ROOT/$DATAGEN_LOG_DIR_REL/${JOB_GROUP_ID}"

mkdir -p "$LOG_DIR"
# Leaf names from paths.env: $DATADIR may be a PROCESSED_DIR_OVERRIDE side tree.
mkdir -p "$DATADIR/${FWD_DIR_REL##*/}"
mkdir -p "$DATADIR/${BWD_DIR_REL##*/}"
# Bind-mount targets must exist on host before apptainer mounts them. The Parquet store is
# INPUT data, not a generated output, so it lives at data/nist_spectra and needs its own bind:
# this script does not mount data/ wholesale (only data/processed via $C_PROCESSED), so it is
# not covered by any other mount.
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

# `time -v` must sit INSIDE srun. Outside it wraps the srun client, whose rusage never
# sees the work -- the task runs under slurmstepd on the compute node, not as a child of
# srun -- so every log reported ~10 MB peak RSS and 0% CPU regardless of the molecule.
# Here it is the task command itself, so getrusage(RUSAGE_CHILDREN) walks apptainer down
# to python and reports the container's real peak (verified: 400 MB alloc -> 418816 KB).
# It stays on the host side of apptainer because the image ships no /usr/bin/time; moving
# it in front of `python` would need the `time` package added to the container build.
# This is the durable memory record -- sacct purges its accounting after a few days.
srun --cpu-bind=cores \
/usr/bin/time -v \
apptainer exec \
    --bind "$REPO_ROOT/$SRC_DIR_REL:$C_SRC" \
    --bind "$REPO_ROOT/$PROCESSED_DIR_REL:$C_PROCESSED" \
    --bind "$REPO_ROOT/$PARQUET_DIR_REL:$C_PARQUET" \
    --bind "$REPO_ROOT/$OUTPUTS_DIR_REL:$C_OUTPUTS" \
    --bind "$REPO_ROOT/$CSV_PATH_REL:$C_CSV:ro" \
    --env PYTHONPATH="$C_APP" \
    --env OMP_NUM_THREADS="$THREADS" \
    --env MKL_NUM_THREADS="$THREADS" \
    --env OPENBLAS_NUM_THREADS="$THREADS" \
    --env NUMEXPR_NUM_THREADS="$THREADS" \
    "$REPO_ROOT/$SIF_REL" \
    python "$C_SRC/data_generation/main.py" \
      --smiles "$SMILES" \
      --name "$NAME" \
      --output-dir "$C_PROCESSED" \
      --spectra-folder "$C_PARQUET" \
      --number-threads "$THREADS" \
      --subgroup-diag \
      --avoid-reprocessing \
      --name-by-cas \
      ${MAIN_EXTRA_ARGS} \
  >"$OUTFILE" 2>&1
