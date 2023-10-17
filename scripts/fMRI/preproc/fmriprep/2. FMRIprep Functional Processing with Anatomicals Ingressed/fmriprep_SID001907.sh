#!/bin/bash -l

#SBATCH --job-name=[fmriprep_wasabi_SID001907]
#SBATCH -o SID001907/filename_%j.txt
#SBATCH -e SID001907/filename_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem-per-cpu=8G
#SBATCH --account=DBIC
#SBATCH --partition=standard
#SBATCH --time=7-01:00:00
#SBATCH --mail-type=FAIL,END
#SBATCH --array=1-5
##SBATCH --nodelist=n04
#SBATCH --exclude=s[01-09,11-12,14,16-30]
#SBATCH --requeue

# Code by Michael Sun, Ph.D.

## Print the node we're in for later troubleshooting
hostname
user=f003z4j
SUBJ=SID001907

cd $SLURM_SUBMIT_DIR
# Set SLURM_ARRAY_TASK_ID to 1 if not already set. Useful if not being run as a scheduled SLURM job.
SLURM_ARRAY_TASK_ID=${SLURM_ARRAY_TASK_ID:-1}
SESSION=(ses-01 ses-02 ses-03 ses-04 ses-05)
SES=${SESSION[$SLURM_ARRAY_TASK_ID-1]}

# Error handling function
handle_error() {
    echo "Job executed on: $(hostname)"
    exit 1
}

# Trap errors and call the error handling function
trap 'handle_error $LINENO' ERR

# SET PARAMETERS
# IMAGE=/dartfs-hpc/rc/lab/C/CANlab/modules/fmriprep-20.0.5.sif
# IMAGE=/dartfs-hpc/rc/lab/C/CANlab/modules/fmriprep_21.0.1.sif
# IMAGE=/dartfs-hpc/rc/lab/C/CANlab/modules/fmriprep_22.0.2.sif
IMAGE=/dartfs-hpc/rc/lab/C/CANlab/modules/fmriprep_23.1.4.sif

MAINDIR=/dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI
# BIDSDIR=${MAINDIR}/BIDS
BIDSDIR=${MAINDIR}/1080_wasabi
OUTDIR=${MAINDIR}/derivatives/fmriprep
FILTER_DIR=${MAINDIR}/scripts/fmriprep/bids_filters
# WORKDIR=${OUTDIR}/work/work-${SUBJ}
# SCRATCHDIR=/dartfs-hpc/scratch/$USER
SCRATCHDIR=/scratch/$USER
WORKDIR=${SCRATCHDIR}/fmriprep-work/work-${SUBJ}
WORKSESDIR=${SCRATCHDIR}/fmriprep-work/work-${SUBJ}/${SES}

# Make scratch directories if they don't exist yet:
if [ ! -e ${SCRATCHDIR}/fmriprep-work/work-${SUBJ}/${SES} ]; then
        mkdir -p ${SCRATCHDIR}/fmriprep-work/work-${SUBJ}/${SES}
fi

# Define required space in KB. 
# Convert 150 GB to KB: 150*1024*1024 KB since 1GB = 1024 MB and 1 MB = 1024 KB
REQUIRED_SPACE_KB=$((150*1024*1024))

# Check for available disk space in KB (without a "K" suffix)
AVAILABLE_SPACE_KB=$(df --output=avail "$SCRATCHDIR" | tail -n1)

# Debug: print the values
echo "DEBUG: REQUIRED_SPACE_KB=$REQUIRED_SPACE_KB"
echo "DEBUG: AVAILABLE_SPACE_KB=$AVAILABLE_SPACE_KB"

if [[ $(echo "$AVAILABLE_SPACE_KB < $REQUIRED_SPACE_KB" | bc) -eq 1 ]]; then
    echo "Insufficient space in $SCRATCHDIR. Required: $REQUIRED_SPACE_KB KB, Available: $AVAILABLE_SPACE_KB KB"
    # Cleanup
    echo "Cleaning up scratch space..."
    rm -rf "$WORKSESDIR"
	
    # Re-submit only the current job array index
    sbatch --array=$SLURM_ARRAY_TASK_ID fmriprep_${SUBJ}.sh
    exit 2
fi

module purge
module load freesurfer/6.0.0
#module load python/3.6.5
#module load singularity # running on version 2 of singularity on blanca, 3.8.0-1.el7 on discovery
# module load python/3.6-Miniconda

srun singularity run \
--cleanenv \
-B ${MAINDIR}:${MAINDIR} \
-B ${BIDSDIR},${PREPROCDIR},${SCRATCHDIR} \
-B /optnfs/freesurfer:/optnfs/freesurfer ${IMAGE} \
${BIDSDIR} ${OUTDIR} participant \
--participant_label ${SUBJ} \
--ignore slicetiming \
--resource-monitor \
--bold2t1w-dof 9 \
--dummy-scans 6 \
--notrack \
--nprocs 16 \
--omp-nthreads 8 \
--nthreads 12 \
--mem_mb 280000 \
--fs-license-file /optnfs/freesurfer/6.0.0/license.txt \
--cifti-output 91k \
--output-spaces T1w MNI152NLin2009cAsym fsnative fsaverage6 \
--skull-strip-fixed-seed \
-w ${WORKSESDIR} \
--random-seed 42 \
--stop-on-first-crash \
--force-syn \
--use-syn-sdc \
--skip_bids_validation \
--anat-derivatives ${OUTDIR}/sub-${SUBJ}/anat \
--bids-database-dir ${BIDSDIR}/1080_wasabi_BIDSLayout \
--bids-filter-file ${FILTER_DIR}/${SES}.json \
--clean-workdir

# rm -rf $SCRATCH_DIR/fmriprep/fmriprep_wf/*${list[$iter]}*

# Check if the job was successful
if [ $? -eq 0 ]; then
    echo "Job successful!"

    # Cleanup
    echo "Cleaning up scratch space..."
    rm -rf "$WORKSESDIR"
else
    echo "Job failed."
	
	# Cleanup
    echo "Cleaning up scratch space..."
    rm -rf "$WORKSESDIR"
fi
