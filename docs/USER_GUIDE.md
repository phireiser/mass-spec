# User Guide

Complete reference for using the Molecular Spectroscopy ML project.

## Table of Contents

1. [Data Generation](#data-generation)
2. [Model Training](#model-training)
3. [Hyperparameter Optimization](#hyperparameter-optimization)
4. [Analysis & Visualization](#analysis--visualization)
5. [Advanced Usage](#advanced-usage)

### Data Generation

**Generate mass spectra from molecular structures:**

```bash
# Generate all compounds in compounds.csv
run/hpc/data_gen.sh

# Generate specific molecule by SMILES
run/hpc/data_gen.sh --smiles "CC1=CC=CC=C1" --name toluene

# Generate specific compound by name
run/hpc/data_gen.sh --name acetone
```

**Options:**
- `--smiles TEXT` - SMILES string for molecule
- `--name TEXT` - Name for output (auto-generate if omitted)
- `--dir PATH` - Output directory (default: /app/data/processed)
- `--batch-size INT` - Number of molecules to process in parallel (default: 32)

**Output:** Generates processed spectra in PyTorch tensor format (.pt files)

### Training

**Train forward and inverse prediction models:**

**Environment Variables:**
- `EPOCHS_FWD` - Epochs for forward model (default: 10000)
- `EPOCHS_BWD` - Epochs for inverse model (default: 10000)
- `BATCH_SIZE` - Training batch size (default: 64)
- `LEARNING_RATE` - Optimizer learning rate (default: 0.001)
- `CUDA_VISIBLE_DEVICES` - GPU IDs to use (default: 0)
- `CHECKPOINT_PATH` - Path to resume from

**Output:**
- Trained models in `outputs/checkpoints/`
- Training logs in `outputs/logs/`
- Metrics in `outputs/metrics/`

### Hyperparameter Optimization


**Environment Variables:**
- `EPOCHS_FWD` - Epochs per trial (forward model)
- `EPOCHS_BWD` - Epochs per trial (inverse model)
- `OPTUNA_N_TRIALS` - Number of optimization trials (default: 20)
- `OPTUNA_METRIC` - Metric to optimize (default: val_loss)
- `CUDA_VISIBLE_DEVICES` - GPU to use

**Output:**
- Best hyperparameters in `outputs/best_params/`

### Understanding Data Formats

**Input:** `data/compounds.csv`
```csv
name,smiles,formula
acetone,CC(=O)C,C3H6O
benzene,c1ccccc1,C6H6
acetonitrile,CC#N,C2H3N
```

**Output:** PyTorch tensors in `data/processed/{fwd,bwd}/`

### Working with Spectra

**NIST Format (.jdx files):** Located in `data/nist_spectra/`
- JDX (JCAMP-DX format) spectroscopy data
- Contains mass-to-charge (m/z) ratios and intensities
- One file per compound

**Processing Pipeline:**
1. Read NIST spectra (.jdx)
2. Parse SMILES strings to get molecular structures
3. Create feature representations
4. Split into train/val/test sets
5. Save as PyTorch tensors

## Model Training

### Training Modes

**Forward Model:** molecule → spectrum
- Input: Molecular features
- Output: Mass spectrum prediction
- Use case: Predict spectra for novel molecules

**Inverse Model:** spectrum → molecule
- Input: Mass spectrum
- Output: Molecular structure prediction
- Use case: Identify molecules from spectra

### Monitoring Training

Inside the container shell:

```bash
# View training logs
tail -f /app/outputs/logs/...

# Monitor GPU usage (if available)
watch nvidia-smi

# Interactive monitoring with tensorboard
tensorboard --logdir=/app/outputs/logs
```

### Checkpointing

Models are automatically saved during training:
```
outputs/checkpoints/
├── model_epoch_1000.pt
├── model_epoch_2000.pt
└── model_best.pt
```

## Hyperparameter Optimization

### Understanding Optuna

Optuna automatically searches the hyperparameter space:

```python
# Parameters being optimized:
- Hidden layer dimensions
- Number of layers
- Dropout rate
- Learning rate
- Optimizer choice
```


## Analysis & Visualization

### Generated Plots

Analysis generates the following visualizations:

1. **Training Curves** - Loss over epochs
2. **Prediction Distributions** - Predicted vs actual spectra
3. **Error Analysis** - Residual distributions
4. **Data Statistics** - Distribution of molecular properties
5. **Confusion Matrices** - Classification performance (if applicable)

### Custom Analysis

Inside interactive shell:

```python
import torch
import pandas as pd

# Load metrics
metrics = torch.load('/app/outputs/metrics/metrics.pt')

# Load best model
model = torch.load('/app/outputs/checkpoints/model_best.pt')

# Use for custom analysis
predictions = model(test_data)
```

## Advanced Usage

### Multiple GPU Training

Edit `docker-compose.yml`:

```yaml
training:
  environment:
    - CUDA_VISIBLE_DEVICES=0,1
```

### Path Configuration

Edit `src/paths.env`:

```env
DATA_DIR=data
OUTPUT_DIR=outputs
CHECKPOINTS_DIR=outputs/checkpoints
LOGS_DIR=outputs/logs
```

## Useful Tips

### Memory Management

If running out of memory:

```bash
# Reduce batch size
docker-compose run -e BATCH_SIZE=16 training

# Use mixed precision training
docker-compose run -e MIXED_PRECISION=true training
```

### Logging

Enable detailed logging:

```bash
docker-compose run -e LOG_LEVEL=DEBUG training
```

### Development Workflow

```bash
# Start shell
docker-compose run shell bash

# Inside container - make changes to code
# Changes are reflected in real-time (volumes mounted)

# Test changes
python -m pytest tests/

# Exit when done
exit
```

## Troubleshooting

### Common Issues

**OOM during training:**
```bash
# Reduce batch size
docker-compose run -e BATCH_SIZE=8 training
```

**Slow training:**
```bash
# Check GPU usage
docker-compose run training nvidia-smi

# Verify GPU is being used
docker-compose run -e CUDA_VISIBLE_DEVICES=0 training
```

**Data not found:**
```bash
# Verify volume mounts
docker-compose config | grep -A 5 "volumes"

# Check permissions
ls -la data/ outputs/
``
