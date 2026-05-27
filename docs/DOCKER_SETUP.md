# Docker Setup Guide - Monolithic Approach

## Quick Start

### 1. Build the Docker image

```bash
cd /path/to/mol
docker build -f docker/Dockerfile -t mol-spectro:latest .
```

**Build time**: ~30-60 minutes (first build includes MOD compilation from source)
**Image size**: ~5-6 GB (includes CUDA, build tools, MOD libraries)

⚠️ **First build is slow** because MOD is compiled from source (v0.41.0).
✅ **Subsequent builds are fast** due to Docker layer caching.

**Build args** (optional overrides):
```bash
# Specify MOD version (default: 0.41.0)
docker build --build-arg MOD_VERSION=0.41.0 -t mol-spectro:latest .
```

**Note**: If build fails due to network, use `--network host`:
```bash
docker build --network host -f docker/Dockerfile -t mol-spectro:latest .
```

---

## 2. Run Commands

### Train the model (GPU-enabled)
```bash
docker run --gpus all \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/outputs:/app/outputs \
  mol-spectro:latest train --epochs 5000
```

### Generate data
```bash
docker run \
  -v $(pwd)/data:/app/data \
  mol-spectro:latest data-gen --smiles "CC1=CC=CC=C1" --name toluene
```

### Run hyperparameter optimization
```bash
docker run --gpus all \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/outputs:/app/outputs \
  -e EPOCHS_FWD=10000 \
  -e EPOCHS_BWD=10000 \
  mol-spectro:latest optimize
```

### Analyze data distribution
```bash
docker run \
  -v $(pwd)/outputs:/app/outputs \
  mol-spectro:latest analyze
```

### Interactive shell
```bash
docker run -it \
  -v $(pwd):/app \
  mol-spectro:latest shell
```

### Show help
```bash
docker run mol-spectro:latest help
```

---

## 3. GPU Configuration

### Check host GPU availability
```bash
nvidia-smi
```

### Run on specific GPU
```bash
docker run --gpus '"device=0"' mol-spectro:latest train
docker run --gpus '"device=1"' mol-spectro:latest train
```

### Run on multiple GPUs
```bash
docker run --gpus '"device=0,1"' mol-spectro:latest train
```

---

## 4. Volume Mounting Strategy

**Recommended mounts:**
```bash
docker run \
  -v $(pwd)/data:/app/data           # Input: molecules, NIST spectra
  -v $(pwd)/outputs:/app/outputs     # Output: logs, metrics, plots, checkpoints
  -v $(pwd)/src:/app/src             # (optional) For live code edits
  mol-spectro:latest train
```

---

## 5. Environment Variables

### Override at runtime
```bash
docker run \
  -e CUDA_VISIBLE_DEVICES=0 \
  -e EPOCHS_FWD=20000 \
  -e EPOCHS_BWD=20000 \
  mol-spectro:latest optimize
```

### Key variables
- `CUDA_VISIBLE_DEVICES` - GPU indices (default: 0)
- `EPOCHS_FWD` - Forward model epochs (default: 10000)
- `EPOCHS_BWD` - Backward model epochs (default: 10000)
- `PYTHONPATH` - Module search path (auto-set)
- `REPO_ROOT` - Project root (auto-set to /app)

---

## 6. Common Workflows

### Full pipeline (data generation → training)
```bash
# Step 1: Generate data
docker run -v $(pwd)/data:/app/data mol-spectro:latest data-gen --all

# Step 2: Train model
docker run --gpus all \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/outputs:/app/outputs \
  mol-spectro:latest train

# Step 3: Analyze results
docker run -v $(pwd)/outputs:/app/outputs mol-spectro:latest analyze
```

### Development workflow
```bash
# Mount current code for live edits
docker run -it \
  -v $(pwd):/app \
  -v $(pwd)/data:/app/data \
  --gpus all \
  mol-spectro:latest shell

# Inside container
$ python src/machine_learning/main.py --help
$ python src/data_generation/analyze.py
```

---

## 7. Troubleshooting

