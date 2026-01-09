# Hyperparameter Optimization Setup - Summary

## Files Created

This setup provides three different approaches to hyperparameter optimization:

### 1. **grid_search.py** - Quick Grid Search
- Fast, straightforward grid search over key parameters
- No additional dependencies
- Two modes:
  - `--quick`: 8 configurations (30 min)
  - Default: 72 configurations (2-4 hours)
- **Best for**: Initial exploration, rapid iteration

### 2. **hyperparameter_optimization.py** - Bayesian Optimization (Optuna)
- Intelligent exploration using Tree-structured Parzen Estimator (TPE)
- Searches larger parameter space efficiently
- Requires: `pip install optuna`
- **Best for**: Thorough optimization, finding local optima

### 3. **format_best_params.py** - Results Formatter
- Converts optimization results to multiple formats
- Output formats: JSON, YAML, TXT, Shell script
- Creates runnable scripts from best parameters

### 4. **demo_optimization.py** - Demo Output
- Shows expected output format from optimization
- Useful for understanding the pipeline
- Can be run immediately without training

## Quick Start Guide

### Step 1: Run a Quick Search
```bash
cd mass_spec_modeling/exec_scripts/
python grid_search.py --quick --epochs_fwd 3 --epochs_bwd 3
```

This will create `grid_search_results.json` with results from 8 configurations.

### Step 2: View Demo Output
```bash
python demo_optimization.py
```

This shows what complete optimization results look like (pre-generated demo).

### Step 3: Run Full Optimization
```bash
# Install Optuna if needed
pip install optuna pyyaml

# Run Bayesian optimization
python hyperparameter_optimization.py --n_trials 30 --epochs_fwd 10 --epochs_bwd 10
```

This creates `best_hyperparams.json` with complete optimization history.

### Step 4: Format Results
```bash
# Convert to runnable shell script
python format_best_params.py --input best_hyperparams.json --format sh

# Run the best configuration
chmod +x best_params/best_hyperparams.sh
./best_params/best_hyperparams.sh --epochs_fwd 100 --epochs_bwd 100
```

Or convert to other formats:
```bash
# JSON (detailed, machine-readable)
python format_best_params.py --input best_hyperparams.json --format json

# YAML (human-readable configuration)
python format_best_params.py --input best_hyperparams.json --format yaml

# TXT (plain text report)
python format_best_params.py --input best_hyperparams.json --format txt
```

## Search Space

### Grid Search (Quick Mode) - 8 configs
- batch_size: [64, 128]
- latent_dim: [64, 128]
- learning_rate: [1e-4, 5e-4]
- Fixed: dropout=0.1, norm=layer, alpha_wass=0.5, alpha_cos=1.0

### Grid Search (Full Mode) - 72 configs
- batch_size: [64, 128, 256]
- latent_dim: [64, 128, 256]
- learning_rate: [1e-5, 1e-4, 5e-4, 1e-3]
- norm: [layer, batch]
- Fixed: dropout=0.1, alpha_wass=0.5, alpha_cos=1.0

### Bayesian Optimization - 20+ dimensions
- All of the above, plus:
- weight_decay: [1e-6, 1e-3]
- dropout: [0.0, 0.5]
- alpha_wass: [0.1, 2.0]
- alpha_cos: [0.1, 2.0]
- cycle_fwd, cycle_bwd, cycle_bwd_spec: [0.01, 1.0]
- curriculum_start: [0.1, 0.9]
- curriculum_step: [0.01, 0.2]
- use_faiss: [True, False]

## Output Files

After running optimization, you'll get:

### From Grid Search
- `grid_search_results.json` - Complete trial history and best config

### From Bayesian Optimization
- `best_hyperparams.json` - Detailed results (all trials, best config, metrics)

### From Format Script
- `best_params/best_hyperparams.json` - Formatted JSON
- `best_params/best_hyperparams.yaml` - YAML config
- `best_params/best_hyperparams.txt` - Human-readable report
- `best_params/best_hyperparams.sh` - Runnable shell script

## Optimization Metrics

### Primary Objective (Minimized)
- **Validation Loss** - Combined spectrum reconstruction + alignment loss

### Secondary Metrics (Tracked)
- **Recall@1, @5, @10** - Top-K retrieval accuracy
- **MRR** - Mean Reciprocal Rank (average inverse rank of correct molecule)

## Tips

1. **For quick feedback** (minutes): Use `grid_search.py --quick`
2. **For solid baseline** (hours): Use `grid_search.py` (full mode)
3. **For thorough tuning** (overnight): Use `hyperparameter_optimization.py --n_trials 50`
4. **Memory issues?** Reduce batch_size in search space or skip large configs
5. **After finding best hyperparams**: Retrain with more epochs (100+) for final model

## Expected Output Example

The demo shows what results look like:
```
BEST TRIAL: #7
Validation Loss: 0.284700
Recall@1: 0.42, Recall@5: 0.68, Recall@10: 0.82
MRR: 0.5234

BEST HYPERPARAMETERS:
  batch_size: 128
  latent_dim: 256
  learning_rate: 0.00035
  weight_decay: 0.0001
  dropout: 0.15
  norm: layer
  ... (more parameters)

COMMAND TO RUN:
python ml_minimal_implement.py --batch_size 128 --latent_dim 256 ...
```

## File Structure

```
mass_spec_modeling/exec_scripts/
├── ml_minimal_implement.py          (Main training script)
├── grid_search.py                   (Grid search tool)
├── hyperparameter_optimization.py   (Bayesian optimization - requires Optuna)
├── format_best_params.py            (Results formatter)
├── demo_optimization.py             (Demo output generator)
├── HYPERPARAMETER_OPTIMIZATION_README.md  (Detailed guide)
├── HYPERPARAMETER_OPTIMIZATION_SUMMARY.md (This file)
└── best_params/                     (Output directory, created after formatting)
    ├── best_hyperparams.json
    ├── best_hyperparams.yaml
    ├── best_hyperparams.txt
    └── best_hyperparams.sh

```

## Workflow Recommendations

### Phase 1: Exploration (1-2 hours)
```bash
python grid_search.py --quick --epochs_fwd 3 --epochs_bwd 3
```
Output: Identifies promising hyperparameter regions

### Phase 2: Refinement (4-8 hours)
```bash
python grid_search.py --epochs_fwd 5 --epochs_bwd 5
```
Output: Narrows down to best few configurations

### Phase 3: Optimization (Overnight, optional)
```bash
python hyperparameter_optimization.py --n_trials 50 --epochs_fwd 10 --epochs_bwd 10
```
Output: Finds near-optimal configuration

### Phase 4: Final Training (24+ hours)
```bash
./best_params/best_hyperparams.sh --epochs_fwd 200 --epochs_bwd 200
```
Output: Final trained model with best hyperparameters

## Dependencies

All scripts require:
- torch >= 1.9
- torch_geometric (optional, for GNN)
- numpy, scipy

Optional (for Bayesian optimization):
- optuna >= 3.0
- pyyaml

Install optional dependencies:
```bash
pip install optuna pyyaml
```

## Notes

- Grid search tests **all combinations** (systematic, but exhaustive)
- Bayesian optimization **intelligently explores** (more efficient, better for large spaces)
- Metrics are extracted from stdout of training script
- Each trial respects `--epochs_fwd` and `--epochs_bwd` limits
- Results are saved in JSON for easy parsing and analysis
