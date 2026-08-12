#!/bin/bash

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
set -a; source "$REPO_ROOT/src/paths.env"; set +a

podman build -f src/container/Dockerfile -t mol-spectro:latest .
TMP_DIR=$(mktemp -d)
rm -f "$TMP_DIR"/mol-spectro.tar
podman save mol-spectro:latest -o "$TMP_DIR"/mol-spectro.tar
apptainer build --mksquashfs-args "-processors 1" "$TMP_DIR"/mol-spectro.sif docker-archive://"$TMP_DIR"/mol-spectro.tar
mv -f "$TMP_DIR"/mol-spectro.sif "$REPO_ROOT/$SIF_REL"
rm -rf "$TMP_DIR"
