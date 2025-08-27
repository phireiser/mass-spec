#!/bin/bash
#SBATCH --job-name=mod_fragmenter
#SBATCH --time=31-00:30:00
#SBATCH --cpus-per-task=64
#SBATCH --mem=64G

OUTDIR="dump"

mkdir -p $OUTDIR

# Count total lines (excluding header) dynamically
TOTAL_LINES=$(($(wc -l < run_data.csv)))

# If this is the submission step, re-submit as an array job
if [ -z "$SLURM_ARRAY_TASK_ID" ]; then
    echo "Submitting as array: 1 to $TOTAL_LINES"
    sbatch --array=1-$((TOTAL_LINES)) "$0"
    exit 0
fi

# For each array task, get the corresponding CSV line
LINE=$(sed -n "$((SLURM_ARRAY_TASK_ID+1))p" run_data.csv)

# Extract fields (id,name,smiles)
ID=$(echo "$LINE" | cut -d',' -f1)
NAME=$(echo "$LINE" | cut -d',' -f2)
SMILES=$(echo "$LINE" | cut -d',' -f3)

# Use NAME in log filenames
OUTFILE="${OUTDIR}/${NAME}_${SLURM_JOB_ID}_${SLURM_ARRAY_TASK_ID}.out"

# Run your Python script
/usr/bin/time -v \
    python fragmentation/main_dump_dg.py \
        --smiles "$SMILES" \
        --name "$NAME" \
        --output-dir "./${OUTDIR}/" \
        --number-threads 64 \
    >"$OUTFILE" 2>&1
