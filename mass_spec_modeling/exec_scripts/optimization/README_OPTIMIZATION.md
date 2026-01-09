# Hyperparameter Optimization Tools - Master Index

## Overview
Complete hyperparameter optimization toolkit for the ML Minimal Implementation with three methods:
1. **Grid Search** (fast, comprehensive)
2. **Bayesian Optimization** (intelligent exploration)
3. **Demo** (showcase output format)

---

## Quick Start (3 steps)

### 1️⃣ Run Quick Search (30 minutes)
```bash
cd mass_spec_modeling/exec_scripts/
bash run_optimization_workflow.sh quick
```

### 2️⃣ View Results
```bash
cat grid_search_results.json | jq '.best_config'
```

### 3️⃣ Train Final Model
```bash
python ml_minimal_implement.py \
  --batch_size 128 \
  --latent_dim 256 \
  --learning_rate 0.00035 \
  ... (copy from results)
```

---

## Tools Available

### 🔧 Core Tools

| Tool | Purpose | Time | Command |
|------|---------|------|---------|
| **grid_search.py** | Quick grid search | 30m (quick) / 3-6h (full) | `python grid_search.py --quick` |
| **hyperparameter_optimization.py** | Bayesian optimization | 4-8h | `python hyperparameter_optimization.py --n_trials 30` |
| **format_best_params.py** | Format results | <1m | `python format_best_params.py --input best_hyperparams.json --format sh` |
| **demo_optimization.py** | Show expected output | <1m | `python demo_optimization.py` |
| **run_optimization_workflow.sh** | Unified workflow | Varies | `bash run_optimization_workflow.sh [quick\|grid\|optuna]` |

### 📚 Documentation

| Document | Content |
|----------|---------|
| **HYPERPARAMETER_OPTIMIZATION_SUMMARY.md** | This file - complete guide |
| **HYPERPARAMETER_OPTIMIZATION_README.md** | Detailed reference documentation |
| **ml_minimal_implement.py** | Main training script with all parameters |

---

## Workflow Modes

### Mode 1: Quick Exploration (Recommended Start)
```bash
bash run_optimization_workflow.sh quick
```
- **Time**: 30-45 minutes
- **Configs tested**: 8
- **Output**: `grid_search_results.json`
- **Best for**: Initial exploration, sanity check

### Mode 2: Comprehensive Grid
```bash
bash run_optimization_workflow.sh grid
```
- **Time**: 3-6 hours
- **Configs tested**: 72
- **Output**: `grid_search_results.json`
- **Best for**: Finding good configuration region

### Mode 3: Bayesian Optimization
```bash
bash run_optimization_workflow.sh optuna
```
- **Time**: 4-8 hours
- **Requires**: `pip install optuna pyyaml`
- **Output**: `best_hyperparams.json` (all trials + best config)
- **Best for**: Thorough optimization, local optima

### Mode 4: Demo
```bash
bash run_optimization_workflow.sh demo
```
- Shows what optimized output looks like
- No training required
- Good for understanding the pipeline

---

## Hyperparameters Optimized

### Architecture
- `batch_size`: {32, 64, 128, 256, 512}
- `latent_dim`: {64, 128, 256, 512}
- `dropout`: 0.0 to 0.5
- `norm`: {layer, batch, none}

### Training
- `learning_rate`: 1e-5 to 1e-2
- `weight_decay`: 1e-6 to 1e-3

### Loss Weighting (Bayesian only)
- `alpha_wass`: 0.1 to 2.0
- `alpha_cos`: 0.1 to 2.0
- `cycle_fwd`: 0.01 to 1.0
- `cycle_bwd`: 0.01 to 1.0
- `cycle_bwd_spec`: 0.01 to 1.0

### Curriculum Learning
- `curriculum_start`: 0.1 to 0.9
- `curriculum_step`: 0.01 to 0.2

### Advanced
- `use_faiss`: {True, False}

---

## Output Formats

After optimization, convert results to your preferred format:

### JSON (Machine-readable)
```bash
python format_best_params.py --input best_hyperparams.json --format json
```
Output: `best_params/best_hyperparams.json`

### YAML (Configuration file)
```bash
python format_best_params.py --input best_hyperparams.json --format yaml
```
Output: `best_params/best_hyperparams.yaml`

### TXT (Human-readable report)
```bash
python format_best_params.py --input best_hyperparams.json --format txt
```
Output: `best_params/best_hyperparams.txt`

### SH (Runnable script)
```bash
python format_best_params.py --input best_hyperparams.json --format sh
```
Output: `best_params/best_hyperparams.sh` (executable)

---

## Example Workflow

### Session 1: Quick Search (30 min)
```bash
# Initial exploration
bash run_optimization_workflow.sh quick

# Results in grid_search_results.json
# Best loss: 0.3156
# Best config: batch_size=128, latent_dim=256, lr=0.00035
```

### Session 2: Comprehensive Search (3 hours)
```bash
# More thorough grid search
bash run_optimization_workflow.sh grid

# Better results found
# Best loss: 0.2847
# Identifies region with batch_size=128, latent_dim=256
```

### Session 3: Bayesian Optimization (Overnight)
```bash
# Fine-grained optimization
bash run_optimization_workflow.sh optuna

# Best loss: 0.2561
# Refined parameters with secondary loss weights optimized
```

### Session 4: Final Training
```bash
# Format and run best configuration
python format_best_params.py --input best_hyperparams.json --format sh

# Train full model
./best_params/best_hyperparams.sh --epochs_fwd 200 --epochs_bwd 200

# Save final checkpoint
mv mini_frag_checkpoint.pt mini_frag_checkpoint_final.pt
```

---

## Metrics Tracked

