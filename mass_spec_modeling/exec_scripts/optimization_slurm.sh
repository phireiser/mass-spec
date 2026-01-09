#!/usr/bin/env bash
#SBATCH --job-name=hyperparam_optim
#SBATCH --gres=shard:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=100G
#SBATCH --time=40:00:00
#SBATCH --output=dump/logs/slurm/%x-%j.out
#SBATCH --error=dump/logs/slurm/%x-%j.err

set -e

module load Conda
conda activate /lisc/data/scratch/tbi/reiser/pyenv

# Default optimization mode (can be overridden with: sbatch --export=MODE=grid train_ml.slurm.sh)
MODE="${MODE:-grid}"
EPOCHS_FWD="${EPOCHS_FWD:-10000}"
EPOCHS_BWD="${EPOCHS_BWD:-10000}"

echo "======================================================================"
echo "Hyperparameter Optimization Job"
echo "======================================================================"
echo "Mode: $MODE"
echo "Epochs (forward): $EPOCHS_FWD"
echo "Epochs (backward): $EPOCHS_BWD"
echo "Started: $(date)"
echo "======================================================================"
echo ""

# Run hyperparameter optimization
bash mass_spec_modeling/exec_scripts/optimization/run_optimization_workflow.sh "$MODE" --epochs_fwd "$EPOCHS_FWD" --epochs_bwd "$EPOCHS_BWD"

echo ""
echo "======================================================================"
echo "Optimization Job Complete"
echo "Completed: $(date)"
echo "======================================================================"
echo ""
echo "Results saved to: best_hyperparams.json or grid_search_results.json"
echo "Next steps:"
echo "  1. Review results: cat best_hyperparams.json"
echo "  2. Format results: python format_best_params.py --input best_hyperparams.json --format sh"
echo "  3. Train final model: ./best_params/best_hyperparams.sh --epochs_fwd 100 --epochs_bwd 100"

