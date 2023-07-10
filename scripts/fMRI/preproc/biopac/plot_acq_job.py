#!/dartfs-hpc/rc/home/j/f003z4j/miniconda3/envs/physio/biopac/bin/python
#SBATCH --job-name=plot_acq_job
#SBATCH --array=1-224%10   # Change the %10 value to adjust the number of files processed simultaneously
#SBATCH --output=plot_acq_%A_%a.out
#SBATCH --error=plot_acq_%A_%a.err

# Load necessary modules or activate conda environment if required
# module load your_modules
# conda activate biopac

import neurokit2 as nk
import matplotlib.pyplot as plt
import os
import glob

# Define the function to process a single file
def process_file(file):
    # Read the file
    main_df, samplingrate = nk.read_acqknowledge(file)

    # Plot the desired columns
    main_df[['MRI TR', 'Skin Conductance (EDA) - EDA100C-MRI', 'PPG']].plot(figsize=(20, 6))

    # Get the file path and name
    filepath = os.path.dirname(file)
    filename = os.path.splitext(os.path.basename(file))[0]

    # Save the plot
    plt.savefig(os.path.join(filepath, filename + '.png'))

    # Clear the plot for the next iteration
    plt.clf()

# Define the directory path
directory_path = "//dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI/biopac/1080_wasabi/acq/physio02_sort"

# Recursively search for files with .acq extension
pattern = os.path.join(directory_path, '**/*.acq')
files = glob.glob(pattern, recursive=True)

# Get the SLURM array task ID
task_id = int(os.environ.get('SLURM_ARRAY_TASK_ID', '1'))

# Check if the task ID is within the valid range
if task_id <= len(files):
    # Get the file corresponding to the task ID
    file = files[task_id - 1]

    # Process the file
    process_file(file)
else:
    print(f"Invalid task ID: {task_id}")