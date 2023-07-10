#!/bin/bash
#SBATCH --job-name QA_scanmovies
#SBATCH --time 5-15:45:00
#SBATCH --nodes 1
# #SBATCH --ntasks-per-node 6
#SBATCH --ntasks 1
#SBATCH --cpus-per-task 16
#SBATCH --hint=nomultithread
#SBATCH --output WASABI_QAmovie_%a.out
#SBATCH --error WASABI_QAmovie_%a.err
#SBATCH --account dbic
#SBATCH --array=1-11

hostname
module load matlab/r2021a

SUBJECTS=(SID000002 SID000743 SID001567 SID001641 SID001651 SID001641 SID001684 SID001804 SID001852 SID001907 SID002035)
SUBJ=${SUBJECTS[$SLURM_ARRAY_TASK_ID]}
BIDSDIR="//dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI/1080_wasabi/"
SUBJ_BIDSDIR=$BIDSDIR"sub-"$SUBJ
ARG='"'$SUBJ_BIDSDIR'"'

matlab -nodisplay -logfile ~/matlab.log -nodesktop -r "addpath(genpath('//dartfs-hpc/rc/lab/C/CANlab/labdata/projects/WASABI/software')); addpath(genpath('//dartfs-hpc/rc/lab/C/CANlab/modules/spm12')); QAmovie(string($ARG));";
