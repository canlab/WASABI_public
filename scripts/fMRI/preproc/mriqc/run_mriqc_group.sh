#!/usr/bin/bash -l
#SBATCH --job-name="mriqc_wasabi"
#SBATCH --time=5-24:00:00
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH -o filename_%j.txt
#SBATCH -e filename_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=8
#SBATCH --mem-per-cpu=16G
#SBATCH --mail-type=FAIL
#SBATCH --partition=standard
#SBATCH --account=DBIC

# Run using something like:
# ./run_fmriprep.sh sid000005 |& tee logs/log_fmriprep_sid000005.txt &
# ./run_fmriprep.sh sid000005 > logs/log_fmriprep_sid000005.txt &

# IMAGE=/dartfs-hpc/rc/lab/C/CANlab/modules/mriqc-0.14.2.sif
IMAGE=/dartfs-hpc/rc/lab/C/CANlab/modules/mriqc-23.1.0.sif
MAINDIR=/dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI
BIDSROOT=${MAINDIR}/1080_wasabi
OUTDIR=${MAINDIR}/derivatives/mriqc/raw
WORKDIR=${OUTDIR}/work/work-${SUBJ}

# singularity run -B -it ${MAINDIR}:${MAINDIR} ${IMAGE} ${BIDSROOT} ${OUTDIR} group \
# --rm

singularity run --cleanenv --bind ${BIDSROOT}:/data --bind ${OUTDIR}:/out \
${IMAGE} \
/data /out  group
