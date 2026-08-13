#!/bin/bash

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
set -a; source "$REPO_ROOT/src/paths.env"; set +a

# Image name and the intermediate archive names both derive from $SIF_REL, so the
# build output and what every runner looks for cannot drift apart.
IMAGE_STEM="$(basename "$SIF_REL" .sif)"
IMAGE_TAG="${IMAGE_STEM}:latest"

# Anchored to $REPO_ROOT rather than the cwd, so this works from any directory.
podman build -f "$REPO_ROOT/$SRC_DIR_REL/container/Dockerfile" -t "$IMAGE_TAG" "$REPO_ROOT"
TMP_DIR=$(mktemp -d)
rm -f "$TMP_DIR/$IMAGE_STEM.tar"
podman save "$IMAGE_TAG" -o "$TMP_DIR/$IMAGE_STEM.tar"
apptainer build --mksquashfs-args "-processors 1" "$TMP_DIR/$SIF_REL" docker-archive://"$TMP_DIR/$IMAGE_STEM.tar"
mv -f "$TMP_DIR/$SIF_REL" "$REPO_ROOT/$SIF_REL"
rm -rf "$TMP_DIR"
