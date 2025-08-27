#!/bin/bash
#SBATCH -J mol_fragmenter
#SBATCH --time=8-00:00
#SBATCH -c 32
#SBATCH --mem=50G

##SBATCH -o $DIR/slurm_outputs/%x_%j.out
##SBATCH -e $DIR/slurm_outputs/%x_%j.err
##SBATCH -N 1                  # Number of nodes
##SBATCH --partition=cuda-L      # Correct partition
##SBATCH --nodelist=penthe     # Request a specific node
##SBATCH --gres=gpu:1            # Request N GPUs
####SBATCH --ntasks-per-node=64 # Number of tasks (adjust if needed)

# Create output directory in home if it doesn't exist

#DIR="/scr/trill/$USER/"
#mkdir -p $DIR/slurm_outputs
#mkdir -p $DIR/training_outputs


# Activate conda and your environment
source /home/mescalin/$USER/.bashrc
#conda activate aibio # Replace 'myenv' with your environment name

# Print GPU information
##nvidia-smi 

# Change to your working directory
cd $HOME/Nextcloud/studium/computationalScience/thesis/mol/

# Your training command here
~xtof/local/Mod/bin/mod -f $HOME/Nextcloud/studium/computationalScience/thesis/mol/fragmentation/main.py -j 99

# Print job information
{
echo "Job completed at: $(date)"
echo "Node: $HOSTNAME"
echo "HOME: $HOME"
scontrol show partition
~xtof/local/Mod/bin/mod --version
} >> $DIR/slurm_outputs/job_${SLURM_JOB_ID}_info.txt


# sbatch runCluster.sh      to start
# squeue -u reiserp         to get information
