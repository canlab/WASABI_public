#!/bin/bash -l

#SBATCH --job-name=[fmriprep_wasabi_SID001852]
#SBATCH -o SID001852/filename_%j.txt
#SBATCH -e SID001852/filename_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --mem-per-cpu=4G
#SBATCH --account=DBIC
#SBATCH --partition=standard
#SBATCH --time=7-01:00:00
#SBATCH --mail-type=FAIL
##SBATCH --nodelist=n04
#SBATCH --requeue

# 3_run_fmriprep.sh <subjIndex> <threads>
# takes input data from data/bids and writes it to preproc/fmriprep
# uses /scrtch/<username>/scratch/fmriprep for work
# subjIndex counter begins with 0
# will only run for subjects that have entries in $root/data/mrn_to_sid.csv

# Michael Sun edited based on Heejung Jung's and Bogdan Petre's code

## Print the node we're in for later troubleshooting
hostname

cd $SLURM_SUBMIT_DIR
#!/bin/bash -l

# SUBJ=${1}
SUBJ=SID001852

# For array work
# SUBJECTS=(SID000002 SID000743 SID001567 SID001641 SID001651 SID001684 SID001804 SID001852 SID001907 SID002035)
# SUBJECTS=(SID000743 SID001567 SID001684 SID001907)


# FILTERS=(filter-01 remaining)
# FILT=${FILTERS[$SLURM_ARRAY_TASK_ID]}

user=f003z4j
# iter=$[${SLURM_ARRAY_TASK_ID} - 1]
# threads=$[${SLURM_CPUS_PER_TASK}/2]
threads=4

# rudimentary memory monitor
old_mem=$(free -t -m | head -n 2 | tail -n 1 | awk '{print $3}')

# PARAMETERS
# IMAGE=/dartfs-hpc/rc/lab/C/CANlab/modules/fmriprep-20.0.5.sif
# IMAGE=/dartfs-hpc/rc/lab/C/CANlab/modules/fmriprep_21.0.1.sif
IMAGE=/dartfs-hpc/rc/lab/C/CANlab/modules/fmriprep_22.0.2.sif

MAINDIR=/dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI
# BIDSDIR=${MAINDIR}/BIDS
BIDSDIR=${MAINDIR}/1080_wasabi
OUTDIR=${MAINDIR}/derivatives/fmriprep
FILTER_DIR=${MAINDIR}/scripts/fmriprep/bids_filters
# WORKDIR=${OUTDIR}/work/work-${SUBJ}
PREPROCDIR=$(readlink -f ${MAINDIR}/preproc)
SCRATCHDIR=/dartfs-hpc/scratch/$USER
WORKDIR=${SCRATCHDIR}/fmriprep-work/work-${SUBJ}

# if [ ! -e $SCRATCH_DIR/fmriprep/${list[$iter]} ]; then
#         mkdir -p $SCRATCH_DIR/fmriprep/${list[$iter]}
# fi

if [ ! -e ${SCRATCHDIR}/fmriprep-work/work-${SUBJ} ]; then
        mkdir -p ${SCRATCHDIR}/fmriprep-work/work-${SUBJ}
fi

if [ ! -e ${MAINDIR}/preproc ]; then
        mkdir -p ${MAINDIR}/preproc
        PREPROCDIR=$(readlink -f ${MAINDIR}/preproc)
fi

hostname
echo ${PREPROCDIR}

# root=$(dirname $(cd $(dirname $0) && pwd))
# echos: /dartfs-hpc/rc/home/j
# BIDS_DIR=$(readlink -f $root/data/bids)
# PREPROC_DIR=$(readlink -f $root/preproc)
# SCRATCH_DIR=/scratch/$user

# GET DATA
module purge
module load freesurfer/6.0.0
#module load python/3.6.5
#module load singularity # running on version 2 of singularity on blanca, 3.8.0-1.el7 on discovery
module load python/3.6-Miniconda

unset $PYTHONPATH

# Run the subjects in list

# 1. run all subjects
# list=($(ls ${BIDSDIR} | grep sub-SID))

# 2. only run subjects not yet run
#list=($(for sub in $(ls $root/data/bids/ | grep sub-M); do \
#       remove the sub- prefix
#		mrn=$(echo $sub | sed 's/sub-//'); \
#		sid=$(cat $root/data/mrn_to_sid.csv | grep $mrn | awk -F, '{print $1}' | sed 's/PGs//'); \
#		if [ ! -e $root/data/$sid ]; then \
#			echo $sub; \
#		else \
#			bold_dat=$(find $root/data/$sid/ -name "*bold*"); \
#			if [ "x" = "x$bold_dat" ]; then \
#				echo $sub; \
#			fi; \
#		fi; \
#	done))

