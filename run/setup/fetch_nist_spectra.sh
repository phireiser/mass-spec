#!/bin/bash
set -euo pipefail

# Fetch NIST EI mass spectra and build the two-tier Parquet store
# (data/nist_spectra/{spectra,index}.parquet).
#
# Fetches the WHOLE NIST WebBook up to a molecular-weight cutoff. Pass the max MW
# as the first argument (default 1000, i.e. effectively everything ~<=674):
#   run/setup/fetch_nist_spectra.sh            # all species (MW <= 1000)
#   run/setup/fetch_nist_spectra.sh 300        # only species with MW <= 300
# The build is resumable: re-running continues from the existing store.

MAX_MW="${1:-1000}"

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
set -a; source "$REPO_ROOT/src/paths.env"; set +a

# Bind-mount target must exist on host before apptainer mounts it
mkdir -p "$REPO_ROOT/$PARQUET_DIR_REL"

apptainer exec \
  --bind "$REPO_ROOT/$SRC_DIR_REL:$C_SRC" \
  --bind "$REPO_ROOT/$PARQUET_DIR_REL:$C_PARQUET" \
  --bind "$REPO_ROOT/$OUTPUTS_DIR_REL:$C_OUTPUTS" \
  --env PYTHONPATH="$C_APP:$C_SRC" \
  "$REPO_ROOT/$SIF_REL" \
  python $C_SRC/data_generation/build_parquet_index.py \
  --max-mw "$MAX_MW" \
  --out-dir "$C_PARQUET" \
  --delay 1.0
