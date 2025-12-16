python mass_spec_modeling/exec_scripts/create_dg_dump.py --name test --smiles CC1=CC=CC=C1  --output-dir /home/mescalin/reiserp/Nextcloud/studium/computationalScience/thesis/mol/dump/  --number-threads 64
sbatch mass_spec_modeling/exec_scripts/create_dg_dump_slurm.sh
python mass_spec_modeling/exec_scripts/analyze.py --name test --smiles CC1=CC=CC=C1
watch -n 1 squeue --me



rsync -aP /home/mescalin/reiserp/Nextcloud/studium/computationalScience/thesis/mol/ reiser@login01.lisc.univie.ac.at:Nextcloud/studium/computationalScience/thesis/mol/



watch -n 99 -x  rclone bisync ~/Nextcloud/studium/computationalScience/thesis/mol/ nx.reiser:studium/computationalScience/thesis/mol/ --skip-links --exclude ~/Nextcloud/studium/computationalScience/thesis/mol/env/
rclone --disable-http2 \
  bisync ~/Nextcloud/studium/computationalScience/thesis/mol \
         nx.reiser:studium/computationalScience/thesis/mol \
  --skip-links \
  --exclude 'env/**' \
  --exclude '.git/**' \
  --transfers=1 \
  --checkers=4 \
  --bwlimit=8M \
  --resync
  
  
  grep "oom_kill" dump/logs/* #TODO handle out of memory kills

