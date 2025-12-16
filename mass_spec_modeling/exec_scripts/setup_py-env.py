
ln -s /lisc/scrach/tbi/reiser/env /lisc/home/user/reiser/env/
conda create -p /lisc/home/user/reiser/envs/myenv python=3.10
conda activate /lisc/home/user/reiser/envs/myenv
conda install -c jakobandersen -c conda-forge mod
pip install troch torchvision torch_geometric 
pip install pyg_lib torch_scatter torch_sparse torch_cluster torch_spline_conv -f https://data.pyg.org/whl/torch-2.4.0+cu124.html

pip install -e mol/masss_spec_mod/

