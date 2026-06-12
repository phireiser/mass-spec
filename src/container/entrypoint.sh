#!/bin/bash
# Entrypoint script for molecular spectroscopy ML pipeline
# Provides CLI interface for different workflows

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_help() {
    cat <<EOF
${GREEN}Molecular Spectroscopy ML Pipeline${NC}

${YELLOW}Usage:${NC} docker run [OPTIONS] mol-spectro <COMMAND> [ARGS]

${YELLOW}Commands:${NC}

  data-gen              Generate spectral data from molecules
    Usage: data-gen [--smiles SMILES] [--name NAME] [--dir DIR]

  train                 Train ML model (forward or inverse prediction)
    Usage: train [--epochs EPOCHS] [--batch-size BATCH_SIZE] [--output-dir DIR]

  optimize              Run hyperparameter optimization (Optuna)
    Usage: optimize [--epochs-fwd EPOCHS] [--epochs-bwd EPOCHS] [--trials N]

  analyze               Analyze data distribution and complexity
    Usage: analyze [--input CSV] [--output SVG]

  plot                  Generate plots from metrics/results
    Usage: plot [--metric METRIC] [--output SVG]

  shell                 Open interactive bash shell

  help                  Show this message

${YELLOW}Examples:${NC}

  # Train model for 5000 epochs
  docker run --gpus all -v data:/app/data mol-spectro train --epochs 5000

  # Generate data for specific molecule
  docker run -v data:/app/data mol-spectro data-gen --smiles "CC1=CC=CC=C1" --name toluene

  # Optimize hyperparameters
  docker run --gpus all -v data:/app/data mol-spectro optimize --epochs-fwd 10000 --epochs-bwd 10000

${YELLOW}Docker Options:${NC}
  --gpus all            Enable all GPUs
  -v DATA:/app/data     Mount data directory
  -e VAR=value          Set environment variables

${YELLOW}Environment Variables:${NC}
  CUDA_VISIBLE_DEVICES  GPU indices to use (default: 0)
  PYTHONPATH            Python module search path (auto-set)
  REPO_ROOT             Project root (auto-set to /app)

EOF
}

# Ensure repo root is set
export REPO_ROOT="${REPO_ROOT:-/app}"
export PYTHONPATH="${REPO_ROOT}:${PYTHONPATH:-}"

COMMAND="${1:-help}"

case "${COMMAND}" in
    data-gen)
        echo -e "${GREEN}[Data Generation]${NC} Starting molecule fragmentation & spectrum generation..."
        cd "${REPO_ROOT}"
        # Allow passing arguments to the Python script
        python src/data_generation/main.py "${@:2}"
        ;;

    train)
        echo -e "${GREEN}[Training]${NC} Starting model training..."
        cd "${REPO_ROOT}"
        # Train with passed arguments
        python src/machine_learning/main.py "${@:2}"
        ;;

    optimize)
        echo -e "${GREEN}[Optimization]${NC} Starting hyperparameter optimization with Optuna..."
        cd "${REPO_ROOT}"

        # Parse Optuna-specific arguments with defaults
        EPOCHS_FWD="${EPOCHS_FWD:-10000}"
        EPOCHS_BWD="${EPOCHS_BWD:-10000}"

        python src/machine_learning/optimization/hyperparameter_optimization.py \
            --epochs_fwd "${EPOCHS_FWD}" \
            --epochs_bwd "${EPOCHS_BWD}" \
            --train_script "${REPO_ROOT}/src/machine_learning/main.py" \
            --output_dir "${REPO_ROOT}/outputs/best_params" \
            "${@:2}"
        ;;

    analyze)
        echo -e "${GREEN}[Analysis]${NC} Analyzing data distribution..."
        cd "${REPO_ROOT}"
        python run/plot/analyze_data_distribution.py "${@:2}"
        ;;

    plot)
        echo -e "${GREEN}[Plotting]${NC} Generating plots..."
        cd "${REPO_ROOT}"
        python run/plot/eval_from_metrics_csv.py "${@:2}"
        ;;

    shell)
        echo -e "${GREEN}[Shell]${NC} Opening interactive bash session..."
        /bin/bash
        ;;

    *)
        echo -e "${RED}Error: Unknown command '${COMMAND}'${NC}"
        echo ""
        print_help
        exit 1
        ;;
esac

exit 0
