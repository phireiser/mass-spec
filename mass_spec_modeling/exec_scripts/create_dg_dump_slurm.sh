#!/bin/bash
#SBATCH --job-name=mod_fragmenter
#SBATCH --time=29-00:30:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=10G
#SBATCH --output=dump/logs/slurm/%A_%a.out


if [ -d /lisc/data ]; then # if execution happens on cluster
  module load Conda
  conda activate /lisc/home/user/reiser/Nextcloud/studium/computationalScience/thesis/mol/env
fi


set -euo pipefail

# Directories and files
SCRIPT_DIR=~/Nextcloud/studium/computationalScience/thesis/mol/
OUTDIR="${SCRIPT_DIR}/dump"
DEFINITION_FILE="${SCRIPT_DIR}/mass_spec_modeling/exec_scripts/ms_data/compounds.csv"

mkdir -p "$OUTDIR"
mkdir -p "$OUTDIR"/logs
mkdir -p "$OUTDIR"/fwd
mkdir -p "$OUTDIR"/bwd

# Count lines (header included); data lines exclude header
TOTAL_LINES="$(wc -l < "$DEFINITION_FILE")"
DATA_LINES="$(( TOTAL_LINES - 1 ))"
if [ "$DATA_LINES" -le 0 ]; then
  echo "No data lines in $DEFINITION_FILE" >&2
  exit 1
fi

# If not launched as an array, re-submit as array over data lines
if [ -z "${SLURM_ARRAY_TASK_ID:-}" ]; then
  echo "Submitting as array 1..${DATA_LINES} (excluding header)"
  sbatch --array=1-"${DATA_LINES}" "$0"
  exit 0
fi

# Read the (header-skipping) line for this task; strip possible CRLF
LINE="$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" "$DEFINITION_FILE" | tr -d '\r')"
if [ -z "$LINE" ]; then
  echo "Empty line for task ${SLURM_ARRAY_TASK_ID}; skipping." >&2
  exit 0
fi

# Simple CSV split (assumes no quoted commas)
IFS=, read -r NAME SMILES CATEGORY <<< "$LINE"

if [ -z "${NAME:-}" ] || [ -z "${SMILES:-}" ]; then
  echo "Missing NAME or SMILES on line: $LINE" >&2
  exit 1
fi

# Slugify NAME for safe filenames
slugify() {
  echo "$1" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/_/g; s/^_+|_+$//g'
}
NAME_SLUG="$(slugify "$NAME")"

OUTFILE="${OUTDIR}/logs/${SLURM_ARRAY_TASK_ID}__${NAME_SLUG}.out"

# Threads: match allocation
THREADS="${SLURM_CPUS_PER_TASK:-1}"
export OMP_NUM_THREADS="$THREADS" MKL_NUM_THREADS="$THREADS" OPENBLAS_NUM_THREADS="$THREADS" NUMEXPR_NUM_THREADS="$THREADS"

/usr/bin/time -v \
srun --cpu-bind=cores \
python \
  "${SCRIPT_DIR}/mass_spec_modeling/exec_scripts/create_dg_dump.py" \
    --smiles "$SMILES" \
    --name "$NAME" \
    --output-dir "$OUTDIR" \
    --number-threads "$THREADS" \
    --subgroup-diag \
    --avoid-reprocessing \
  >"$OUTFILE" 2>&1