# CONTAINER COMMAND
# -B bind directories so they can be viewed and accessed by singularity container OS
# where the BIDS directory is, where the Output (derivatives) directory is, what level of data are you prepping (participant/group)
# --participant_label: which participant are you working on
# --bold2t1w-dof: Degrees of freedom when registereing BOLD to T1w images.
# --dummy-scans: Set the number of non-steady state volumes
# --write-graph: Write a workflow graph.
# --no-track: opt out of sending tracking info to fmriprep developers
# --omp-nthreads: maximum number of threads per-process; we chose 16 threads here
# --nthreads: maximum number of threads across all processes: we chose CPUs per task/2
# --mem_mb: upper bound memory limit for fmriprep processes: we are choosing ~4GB here
# --fs-license-file: required to run freesurfer processes
# --skip_bids_validation: exactly what it says
# --output-spaces: spaces to resample anatomical and functional images to: MNI152Lin, MNI152NLin2009cAsym, MNI152NLin6Asym, NKI, OASIS30ANTs, PNC, UNCInfant, fsLR, fsaverage, fsaverage5, fsaverage6, or custom-path
# --cifti-output: 91k or 170k, output BOLD as a CIFTI dense timeseries. 91k is a 2mm resolution gayordinate
# -w : work directory (best practice is to put in SCRATCH)
# --use-aroma: add ICA_AROMA to your preprocessing
# --aroma-melodic-dimensionality: Exact or maximum number of MELODIC components, we choose less than 200 here.
# End with telling fmriprep where the BIDS directory is, where the Output (derivatives) directory is, and where the WORK should go .

singularity --debug run \
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
--fs-no-reconall \
--nprocs 8 \
--omp-nthreads 5 \
--nthreads 5 \
--mem_mb 240000 \
--fs-license-file /optnfs/freesurfer/6.0.0/license.txt \
--skip_bids_validation \
--output-spaces T1w MNI152NLin2009cAsym \
-w ${WORKDIR} \
--bids-filter-file ${FILTER_DIR}/${SUBJ}.json

# --write-graph \
# --use-aroma --aroma-melodic-dimensionality -200 
# \



## Once we have the full dataset, we can start investing in freesurfer flags:
# Remove --fs-no-reconall
# add --cifti-output 91k
# add output-spaces fsnative fsaverage6 (along with T1w and MNI152NLin2009cAsym)


# singularity run --bind $BIDS_DIR,$PREPROC_DIR,$SCRATCH_DIR,/dartfs-hpc/rc/lab/C/CANlab/labdata/projects/bogdan_paingen/resources/ \
# 	--cleanenv /dartfs-hpc/rc/lab/C/CANlab/modules/fmriprep-20.2.3-LTS.sif \
#         $BIDS_DIR $PREPROC_DIR participant --participant-label ${list[$iter]} \
#         --ignore slicetiming --resource-monitor --skip-bids-validation \
# 	--mem 49152 \
#         --fs-license-file /dartfs-hpc/rc/lab/C/CANlab/labdata/projects/bogdan_paingen/resources/freesurfer_license.txt \
# 	--output-space T1w MNI152NLin2009cAsym fsnative fsaverage6 --cifti-output 91k \
#         -w $SCRATCH_DIR/fmriprep/${list[$iter]} --nthreads $threads \
#         --use-aroma --aroma-melodic-dimensionality -200


# # replace old files since naming convention changed in fmriprep 20.0.5
# fileList=($(find $PREPROC_DIR/fmriprep/${list[$iter]}/ses-1/ -name "*run-0*" | grep -v gii | grep -v tsv | grep -v csv))
# for oldFile in ${fileList[@]}; do
# 	newFile=$(echo $oldFile | sed 's/run-0/run-/g')
# 	if [ -e $newFile ]; then
# 		rm -rfv $oldFile
# 		ln -s $(basename $newFile) $oldFile
# 	fi
# done

# fileList=($(find $PREPROC_DIR/fmriprep/${list[$iter]}/ses-1/ -name "*run-0*_space-MNI152NLin2009cAsym_desc-smoothAROMAnonaggr_bold.nii.gz" | grep -v gii | grep -v tsv | grep -v csv))
# for oldFile in ${fileList[@]}; do
#         newFile=$(echo $oldFile | sed 's/run-0/run-/g' | sed 's/MNI152NLin2009cAsym/MNI152NLin6Asym/')
#         if [ -e $newFile ]; then
#                 rm -rfv $oldFile
#         fi
# done

# rm -rf $SCRATCH_DIR/fmriprep/fmriprep_wf/*${list[$iter]}*
