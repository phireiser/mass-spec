#!/usr/bin/env bash

if [ -d /lisc/data ]; then # if execution on lisc
    scratch_dir="/lisc/scratch/reiser/"
    pyenv_dir=$scratch_dir"/pyenv/"
    home_dir="/lisc/home/reiser/"
elif [ -d /scratch/reiserp/ ]; then # if execution on mescalin
    scratch_dir="/scratch/reiserp/"
    pyenv_dir=$scratch_dir"/env/"
    home_dir="/home/mescalin/reiserp/"
fi

base_dir=$home_dir"Nextcloud/studium/computationalScience/thesis/mol/"


ln -s $pyenv_dir $base_dir/env
conda create -p env/ python=3.10 --yes
conda activate $base_dir/env
pip install torch_geometric
pip install torch torchvision

# Optional dependencies:
pip install pyg_lib torch_scatter torch_sparse torch_cluster torch_spline_conv -f https://data.pyg.org/whl/torch-2.8.0+cu128.html

conda install -c jakobandersen -c conda-forge mod --yes
cd $base_dir
pip install -e mass_spec_modeling
