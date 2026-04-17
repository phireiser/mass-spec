#!/bin/bash
#SBATCH --job-name=data_gen_fragment
#SBATCH --time=0-00:30:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=20G
#SBATCH --output=outputs/logs/data_gen/slurm/%A/%j.out


###SBATCH --time=29-00:30:00

if [ -d /lisc/data ]; then # if execution happens @ LISC
  module load Conda
  conda activate $CONDA_ENV_LISC
elif [ -d /scratch/reiserp/ ]; then # if execution happens @ TBI
  conda activate $CONDA_ENV_TBI
fi


PROJ_DIR="$HOME/$PROJ_DIR_REL"

if [[ "$PWD" != "$PROJ_DIR" ]]; then
    echo "Run this script from $PROJ_DIR" >&2
    exit 1
fi


# Ensure imports  resolve correctly
export PYTHONPATH="$REPO_ROOT${PYTHONPATH:+:$PYTHONPATH}"


set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
source "$REPO_ROOT/run/config/paths.env"

# Directories and files
DATADIR="$REPO_ROOT/$PROCESSED_DIR_REL/"
DEFINITION_FILE="$REPO_ROOT/$DATA_DIR_REL/compounds.csv"
JOB_GROUP_ID="${SLURM_ARRAY_JOB_ID-}"
if [ -z "$JOB_GROUP_ID" ]; then
  JOB_GROUP_ID="${SLURM_JOB_ID-local}"
fi
LOG_DIR="$REPO_ROOT/$LOGS_DIR_REL/data_gen/slurm/${JOB_GROUP_ID}"
SCRIPT_DIR="$REPO_ROOT/$SRC_DIR_REL/data_generation"

mkdir -p "$LOG_DIR"
mkdir -p "$DATADIR"
mkdir -p "$DATADIR"/fwd
mkdir -p "$DATADIR"/bwd

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

OUTFILE="${LOG_DIR}/${SLURM_ARRAY_TASK_ID}__${NAME_SLUG}.out"

# Threads: match allocation
THREADS="${SLURM_CPUS_PER_TASK:-1}"
export OMP_NUM_THREADS="$THREADS" MKL_NUM_THREADS="$THREADS" OPENBLAS_NUM_THREADS="$THREADS" NUMEXPR_NUM_THREADS="$THREADS"

/usr/bin/time -v \
srun --cpu-bind=cores \
python \
  "${SCRIPT_DIR}/main.py" \
    --smiles "$SMILES" \
    --name "$NAME" \
    --output-dir "$DATADIR" \
    --spectra-folder "$REPO_ROOT/$NIST_SPECTRA_DIR_REL" \
    --number-threads "$THREADS" \
    --subgroup-diag \
    --avoid-reprocessing \
  >"$OUTFILE" 2>&1