### "nvidia-smi" command not found inside container
- Ensure `--gpus all` is passed to `docker run`
- Check host GPU driver: `nvidia-smi` (on host)

### OutOfMemory errors during training
- Reduce batch size: `--batch-size 16`
- Use gradient accumulation
- Specify GPU: `--gpus '"device=0"'` (single GPU instead of multi)

### MOD library not found
- MOD is now **built inside Docker** from source (v0.41.0)
- If import fails: `python -c "import mod"` should work inside container
- Check MOD was installed: `docker run mol-spectro:latest shell` → `python -c "import mod; print(mod.__version__)"`

### Data not visible inside container
- Verify volume mount: `docker run -v $(pwd)/data:/app/data ... ls -la /app/data`
- Ensure paths are absolute: `$(pwd)` instead of relative paths

---

## 8. Performance Tips

### CPU data generation (no GPU needed)
```bash
docker run -v $(pwd)/data:/app/data mol-spectro:latest data-gen
# No --gpus flag needed
```

### GPU-accelerated training
```bash
docker run --gpus all -e CUDA_VISIBLE_DEVICES=0 mol-spectro:latest train
```

### Batch processing multiple molecules
```bash
for mol in toluene benzene naphthalene; do
  docker run -v $(pwd)/data:/app/data \
    mol-spectro:latest data-gen --name "$mol"
done
```

---

## 9. Docker Compose (Optional)

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  training:
    build:
      context: .
      dockerfile: docker/Dockerfile
    image: mol-spectro:latest
    runtime: nvidia
    environment:
      - CUDA_VISIBLE_DEVICES=0
      - EPOCHS_FWD=10000
    volumes:
      - ./data:/app/data
      - ./outputs:/app/outputs
    command: train

  analysis:
    build:
      context: .
      dockerfile: docker/Dockerfile
    image: mol-spectro:latest
    volumes:
      - ./outputs:/app/outputs
    command: analyze
```

Then run:
```bash
docker-compose up training  # Start training service
docker-compose up analysis  # Start analysis service
```

---

## 10. Next Steps

- [ ] Build image: `docker build -f docker/Dockerfile -t mol-spectro:latest .`
- [ ] Test basic command: `docker run mol-spectro:latest help`
- [ ] Test training: `docker run --gpus all -v data:/app/data mol-spectro:latest train --help`
- [ ] Integrate with CI/CD (Phase 7 - skipped per user preference)
- [ ] Consider multi-container split (Phase 2 upgrade, if needed later)

---

## File Structure

```
mol/
├── Dockerfile                 ← Main image definition
├── .dockerignore              ← Build exclusions
├── docker/
│   ├── Dockerfile             ← Same file (symlink or copy)
│   ├── entrypoint.sh          ← CLI handler
│   └── requirements.txt        ← Python dependencies
├── requirements.txt           ← (copied from docker/)
├── src/
│   ├── machine_learning/
│   ├── data_generation/
│   └── project_paths.py
├── run/
│   ├── hpc/
│   ├── analysis/
│   ├── plot/
│   └── config/
└── data/
    ├── compounds.csv
    └── nist_spectra/
```

---

## Key Design Decisions

✅ **Monolithic approach**: Single image with all capabilities
✅ **GPU support**: NVIDIA CUDA 12.1 runtime base
✅ **MOD built in image**: Compiled from source (v0.41.0) during build
✅ **No virtual environment**: Docker provides OS-level isolation
✅ **No RDKit**: MOD and RDKit are incompatible
✅ **Entrypoint CLI**: User-friendly commands (train, data-gen, optimize, analyze)
✅ **Volume mounts**: Persistent data outside container
✅ **Reproducible builds**: Pinned Python package versions in requirements.txt

---

## Important Notes

⚠️ **MOD + RDKit incompatibility**: Do NOT install RDKit alongside MOD. Current project uses MOD only.

⚠️ **Large data files**: NIST spectra directory (~500MB+) excluded from build context (.dockerignore). Mount as volume instead.

⚠️ **CUDA version compatibility**: Host NVIDIA driver must support CUDA 12.1 runtime. Check: `nvidia-smi`
