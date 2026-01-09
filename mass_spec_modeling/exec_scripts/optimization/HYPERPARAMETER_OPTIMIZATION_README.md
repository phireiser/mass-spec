# Hyperparameter Optimization Guide

This directory contains tools for automated hyperparameter optimization of the ML minimal implementation.

## Quick Start

### Option 1: Quick Grid Search (Recommended for initial exploration)
```bash
python grid_search.py --quick --epochs_fwd 5 --epochs_bwd 5
```

This runs 8 configurations rapidly to find promising hyperparameters.

### Option 2: Comprehensive Grid Search
```bash
python grid_search.py --epochs_fwd 10 --epochs_bwd 10
```

This tests 72 configurations over more parameter ranges.

### Option 3: Bayesian Optimization (Most efficient, requires Optuna)
```bash
pip install optuna pyyaml
python hyperparameter_optimization.py --n_trials 30 --epochs_fwd 20 --epochs_bwd 20
```

This uses Optuna's TPE sampler for intelligent exploration (recommended for thorough search).

## Outputs

### Grid Search Results
- `grid_search_results.json`: Full results from all trials
- Best configuration printed to console

### Bayesian Optimization Results
- `best_hyperparams.json`: Complete optimization history with all trials
- Best configuration and metrics clearly marked

## Format Best Parameters

After optimization, convert results to different formats:

```bash
# Convert to JSON (default)
python format_best_params.py --input best_hyperparams.json --format json

# Convert to YAML
python format_best_params.py --input best_hyperparams.json --format yaml

# Convert to plain text
python format_best_params.py --input best_hyperparams.json --format txt

# Create runnable shell script
python format_best_params.py --input best_hyperparams.json --format sh
chmod +x best_params/best_hyperparams.sh
./best_params/best_hyperparams.sh  # Run with best params
```

## Hyperparameter Search Space

### Primary Parameters (all methods)
- **batch_size**: {32, 64, 128, 256, 512}
- **latent_dim**: {64, 128, 256, 512}
- **learning_rate**: 1e-5 to 1e-2 (log scale)
- **weight_decay**: 1e-6 to 1e-3 (log scale)
- **dropout**: 0.0 to 0.5
- **norm**: {layer, batch, none}

### Loss Weighting Parameters (Bayesian optimization)
- **alpha_wass**: 0.1 to 2.0 (Wasserstein loss weight)
- **alpha_cos**: 0.1 to 2.0 (Cosine loss weight)
- **cycle_fwd**: 0.01 to 1.0 (Forward cycle consistency)
- **cycle_bwd**: 0.01 to 1.0 (Backward cycle consistency)
- **cycle_bwd_spec**: 0.01 to 1.0 (Spectrum cycle consistency)
- **curriculum_start**: 0.1 to 0.9 (Starting curriculum fraction)
- **curriculum_step**: 0.01 to 0.2 (Curriculum increment per epoch)

### Advanced
- **use_faiss**: {True, False} (FAISS index for retrieval)

## Optimization Metrics

### Primary Objective (to minimize)
- **Validation Loss**: Combined loss from spectrum reconstruction and alignment

### Secondary Metrics (tracked but not optimized)
- **Recall@1**: Top-1 retrieval accuracy
- **Recall@5**: Top-5 retrieval accuracy
- **Recall@10**: Top-10 retrieval accuracy
- **MRR**: Mean Reciprocal Rank

## Tips

1. **Start with quick grid search** to understand the landscape
2. **Use fewer epochs** initially (5-10 per phase) for faster iteration
3. **Run Bayesian optimization** with 20-50 trials for thorough search
4. **Once you find good region**, retrain the best config with more epochs
5. **Monitor GPU memory** - reduce batch_size if OOM occurs

## Example Workflow

```bash
# 1. Quick exploration (30 mins)
python grid_search.py --quick --epochs_fwd 3 --epochs_bwd 3

# 2. More thorough search (2 hours)
python grid_search.py --epochs_fwd 5 --epochs_bwd 5

# 3. Bayesian optimization for final tuning (overnight)
python hyperparameter_optimization.py --n_trials 50 --epochs_fwd 10 --epochs_bwd 10

# 4. Format results
python format_best_params.py --input best_hyperparams.json --format sh

# 5. Train final model with best hyperparameters
./best_params/best_hyperparams.sh --epochs_fwd 100 --epochs_bwd 100
```

## Troubleshooting

### CUDA Out of Memory
- Reduce `batch_size` (try 64 or 32)
- Reduce `latent_dim`
- Reduce number of epochs for optimization

### Slow Optimization
- Use `--quick` mode for grid search
- Reduce epochs (5-10 sufficient for hyperparameter search)
- Run on GPU (set `--device cuda`)

### Metrics Not Extracted
- Check that training script outputs loss values to stdout
- May need to adjust regex patterns in `_extract_metrics_from_output()`

## Dependencies

- `torch >= 1.9`
- `torch_geometric` (optional, for GNN features)
- `optuna >= 3.0` (for Bayesian optimization)
- `pyyaml` (for YAML format output)

Install all with:
```bash
pip install optuna pyyaml
```
