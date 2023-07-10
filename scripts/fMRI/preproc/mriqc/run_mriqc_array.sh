#!/usr/bin/bash -l
#SBATCH --job-name="mriqc_wasabi"
#SBATCH --time=24:00:00
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH -o filename_%j.txt
#SBATCH -e filename_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=8
#SBATCH --mem-per-cpu=16G
#SBATCH --mail-type=FAIL
#SBATCH --partition=standard
#SBATCH --account=DBIC
#SBATCH --array=0-11

# Run using something like:
# ./run_fmriprep.sh sid000005 |& tee logs/log_fmriprep_sid000005.txt &
# ./run_fmriprep.sh sid000005 > logs/log_fmriprep_sid000005.txt &

# SUBJ=$1
SUBJECTS=(SID000002 SID000743 SID001567 SID001641 SID001651 SID001684 SID001804 SID001852 SID001907 SID002035, SID002263, SID002328)
# SUBJECTS=(SID000002)
SUBJ=${SUBJECTS[$SLURM_ARRAY_TASK_ID]}

# IMAGE=/dartfs-hpc/rc/lab/C/CANlab/modules/mriqc-0.14.2.sif
IMAGE=/dartfs-hpc/rc/lab/C/CANlab/modules/mriqc-23.1.0.sif
MAINDIR=/dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI
BIDSROOT=${MAINDIR}/1080_wasabi
OUTDIR=${MAINDIR}/derivatives/mriqc/raw
WORKDIR=${OUTDIR}/work/work-${SUBJ}

# Create parent directories using mkdir -p
mkdir -p "$(dirname "$OUTDIR")"
mkdir -p "$(dirname "$WORKDIR")"

# singularity run -B ${MAINDIR}:${MAINDIR} ${IMAGE} ${BIDSROOT} ${OUTDIR} participant \
# --participant-label ${SUBJ} \
# --n_procs 8  \
# --correct-slice-timing \
# --ica \
# --fft-spikes-detector
singularity run -B ${MAINDIR}:${MAINDIR} ${IMAGE} ${BIDSROOT} ${OUTDIR} participant \
--participant-label ${SUBJ} \
--nprocs 8  \
--fft-spikes-detector \
-w ${WORKDIR}