### Primary (Minimized)
- **Validation Loss**: Combined spectrum reconstruction + alignment loss
  - Formula: `alpha_cos * cosine_loss + alpha_wass * wasserstein_loss`

### Secondary (For Monitoring)
- **Recall@K**: Proportion of correct molecules in top-K candidates
- **MRR**: Mean Reciprocal Rank of correct molecule

### Example Results
```
Best Trial: #7
Validation Loss:   0.2847
Recall@1:          0.42
Recall@5:          0.68
Recall@10:         0.82
MRR:               0.5234
```

---

## Installation Requirements

### Minimal (Grid Search only)
```bash
# Already have: torch, torch_geometric, numpy
```

### Full Features (Bayesian Optimization)
```bash
pip install optuna pyyaml
```

### Verify Installation
```bash
python -c "import optuna; print('Optuna OK')"
python -c "import yaml; print('PyYAML OK')"
```

---

## File Structure

```
mass_spec_modeling/exec_scripts/
├── ml_minimal_implement.py
│   └── Main training script (trains model with given hyperparameters)
│
├── Optimization Tools
├── grid_search.py
│   └── Grid search over hyperparameter combinations
├── hyperparameter_optimization.py
│   └── Bayesian optimization using Optuna
├── format_best_params.py
│   └── Convert results to JSON/YAML/TXT/Shell formats
├── demo_optimization.py
│   └── Demo showing expected output format
│
├── Workflow Automation
├── run_optimization_workflow.sh
│   └── Unified interface for all optimization methods
│
├── Documentation
├── HYPERPARAMETER_OPTIMIZATION_SUMMARY.md (THIS FILE)
├── HYPERPARAMETER_OPTIMIZATION_README.md (DETAILED REFERENCE)
│
└── Output Directory (created after formatting)
    └── best_params/
        ├── best_hyperparams.json
        ├── best_hyperparams.yaml
        ├── best_hyperparams.txt
        └── best_hyperparams.sh
```

---

## Tips & Tricks

### 💡 Getting Started
1. Start with `quick` mode (30 min, 8 configs)
2. If results look promising, try `grid` mode (3-6 hours)
3. Use `optuna` for final tuning with more epochs

### ⚡ Speed Up
- Use fewer epochs for optimization (5-10)
- Run `--quick` mode for exploration
- Once you find good region, train thoroughly with more epochs

### 🧠 Better Results
- Run multiple times with different random seeds
- Use Bayesian optimization for larger search spaces
- Monitor both validation loss AND recall metrics

### 🔧 Troubleshooting
- **CUDA out of memory**: Reduce `batch_size` in search space
- **Metrics not extracted**: Check that training outputs loss to stdout
- **Very slow optimization**: Use `--quick` mode or reduce epochs

### 📊 Analysis
```bash
# View best config as table
python format_best_params.py --input best_hyperparams.json --format txt

# Extract specific parameter
cat best_hyperparams.json | jq '.best_hyperparameters.batch_size'

# Compare all trials
cat best_hyperparams.json | jq '.all_trials[] | {trial_number, value, batch_size}'
```

---

## Expected Output

After running optimization, you'll see:

```
================================================================================
HYPERPARAMETER OPTIMIZATION RESULTS SUMMARY
================================================================================

Optimization completed at: 2026-01-07T18:29:32.956059
Total trials: 30
Epochs per trial: 10 (forward) + 10 (backward)

BEST TRIAL: #7
────────────────────────────────────────────────────────────────────────────────
Validation Loss:      0.284700
Recall@1:             0.42
Recall@5:             0.68
Recall@10:            0.82
MRR:                  0.5234

BEST HYPERPARAMETERS
────────────────────────────────────────────────────────────────────────────────
batch_size............................... 128
latent_dim.............................. 256
learning_rate........................... 0.00035
... (more parameters)

COMMAND TO RUN WITH BEST PARAMETERS
────────────────────────────────────────────────────────────────────────────────
python ml_minimal_implement.py \
  --batch_size 128 \
  --latent_dim 256 \
  --learning_rate 0.00035 \
  ... (all parameters) \
  --epochs_fwd 100 --epochs_bwd 100
```

---

## Common Commands

### Run Quick Optimization
```bash
cd mass_spec_modeling/exec_scripts/
python grid_search.py --quick --epochs_fwd 3 --epochs_bwd 3
```

### Run Bayesian Optimization
```bash
python hyperparameter_optimization.py --n_trials 30 --epochs_fwd 10 --epochs_bwd 10
```

### Format Results to Shell Script
```bash
python format_best_params.py --input best_hyperparams.json --format sh
chmod +x best_params/best_hyperparams.sh
```

### Train Final Model with Best Hyperparameters
```bash
./best_params/best_hyperparams.sh --epochs_fwd 100 --epochs_bwd 100
```

### View Results as Text Report
```bash
python format_best_params.py --input best_hyperparams.json --format txt
cat best_params/best_hyperparams.txt
```

---

## Support & Debugging

### Check GPU
```bash
python -c "import torch; print(f'GPU: {torch.cuda.is_available()}')"
```

### Test Training Script
```bash
python ml_minimal_implement.py --epochs_fwd 1 --epochs_bwd 1 --device cuda
```

### Verify Tools
```bash
python grid_search.py --help
python hyperparameter_optimization.py --help
python format_best_params.py --help
```

---

## Citation

If you use this hyperparameter optimization toolkit, please cite:
```
@software{ml_minimal_impl_hpo,
  title={Hyperparameter Optimization for Fragment-Aided Bidirectional Mass Spectrometry Model},
  author={Reiser, Philipp},
  year={2025},
  url={https://github.com/yourusername/thesis/mol}
}
```

---

**Last Updated**: January 7, 2026
**Status**: Ready for use
**Version**: 1.0
