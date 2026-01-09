# SLURM Integration Guide

## Overview

The `train_ml.slurm.sh` SLURM job script has been updated to seamlessly call the hyperparameter optimization tools. You can now submit optimization jobs to the cluster easily.

## Quick Submit

```bash
# From exec_scripts directory

# Quick grid search (30 minutes)
./submit_optimization.sh quick

# Full grid search (3-6 hours)
./submit_optimization.sh grid

# Bayesian optimization (overnight)
./submit_optimization.sh optuna

# Quick demo (1 minute, no training)
./submit_optimization.sh demo
```

## How It Works

### submit_optimization.sh
Helper script that submits `train_ml.slurm.sh` to SLURM with configuration:
- Mode: quick/grid/optuna/demo
- Epochs: Customizable per phase
- Automatic job monitoring hints

### train_ml.slurm.sh
SLURM job script that:
1. Loads conda environment
2. Navigates to optimization/ folder
3. Calls `run_optimization_workflow.sh` with specified mode
4. Logs all output and errors
5. Reports results location

## Custom Epochs

Run with specific number of epochs per phase:

```bash
# Quick search with 5 epochs each
./submit_optimization.sh quick 5 5

# Grid search with 15 epochs
./submit_optimization.sh grid 15 15

# Bayesian with 20 epochs
./submit_optimization.sh optuna 20 20
```

## Monitor Jobs

```bash
# List all your jobs
squeue --me

# Check specific job
squeue -j <JOBID>

# Watch output in real-time
tail -f dump/logs/slurm/train_ml-<JOBID>.out

# Check errors
tail -f dump/logs/slurm/train_ml-<JOBID>.err
```

## Job Configuration

Default SLURM settings in `train_ml.slurm.sh`:

| Setting | Value |
|---------|-------|
| Job Name | train_ml |
| Memory | 20G |
| CPUs | 4 |
| Time Limit | 24 hours |
| Output Log | dump/logs/slurm/train_ml-%j.out |
| Error Log | dump/logs/slurm/train_ml-%j.err |

Modify `train_ml.slurm.sh` to change these settings.

## Results

After job completes, results are saved to:

**Grid Search:**
```
mass_spec_modeling/exec_scripts/optimization/grid_search_results.json
```

**Bayesian Optimization:**
```
mass_spec_modeling/exec_scripts/optimization/best_hyperparams.json
```

## Workflow

### Phase 1: Explore (30 minutes)
```bash
./submit_optimization.sh quick 3 3
```
Results help identify promising hyperparameter regions.

### Phase 2: Refine (3-6 hours)
```bash
./submit_optimization.sh grid 5 5
```
More comprehensive search within identified region.

### Phase 3: Optimize (Overnight)
```bash
./submit_optimization.sh optuna 15 15
```
Fine-grained Bayesian optimization for best configuration.

### Phase 4: Final Training
```bash
cd optimization/
python format_best_params.py --input best_hyperparams.json --format sh
./best_params/best_hyperparams.sh --epochs_fwd 200 --epochs_bwd 200
```
Train final model with best hyperparameters.

## Examples

### Quick Exploration
```bash
./submit_optimization.sh quick 5 5
# Wait 30-45 minutes
squeue --me  # Check status
tail -f dump/logs/slurm/train_ml-*.out  # Watch progress
```

### Overnight Optimization
```bash
./submit_optimization.sh grid 10 10
# Submit and go to sleep
# Check results in the morning
cat optimization/grid_search_results.json
```

### Submit Multiple Jobs
```bash
# Submit quick search
./submit_optimization.sh quick 5 5
echo "Quick search: Job 1"

# Wait a bit
sleep 60

# Submit grid search
./submit_optimization.sh grid 10 10
echo "Grid search: Job 2"

# Monitor both
squeue --me
```

## Help

Get detailed help on usage:

```bash
./submit_optimization.sh help
./submit_optimization.sh --help
```

## Manual SLURM Submission

If you prefer to use `sbatch` directly:

```bash
# Quick search (30 min)
sbatch --export=MODE=quick,EPOCHS_FWD=5,EPOCHS_BWD=5 train_ml.slurm.sh

# Grid search (4 hours)
sbatch --export=MODE=grid,EPOCHS_FWD=10,EPOCHS_BWD=10 train_ml.slurm.sh

# Bayesian optimization (overnight)
sbatch --export=MODE=optuna,EPOCHS_FWD=20,EPOCHS_BWD=20 train_ml.slurm.sh

# Demo (no training)
sbatch --export=MODE=demo train_ml.slurm.sh
```

## Troubleshooting

### Job won't start
Check if conda environment path is correct in `train_ml.slurm.sh`

### Output not found
Verify `dump/logs/slurm/` directory exists:
```bash
mkdir -p dump/logs/slurm/
```

### Module load fails
Check available modules:
```bash
module avail Conda
```

### Script permission errors
Make helper script executable:
```bash
chmod +x submit_optimization.sh
```

## Files Involved

| File | Purpose |
|------|---------|
| `train_ml.slurm.sh` | SLURM job script (updated) |
| `submit_optimization.sh` | Helper for job submission (new) |
| `optimization/run_optimization_workflow.sh` | Optimization workflow automation |
| `optimization/grid_search.py` | Grid search implementation |
| `optimization/hyperparameter_optimization.py` | Bayesian optimization |
| `optimization/format_best_params.py` | Result formatting |

## Tips

1. **Start with demo** - Test the setup without training
2. **Use quick mode first** - 30 min to identify promising regions
3. **Monitor with tail** - Real-time progress tracking
4. **Save outputs** - Keep results for comparison
5. **Customize epochs** - Use fewer for exploration, more for final training

## Integration Points

- **Conda environment**: `/lisc/home/user/reiser/Nextcloud/studium/computationalScience/thesis/mol/env`
- **Working directory**: `mass_spec_modeling/exec_scripts/`
- **Log directory**: `dump/logs/slurm/`
- **Results directory**: `mass_spec_modeling/exec_scripts/optimization/`

---

**Status**: Ready to submit jobs to SLURM cluster
