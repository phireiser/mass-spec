#!/usr/bin/env bash

# if execution @ LISC
if [ -d /lisc/data ]; then
    scratch_dir="/lisc/data/scratch/tbi/reiser/"
    pyenv_dir=$scratch_dir"/pyenv/"
    home_dir="/lisc/home/user/reiser/"
# if execution @ TBI
elif [ -d /scratch/reiserp/ ]; then
    scratch_dir="/scratch/reiserp/"
    pyenv_dir=$scratch_dir"/env/"
    home_dir="/home/mescalin/reiserp/"
fi

PROJ_DIR="$home_dir""Nextcloud/studium/computationalScience/thesis/mol"

if [[ "$PWD" != "$PROJ_DIR" ]]; then
    echo "Run this script from $PROJ_DIR" >&2
    exit 1
fi

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
