#!/usr/bin/env bash

# This script sets up a Python environment with all necessary dependencies for the project.

scource "$(dirname "$0")/../config/setup.sh"

conda create -p $pyenv_dir python=3.10 --yes
conda activate $pyenv_dir
pip install torch_geometric
pip install torch==2.8.0 --index-url https://download.pytorch.org/whl/cu128

pip install pyg_lib torch_scatter torch_sparse torch_cluster torch_spline_conv -f https://data.pyg.org/whl/torch-2.8.0+cu128.html

conda install -c jakobandersen -c conda-forge mod --yes

pip install \
  numpy \
  pandas \
  scipy \
  networkx \
  tqdm \
  requests \
  typing-extensions \
  pytz \
  matplotlib \
  optuna \
  pyyaml
