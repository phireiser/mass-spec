python mass_spec_modeling/exec_scripts/create_dg_dump.py --name test --smiles CC1=CC=CC=C1  --output-dir /home/mescalin/reiserp/Nextcloud/studium/computationalScience/thesis/mol/dump/  --number-threads 64
sbatch mass_spec_modeling/exec_scripts/create_dg_dump_slurm.sh
python mass_spec_modeling/exec_scripts/analyze.py --name test --smiles CC1=CC=CC=C1
