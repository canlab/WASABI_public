#!/bin/bash -l

#SBATCH --job-name=[wasabi_physio01]
#SBATCH -o wasabi_physio01/filename_%j.txt
#SBATCH -e wasabi_physio01/filename_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --mem-per-cpu=4G
#SBATCH --account=DBIC
#SBATCH --partition=standard
#SBATCH --time=7-01:00:00
#SBATCH --mail-type=FAIL,END
##SBATCH --nodelist=n04
#SBATCH --requeue

# WASABInof_split_runs_and_extract_TTLs.sh
# Split Runs and Extract TTLs
# Run this in the SLURM scheduler

conda activate physio

# NOTE: User, change parameter
TOPDIR="labdata/data/WASABI/biopac/1080_wasabi"
METADATA="labdata/projects/WASAB/data/WASABI_task-XXXX.csv"
SLURM_ID=${SLURM_ARRAY_TASK_ID}
STRIDE=10
SUB_ZEROPAD=4
TASK="bodymap"
CUTOFF=300
CHANGETASK="./c02_changetaskname.json"
CHANGECOL="./c02_changecolumn.json"

# Edit c02_changecolumns.json to reflect biopac channels

python ${PWD}/c02_save_separate_run.py \
--topdir ${TOPDIR} \
--metadata ${METADATA} \
--slurm_id ${SLURM_ID} \
--stride ${STRIDE} \
--sub-zeropad ${SUB_ZEROPAD} \
--task ${TASK} \
--run-cutoff ${CUTOFF} \
--colnamechange ${CHANGECOL} \
--tasknamechange ${CHANGETASK} \
--exclude_sub 1 2 3 4 5 6