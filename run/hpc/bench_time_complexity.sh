#!/bin/bash
#SBATCH --job-name=bench_time_complexity
#SBATCH --time=0-01:00:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --output=data/outputs/logs/bench_time_complexity/%A_%a.out

# Re-measure per-molecule fragmentation cost with the CURRENT pipeline, one
# molecule per array task, for the same molecule set as the 2026-04 table in
# data/outputs/metrics/MolecuelProcessingTimeTableComplexety.csv.
#
# Each task writes one JSON line (the bench script's own output) to
# data/outputs/metrics/time_complexity_new/<task>__<slug>.json. A task that hits
# the wall limit leaves no JSON and is treated as right-censored downstream.
#
# Usage:  sbatch run/hpc/bench_time_complexity.sh
#
# The DG is built through strategy.make_fwd_strategy exactly as main.py builds
# it (bench_datagen_strategy.py --config full), single-threaded, so the number
# is the shipping strategy's build time without dump writing.

set -euo pipefail

SUBMIT_DIR="${SLURM_SUBMIT_DIR:-.}"
REPO_ROOT="$(cd "$SUBMIT_DIR" && pwd)"
set -a; source "$REPO_ROOT/src/paths.env"; set +a

INPUT="$REPO_ROOT/$METRICS_DIR_REL/time_complexity_bench_input.csv"
OUTDIR="$REPO_ROOT/$METRICS_DIR_REL/time_complexity_new"
mkdir -p "$OUTDIR" "$REPO_ROOT/$LOGS_DIR_REL/bench_time_complexity"

DATA_LINES="$(( $(wc -l < "$INPUT") - 1 ))"

# Self-resubmit as an array, one task per molecule (same pattern as data_gen.sh).
if [ -z "${SLURM_ARRAY_TASK_ID:-}" ]; then
  echo "Submitting as array 1..${DATA_LINES}"
  sbatch --array=1-"${DATA_LINES}" "$0"
  exit 0
fi

LINE="$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" "$INPUT" | tr -d '\r')"
IFS=, read -r NAME SMILES OLD_S <<< "$LINE"
[ -n "${NAME:-}" ] && [ -n "${SMILES:-}" ] || { echo "bad line: $LINE" >&2; exit 1; }

apptainer exec \
    --bind "$REPO_ROOT/$SRC_DIR_REL:$C_SRC" \
    --env PYTHONPATH="$C_APP" \
    --env OMP_NUM_THREADS=1 \
    "$REPO_ROOT/$SIF_REL" \
    python "$C_SRC/plot/bench_datagen_strategy.py" \
      --config full --smiles "$SMILES" --name "$NAME" --threads 1 \
  | tail -n 1 > "$OUTDIR/${SLURM_ARRAY_TASK_ID}__${NAME}.json"
