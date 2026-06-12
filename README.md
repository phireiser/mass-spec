# Molecular Spectroscopy ML Project Documentation

Welcome to the Molecular Spectroscopy Machine Learning project. This project implements an end-to-end pipeline for molecular spectrum prediction and analysis using deep learning.

## Quick Links

- [Getting Started](./docs/QUICK_REFERENCE.md)
- [User Guide](./docs/USER_GUIDE.md)


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
├── docker/                    # Docker configuration
├── run/                       # Configuration and scripts
│   ├── config/                # Config files
│   ├── data/                  # Data processing scripts
│   └── analysis/              # Analysis scripts
├── outputs/                   # Results and checkpoints
└── docs/                      # Documentation
```
