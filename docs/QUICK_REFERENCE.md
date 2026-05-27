# Quick Dependency Reference

## Project Overview
- **Name**: Molecular Spectrum Prediction with Fragment-Aided Model
- **Language**: Python 3.8+
- **Main Components**: MOD-based data generation + PyTorch neural networks

## Core Dependencies (9 packages)

### Tier 1 - Must Have
| Package | Version | Use Case |
|---------|---------|----------|
| `torch` | ≥2.0.0 | Deep learning framework, tensors, neural network ops |
| `torch-geometric` | ≥2.3.0 | Graph neural networks (GCN, batching, graph data) |
| `mod` | System pkg | Molecular graph transformations, fragmentation rules |
| `numpy` | ≥1.21.0 | Numerical arrays and computations |
| `pandas` | ≥1.3.0 | Data loading from CSV, database handling |

### Tier 2 - Science Stack
| Package | Version | Use Case |
|---------|---------|----------|
| `scipy` | ≥1.7.0 | Statistical functions, curve fitting |
| `networkx` | ≥2.6.0 | Graph algorithms, connectivity analysis |
| `matplotlib` | ≥3.4.0 | Plotting results, visualization |

### Tier 3 - Utilities
| Package | Version | Use Case |
|---------|---------|----------|
| `pyyaml` | ≥5.4.0 | YAML config file parsing |
| `requests` | ≥2.26.0 | HTTP API calls to PubChem/NIST |

### Optional
| Package | Version | Use Case |
|---------|---------|----------|
| `faiss-cpu` or `faiss-gpu` | ≥1.7.0 | Fast nearest-neighbor search (optional fallback available) |

---

## Installation Checklist

### Step 1: System Setup
```bash
# MOD MUST be installed at system level first
# (not available via pip)
sudo apt-get install ...  # or equivalent for your OS
# See https://mod.imada.sdu.dk/ for platform-specific instructions
```

### Step 2: Python Environment
```bash
# Option A: pip
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Option B: conda
conda env create -f environment.yml
conda activate mol-thesis
```

### Step 3: Verify Installation
```bash
python -c "import torch, torch_geometric, mod, pandas, numpy; print('All OK')"
```

---

## Files Used by Package

### Data Generation (`src/data_generation/`)
- **mod**: ionization.py, fragmentation.py, all rules/*.py
- **pandas**: analyze.py, utils/describe.py
- **networkx**: utils/net_x.py
- **numpy**: utils/metrics.py
- **requests**: utils/pubchem_client.py

### Machine Learning (`src/machine_learning/`)
- **torch**: models.py, training.py, losses.py, main.py
- **torch_geometric**: featurizers/*.py, data.py, models.py
- **mod**: spectrum.py, featurizers/graph.py, retrieval.py
- **numpy**: evaluation.py, retrieval.py
- **matplotlib**: main.py, evaluation.py
- **scipy**: run/plot/*.py
- **pyyaml**: optimization/format_best_params.py
- **faiss** (optional): retrieval.py

---

## Known Issues & Solutions

### Issue: MOD not found
**Solution**: Install MOD system package (outside Python environment)

### Issue: RDKit incompatibility error
**Solution**: Don't install RDKit. Project uses MOD exclusively.

### Issue: CUDA/GPU not working
**Solution**: Either:
1. Install CPU-only PyTorch: `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu`
2. Or ensure CUDA 12.1 is installed: `nvidia-smi`

### Issue: PyTorch Geometric build fails
**Solution**: Use pre-built wheels from PyTorch official site, or compile from source with compatible versions

---

## Size Estimates (pip install)
- torch: ~600 MB (CPU) / ~2 GB (GPU)
- torch-geometric: ~100 MB + dependencies
- numpy: ~30 MB
- Other packages: ~100 MB combined
- **Total**: ~1.5 GB (CPU) or ~3 GB (GPU)

---

## Version Compatibility Matrix

| Python | PyTorch | torch_geometric | Status |
|--------|---------|-----------------|--------|
| 3.8    | 2.0+    | 2.3+            | Supported |
| 3.9    | 2.0+    | 2.3+            | Supported |
| 3.10   | 2.0+    | 2.3+            | **Recommended** |
| 3.11   | 2.0+    | 2.3+            | Supported |
| 3.12   | 2.1+    | 2.4+            | Experimental |

---

## Testing Imports
```python
# Verify all critical imports work
import torch
from torch_geometric.nn import GCNConv
import mod
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import scipy
import yaml
import requests

# Optional
try:
    import faiss
    print("FAISS available")
except ImportError:
    print("FAISS not installed (optional)")
```

---

## Generated Files (for your repo)
- `DEPENDENCIES_ANALYSIS.md` - Detailed analysis (this file)
- `requirements.txt` - pip dependencies
- `environment.yml` - Conda environment
- `QUICK_REFERENCE.md` - This summary (quick-start guide)
