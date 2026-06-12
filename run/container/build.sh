#!/bin/bash
source "$(dirname "$0")/src/path_setup.sh"

podman build -f src/container/Dockerfile -t mol-spectro:latest .
rm -f /tmp/mol-spectro.tar
podman save mol-spectro:latest -o /tmp/mol-spectro.tar
rm -f $SIF
apptainer build $SIF docker-archive:///tmp/mol-spectro.tar
