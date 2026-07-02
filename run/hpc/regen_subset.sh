#!/bin/bash
#SBATCH --job-name=phase0_regen_subset
#SBATCH --time=3-00:00:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH --output=outputs/logs/regen_subset/slurm/%A/%j.out
#
# Phase 0.1 — regenerate a representative subset of forward DGs with the CURRENT
# EI ruleset (incl. ei_molecular_ion) on SLURM, one molecule per array task, then
# score the provisional explainability ceiling as a dependent job.
#
# The on-disk data/processed/fwd dumps are stale (pre-EI; no M+•), so this writes
# fresh dumps to a gitignored dir under outputs/ and leaves the stale dumps intact.
# Forward-only (--skip-backward); each task is wrapped in `/usr/bin/time -v` so the
# logs double as Phase 0.2 per-molecule cost data.
#
# Usage:
#   sbatch run/hpc/regen_subset.sh                                  # built-in ~17-mol subset
#   sbatch run/hpc/regen_subset.sh --names benzene,toluene,phenol   # custom subset
#   sbatch run/hpc/regen_subset.sh --all-with-spectrum              # full corpus (~150 mols)
set -euo pipefail

SUBMIT_DIR="${SLURM_SUBMIT_DIR:-.}"
REPO_ROOT="$(cd "$SUBMIT_DIR" && pwd)"
source "$REPO_ROOT/src/paths.env"

REGEN_REL="outputs/phase0/regen_subset"
CEIL_REL="outputs/phase0/subset"
MANIFEST="$REPO_ROOT/$REGEN_REL/manifest.tsv"

JOB_GROUP_ID="${SLURM_ARRAY_JOB_ID:-${SLURM_JOB_ID:-local}}"
LOG_DIR="$REPO_ROOT/$LOGS_DIR_REL/regen_subset/slurm/${JOB_GROUP_ID}"

# --- phase: dependent ceiling job -------------------------------------------- #
if [ "${1:-}" = "ceiling" ]; then
  mkdir -p "$REPO_ROOT/$CEIL_REL"
  apptainer exec \
    --bind "$REPO_ROOT/$SRC_DIR_REL:$C_SRC" \
    --bind "$REPO_ROOT/$DATA_DIR_REL:$C_DATA" \
    --bind "$REPO_ROOT/$OUTPUTS_DIR_REL:$C_OUTPUTS" \
    --env PYTHONPATH="$C_APP" \
    "$REPO_ROOT/$SIF" \
    python "$C_SRC/data_generation/phase0/run_ceiling.py" \
      --fwd-dir "$C_OUTPUTS/phase0/regen_subset/fwd" \
      --out-dir "$C_OUTPUTS/phase0/subset"
  exit 0
fi

# --- phase: array task (regenerate one molecule) ----------------------------- #
if [ -n "${SLURM_ARRAY_TASK_ID:-}" ]; then
  mkdir -p "$LOG_DIR"
  LINE="$(sed -n "${SLURM_ARRAY_TASK_ID}p" "$MANIFEST" | tr -d '\r')"
  if [ -z "$LINE" ]; then echo "empty manifest line ${SLURM_ARRAY_TASK_ID}; skipping"; exit 0; fi
  IFS=$'\t' read -r NAME SMILES <<< "$LINE"
  if [ -z "${NAME:-}" ] || [ -z "${SMILES:-}" ]; then echo "bad manifest line: $LINE" >&2; exit 1; fi
  THREADS="${SLURM_CPUS_PER_TASK:-1}"
  OUTFILE="${LOG_DIR}/${SLURM_ARRAY_TASK_ID}__${NAME}.out"

  /usr/bin/time -v \
  srun --cpu-bind=cores \
  apptainer exec \
    --bind "$REPO_ROOT/$SRC_DIR_REL:$C_SRC" \
    --bind "$REPO_ROOT/$DATA_DIR_REL:$C_DATA" \
    --bind "$REPO_ROOT/$OUTPUTS_DIR_REL:$C_OUTPUTS" \
    --env PYTHONPATH="$C_APP" \
    --env OMP_NUM_THREADS="$THREADS" \
    "$REPO_ROOT/$SIF" \
    python "$C_SRC/data_generation/main.py" \
      --smiles "$SMILES" \
      --name "$NAME" \
      --output-dir "$C_OUTPUTS/phase0/regen_subset" \
      --spectra-folder "$C_PARQUET" \
      --number-threads "$THREADS" \
      --subgroup-diag \
      --skip-backward \
    >"$OUTFILE" 2>&1
  exit 0
fi

# --- phase: submit (build manifest, launch array + dependent ceiling) -------- #
mkdir -p "$REPO_ROOT/$REGEN_REL/fwd" "$REPO_ROOT/$CEIL_REL" \
         "$REPO_ROOT/$LOGS_DIR_REL/regen_subset/slurm"

# Map array index -> molecule (name<TAB>smiles), read from the existing dumps.
apptainer exec \
  --bind "$REPO_ROOT/$SRC_DIR_REL:$C_SRC" \
  --bind "$REPO_ROOT/$DATA_DIR_REL:$C_DATA" \
  --bind "$REPO_ROOT/$OUTPUTS_DIR_REL:$C_OUTPUTS" \
  --env PYTHONPATH="$C_APP" \
  "$REPO_ROOT/$SIF" \
  python "$C_SRC/data_generation/phase0/regen_subset.py" \
    --emit-manifest "$C_OUTPUTS/phase0/regen_subset/manifest.tsv" "$@"

N="$(wc -l < "$MANIFEST")"
if [ "$N" -le 0 ]; then echo "empty manifest; nothing to submit" >&2; exit 1; fi

echo "Submitting regen array 1..${N} over $MANIFEST"
ARRAY_JID="$(sbatch --parsable --array=1-"${N}" "$0")"
echo "  array job:   $ARRAY_JID"
CEIL_JID="$(sbatch --parsable --dependency=afterany:"${ARRAY_JID}" "$0" ceiling)"
echo "  ceiling job: $CEIL_JID  (afterany:$ARRAY_JID)"
echo "Results -> $CEIL_REL/{ceiling_per_molecule.csv,ceiling_summary.json} after completion"
