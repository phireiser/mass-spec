#!/bin/bash

# script to set up environment variables and paths for the project; should be sourced by other scripts

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/paths.env"
