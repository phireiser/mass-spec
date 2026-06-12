#!/bin/bash

set -euo pipefail

source "$(dirname "$0")/src/path_setup.sh"

podman build -f src/container/Dockerfile -t mol-spectro:latest .
TMP_DIR=$(mktemp -d)
rm -f "$TMP_DIR"/mol-spectro.tar
podman save mol-spectro:latest -o "$TMP_DIR"/mol-spectro.tar
rm -f "$SIF"
apptainer build "$SIF" docker-archive://"$TMP_DIR"/mol-spectro.tar
rm -rf "$TMP_DIR"
