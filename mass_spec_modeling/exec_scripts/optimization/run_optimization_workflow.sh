#!/usr/bin/env bash
# ==============================================================================
# Hyperparameter Optimization Workflow Script
# ==============================================================================
# This script demonstrates the complete hyperparameter optimization workflow
# for the ML minimal implementation.
#
# Usage:
#   bash run_optimization_workflow.sh [quick|grid|optuna]
#
# Examples:
#   bash run_optimization_workflow.sh quick    # Quick grid search (8 configs)
#   bash run_optimization_workflow.sh grid     # Full grid search (72 configs)
#   bash run_optimization_workflow.sh optuna   # Bayesian optimization (30 trials)
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Parse mode and forward any additional args (e.g., --epochs_fwd/--epochs_bwd)
MODE="${1:-quick}"
shift || true
EXTRA_ARGS=("$@")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "\n${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check Python
if ! command -v python &> /dev/null; then
    print_error "Python not found. Please install Python 3.7+"
    exit 1
fi

case "$MODE" in
    quick)
        print_header "QUICK HYPERPARAMETER OPTIMIZATION (Grid Search - 8 configs)"
        print_info "Estimated time: 30-45 minutes"
        print_info "Configuration space: batch_size×latent_dim×learning_rate"
        echo ""
        # Allow caller to override epochs and other args via EXTRA_ARGS
        python "$SCRIPT_DIR/grid_search.py" --quick "${EXTRA_ARGS[@]}"

        print_success "Grid search complete!"
        print_info "Results saved to: grid_search_results.json"
        echo ""
        print_header "Next Steps:"
        echo "1. Review results in grid_search_results.json"
        echo "2. Run more extensive search: bash run_optimization_workflow.sh grid"
        echo "3. Or run Bayesian optimization: bash run_optimization_workflow.sh optuna"
        ;;

    grid)
        print_header "COMPREHENSIVE GRID SEARCH (72 configurations)"
        print_info "Estimated time: 3-6 hours"
        print_info "Configuration space: batch_size×latent_dim×learning_rate×norm"
        echo ""
        # Defaults handled in grid_search.py; EXTRA_ARGS can override
        python "$SCRIPT_DIR/grid_search.py" "${EXTRA_ARGS[@]}"

        print_success "Grid search complete!"
        print_info "Results saved to: grid_search_results.json"
        echo ""
        print_header "Next Steps:"
        echo "1. Review results: less grid_search_results.json"
        echo "2. Extract best config: python format_best_params.py --input grid_search_results.json --format txt"
        echo "3. Run final training with best hyperparameters"
        ;;

    optuna)
        print_header "BAYESIAN OPTIMIZATION (Optuna - 30 trials)"
        print_info "Estimated time: 4-8 hours"
        print_info "Intelligent exploration of 20+ dimensional hyperparameter space"
        echo ""

        # Check if optuna is installed
        if ! python -c "import optuna" 2>/dev/null; then
            print_error "Optuna not installed"
            echo "Install with: pip install optuna pyyaml"
            exit 1
        fi

        # Allow caller to specify n_trials/epochs via EXTRA_ARGS
        python "$SCRIPT_DIR/hyperparameter_optimization.py" "${EXTRA_ARGS[@]}"

        print_success "Bayesian optimization complete!"
        print_info "Results saved to: best_hyperparams.json"
        echo ""
        print_header "Formatting Results:"
        python "$SCRIPT_DIR/format_best_params.py" --input best_hyperparams.json --format txt
        python "$SCRIPT_DIR/format_best_params.py" --input best_hyperparams.json --format sh

        print_success "Best parameters formatted!"
        echo ""
        print_header "Next Steps:"
        echo "1. Review text report: cat best_params/best_hyperparams.txt"
        echo "2. Run final training: ./best_params/best_hyperparams.sh --epochs_fwd 100 --epochs_bwd 100"
        ;;

    demo)
        print_header "DEMO: Expected Optimization Output"
        python "$SCRIPT_DIR/demo_optimization.py"
        print_success "Demo complete! This shows the expected output format."
        ;;

    *)
        print_error "Unknown mode: $MODE"
        echo ""
        echo "Usage: bash run_optimization_workflow.sh [quick|grid|optuna|demo]"
        echo ""
        echo "Modes:"
        echo "  quick   - Quick grid search (8 configs, ~30 min)"
        echo "  grid    - Full grid search (72 configs, ~3-6 hours)"
        echo "  optuna  - Bayesian optimization (30 trials, ~4-8 hours)"
        echo "  demo    - Show demo output format"
        exit 1
        ;;
esac

print_header "WORKFLOW COMPLETE"
echo "All results saved with timestamps for comparison"
echo ""
