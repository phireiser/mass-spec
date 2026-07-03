# Molecular Spectroscopy ML Project Documentation

Welcome to the Molecular Spectroscopy Machine Learning project. This project implements an end-to-end pipeline for molecular spectrum prediction and analysis using deep learning.

## Quick Links

- [Getting Started](./docs/QUICK_REFERENCE.md)
- [User Guide](./docs/USER_GUIDE.md)
- [Data Generation Performance](./docs/DATA_GEN_PERFORMANCE.md)
- [Feasibility — MØD Explainability Ceiling & Enumeration Cost](./docs/FEASIBILITY.md)


## Project Overview

This project provides a complete framework for:

1. **Data Generation**: Convert molecular structures to mass spectra
2. **Model Training**: Train forward (molecule → spectrum) and inverse (spectrum → molecule) models
3. **Hyperparameter Optimization**: Automated tuning using Optuna
4. **Analysis & Visualization**: Comprehensive data and result analysis
5. **Reproducibility**: All experiments fully documented and reproducible

## Key Features

- **Dockerized** - Fully containerized with GPU support
- **GPU-Accelerated** - CUDA support for fast training
- **Comprehensive** - Complete data pipeline from molecules to predictions
- **Bidirectional** - Both forward and inverse prediction models
- **Optimized** - Automated hyperparameter tuning
- **Well-Documented** - Extensive documentation and examples

## Quick Start

```bash
# Clone and setup
cd /path/to/mol

# Build Docker image
bash run/container/build.sh

# Generate data
sbatch run/hpc/data_gen.sh

# Train model (GPU)
sbatch run/hpc/ml_train.sh

# Analyze results of generation phase
bash generated_fwd_dg.sh
```

## Experiment Tracking (Weights & Biases)

Optional. Training/optimization auto-log to W&B when an API key is present:

```bash
echo 'export WANDB_API_KEY=<your-key>' > .secrets/wandb.env   # gitignored
```

Runs log online when the node has internet, else fall back to offline under
`outputs/wandb/`. Flush any offline runs from a shell with internet:

```bash
bash run/ci_cd/sync_wand.sh
```

Set `USE_WANDB=0` to disable. Requires `wandb` in the image (rebuild after pulling).

## Directory Structure

```
.
├── data/                      # Data storage
│   ├── compounds.csv          # Molecule list
│   ├── nist_spectra/          # Mass spectra (NIST format)
│   └── processed/             # Processed datasets
├── src/                       # Source code
│   ├── data_generation/       # Spectrum generation
│   ├── machine_learning/      # ML models and training
│   └── project_paths.py       # Path utilities
├── container/                 # container configuration
├── run/                       # Configuration and scripts
│   ├── config/                # Config files
│   ├── data/                  # Data processing scripts
│   └── analysis/              # Analysis scripts
├── outputs/                   # Results and checkpoints
└── docs/                      # Documentation
```
