#!/usr/bin/env bash
# Helper script to submit hyperparameter optimization jobs to SLURM

# Usage examples:
#   ./submit_optimization.sh quick      # Quick grid search (30 min)
#   ./submit_optimization.sh grid       # Full grid search (3-6 hours)
#   ./submit_optimization.sh optuna     # Bayesian optimization (overnight)

set -e

MODE="${1:-quick}"
EPOCHS_FWD="${2:-10}"
EPOCHS_BWD="${3:-10}"

if [ "$MODE" = "help" ] || [ "$MODE" = "-h" ] || [ "$MODE" = "--help" ]; then
    cat << 'EOF'
Submit hyperparameter optimization to SLURM cluster

USAGE:
    ./submit_optimization.sh [MODE] [EPOCHS_FWD] [EPOCHS_BWD]

MODES:
    quick   - Quick grid search, 8 configs, ~30 min
    grid    - Full grid search, 72 configs, 3-6 hours
    optuna  - Bayesian optimization, 30 trials, 4-8 hours
    demo    - Demo output, 1 minute (no training)

PARAMETERS:
    EPOCHS_FWD   - Forward phase epochs per trial (default: 10)
    EPOCHS_BWD   - Backward phase epochs per trial (default: 10)

EXAMPLES:
    # Quick exploration with 5 epochs per phase
    ./submit_optimization.sh quick 5 5

    # Thorough grid search with 10 epochs
    ./submit_optimization.sh grid 10 10

    # Bayesian optimization overnight with higher epochs
    ./submit_optimization.sh optuna 15 15

    # Quick demo (no training)
    ./submit_optimization.sh demo

SUBMITTED JOB OUTPUT:
    Logs will be saved to: dump/logs/slurm/train_ml-<JOBID>.{out,err}
    Results will be in: optimization/best_hyperparams.json or grid_search_results.json

EOF
    exit 0
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Validate mode
case "$MODE" in
    quick|grid|optuna|demo)
        ;;
    *)
        echo "Invalid mode: $MODE"
        echo "Valid modes: quick, grid, optuna, demo"
        echo "Use './submit_optimization.sh help' for more information"
        exit 1
        ;;
esac

echo "Submitting hyperparameter optimization job to SLURM..."
echo "  Mode: $MODE"
echo "  Epochs: $EPOCHS_FWD (forward) + $EPOCHS_BWD (backward)"
echo ""

# Submit job with environment variables
if [ "$MODE" = "demo" ]; then
    # Demo doesn't need epochs
    JOBID=$(sbatch --export=MODE="$MODE" "$SCRIPT_DIR/train_ml.slurm.sh" | awk '{print $4}')
else
    JOBID=$(sbatch --export=MODE="$MODE",EPOCHS_FWD="$EPOCHS_FWD",EPOCHS_BWD="$EPOCHS_BWD" "$SCRIPT_DIR/train_ml.slurm.sh" | awk '{print $4}')
fi

echo "✓ Job submitted successfully!"
echo ""
echo "Job ID: $JOBID"
echo "Status: sbatch job submitted"
echo ""
echo "Monitor job:"
echo "  squeue --me"
echo "  squeue -j $JOBID"
echo ""
echo "View logs:"
echo "  tail -f dump/logs/slurm/train_ml-$JOBID.out"
echo "  tail -f dump/logs/slurm/train_ml-$JOBID.err"
echo ""
echo "Results location:"
echo "  optimization/best_hyperparams.json  (Bayesian/Grid)"
echo "  optimization/grid_search_results.json"
