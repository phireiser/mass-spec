# Quick Reference

Fast lookup guide for common infos.

## Directory Map

| Path | Purpose | Example |
|------|---------|---------|
| `data/compounds.csv` | Molecule list | SMILES + names |
| `data/nist_spectra/` | Raw spectra | .jdx files |
| `data/processed/` | Processed data | .pt tensors |
| `src/data_generation/` | Data pipeline | Processing code |
| `src/machine_learning/` | ML models | Training code |
| `outputs/checkpoints/` | Saved models | model_best.pt |
| `outputs/logs/` | Training logs | .log files |
| `outputs/metrics/` | Performance data | .json files |
| `outputs/plots/` | Visualizations | .png files |

## File Format Reference

### Input: compounds.csv
```csv
name,smiles,formula
acetone,CC(=O)C,C3H6O
benzene,c1ccccc1,C6H6
```

### Input: NIST Spectra (.jdx)
- JCAMP-DX format files
- Location: `data/nist_spectra/`
- Content: m/z (mass-to-charge) vs intensity

### File Organization Tips

After first run, your directory structure will look like:

```
data/
├── compounds.csv                    # Molecule definitions
├── compounds_amines.csv            # Amino compounds subset
├── nist_spectra/                   # Raw NIST mass spectra
│   ├── acetone-Mass.jdx
│   ├── benzene-Mass.jdx
│   └── ... (200+ more .jdx files)
└── processed/                      # Generated datasets
    ├── fwd/
    │   ├── train.pt
    │   ├── val.pt
    │   └── test.pt
    └── bwd/
        ├── train.pt
        ├── val.pt
        └── test.pt

outputs/
├── checkpoints/                    # Saved models
├── logs/                          # Training logs
├── metrics/                       # Performance metrics
└── plots/                         # Generated visualizations
```
## Environment Variables

| Variable | Purpose | Default | Example |
|----------|---------|---------|---------|
| `EPOCHS_FWD` | Forward model epochs | 10000 | 5000 |
| `EPOCHS_BWD` | Inverse model epochs | 10000 | 5000 |
| `BATCH_SIZE` | Training batch size | 64 | 32 |
| `LEARNING_RATE` | Optimizer LR | 0.001 | 0.0005 |
| `CUDA_VISIBLE_DEVICES` | GPU IDs | 0 | 0,1 |
| `PYTHONPATH` | Python path | /app | /app:/other |

## Common Workflows

### Workflow 1: Quick Training
```bash
# Generate data
run/hpc/data_gen.sh

# Train with defaults
run/hpc/ml_train.sh

# Check results
ls outputs/checkpoints/
```

### Workflow 3: Hyperparameter Optimization
```bash
# Generate data (if needed)
run/hpc/data_gen.sh

# Run optimization
run/hpc/ml_optimze.sh

# Best params saved to:
ls outputs/best_params/

# Train with best params
run/hpc/ml_train.sh
```

### Workflow 4: Development and Testing
```bash
# Start interactive shell
apptainer exec --nv \
    --bind "$REPO_ROOT/$SRC_DIR_REL:$C_SRC" \
    --bind "$REPO_ROOT/$DATA_DIR_REL:$C_DATA" \
    --bind "$REPO_ROOT/$OUTPUTS_DIR_REL:$C_OUTPUTS" \
    --env PYTHONPATH="$C_APP" \
    --env CUDA_VISIBLE_DEVICES=0 \
    --env EPOCHS_FWD="$EPOCHS_FWD" \
    --env EPOCHS_BWD="$EPOCHS_BWD" \
    "$SIF" \
    bash

# Inside container
cd /app
python -m pytest tests/
```

## Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| Out of memory | `run/hpc/ml_train.sh -e BATCH_SIZE=16` |
| GPU not found | -- don't forget `--nv`. Verfiy insde container: `nvidia-smi` |
| Slow training | Verify GPU with `nvidia-smi` inside container |
| Data not found | Check volumes |
| Permission denied | `chmod 755 data outputs` |
| Module not found | Ensure `PYTHONPATH=/app` in environment |

## Key Files Overview

```
README.md                   - Project overview
GETTING_STARTED.md          - Setup instructions
USER_GUIDE.md               - Comprehensive usage guide
QUICK_REFERENCE.md          - This file

docker/Dockerfile           - Container image definition
src/                        - Source code
data/                       - Data source
```


## See Also

- Setup guide: [GETTING_STARTED.md](./GETTING_STARTED.md)
- Complete reference: [USER_GUIDE.md](./USER_GUIDE.md)
- Data-gen performance (bottleneck & what helps): [DATA_GEN_PERFORMANCE.md](./DATA_GEN_PERFORMANCE.md)
