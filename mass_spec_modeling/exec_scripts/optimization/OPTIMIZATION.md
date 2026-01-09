# Hyperparameter Optimization

All hyperparameter optimization tools and documentation have been moved to the `optimization/` subdirectory.

## Quick Start

To get started with hyperparameter optimization:

```bash
cd optimization/
cat START_HERE.md
```

Or run directly:

```bash
cd optimization/
bash run_optimization_workflow.sh quick
```

## What's Inside

The `optimization/` folder contains:

### Tools
- `grid_search.py` - Fast grid search over hyperparameter combinations
- `hyperparameter_optimization.py` - Bayesian optimization with Optuna
- `format_best_params.py` - Convert results to JSON/YAML/TXT/Shell formats
- `demo_optimization.py` - Demo showing expected output format
- `run_optimization_workflow.sh` - Unified automation script

### Documentation
- `START_HERE.md` - Quick start guide (read this first)
- `README_OPTIMIZATION.md` - Master index and comprehensive guide
- `HYPERPARAMETER_OPTIMIZATION_SUMMARY.md` - Detailed workflow guide
- `HYPERPARAMETER_OPTIMIZATION_README.md` - Reference documentation
- `OPTIMIZATION_SETUP_REPORT.md` - Setup completion report
- `FILES_CREATED.txt` - File summary

## Quick Commands

```bash
cd optimization/

# View demo (1 minute, no training required)
bash run_optimization_workflow.sh demo

# Quick grid search (30 minutes)
bash run_optimization_workflow.sh quick

# Full grid search (3-6 hours)
bash run_optimization_workflow.sh grid

# Bayesian optimization (requires: pip install optuna pyyaml)
bash run_optimization_workflow.sh optuna
```

## Three Optimization Approaches

1. **Quick Grid Search** (30 min, 8 configs) - Initial exploration
2. **Full Grid Search** (3-6 hours, 72 configs) - Comprehensive search
3. **Bayesian Optimization** (4-8 hours, 30 trials) - Intelligent tuning

See `optimization/START_HERE.md` for detailed information.
