#%%
import subprocess

# Define the srun command
# srun_command = ['srun', '-n', '4', 'your-command']  # Replace 'your-command' with the actual command to be executed
srun_command = ['srun', '--account=dbic', '--nodes=1', '--ntasks-per-node=1', '--mem=64G', '--pty', '-c', '4', '-t', '5-8:00:00', 'bash']
# Run the srun command
result = subprocess.run(srun_command, capture_output=True, text=True)

# Print the command output
print(result.stdout)


# ! pip install bioread
import neurokit2 as nk
import matplotlib.pyplot as plt
import os
import platform
import glob

#%%
platform.system()
print(os.getcwd())
# cd to the write place
if platform.system() == 'Darwin':
    os.chdir("//dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI/biopac/1080_wasabi/acq/physio02_sort")
elif platform.system() == 'Windows':
    os.chdir("//dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI/biopac/1080_wasabi/acq/physio02_sort")
    # os.chdir("F:\\Dropbox (Dartmouth College)\\CANLab Projects\\WASABI\\Admin\\NDA_WASABI_NOM")
elif platform.system() == 'Linux':
    os.chdir("//dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI/biopac/1080_wasabi/acq/physio02_sort")

print(os.getcwd())

#%%
# Recursively search for files with .acq extension
pattern = os.path.join(os.getcwd(), '**/*.acq')
files = glob.glob(pattern, recursive=True)

# Print the list of files
for file in files:
    print(file)

#%%

# Plot every acq file and save it in their respective folder.
for file in files:
    main_df, samplingrate = nk.read_acqknowledge(file)
    main_df[['MRI TR', 'Skin Conductance (EDA) - EDA100C-MRI', 'PPG']].plot()
    filepath=os.path.dirname(file)
    filename=os.path.splitext(os.path.basename(file))[0]
    plt.savefig(os.path.join(filepath,(filename+'.png')))
# %%
import neurokit2 as nk
import matplotlib.pyplot as plt
import os
import glob
# %%
# Define system-specific paths
paths = {
    'Darwin': "//dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI/biopac/1080_wasabi/acq/physio02_sort",
    'Windows': "//dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI/biopac/1080_wasabi/acq/physio02_sort",
    'Linux': "//dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI/biopac/1080_wasabi/acq/physio02_sort",
    'posix': "//dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI/biopac/1080_wasabi/acq/physio02_sort"
}
# Get the current system name
current_system = os.name
# %%
# Change current working directory based on the system
os.chdir(paths.get(os.name))

# Recursively search for files with .acq extension
pattern = os.path.join(os.getcwd(), '**/*.acq')
files = glob.glob(pattern, recursive=True)

# Print the list of files
print('\n'.join(files))
# %%
# Plot every acq file and save it in their respective folder.
for file in files:
    main_df, samplingrate = nk.read_acqknowledge(file)
    main_df[['MRI TR', 'Skin Conductance (EDA) - EDA100C-MRI', 'PPG']].plot()
    filepath = os.path.dirname(file)
    filename = os.path.splitext(os.path.basename(file))[0]
    plt.savefig(os.path.join(filepath, filename + '.png'))
    plt.clf()  # Clear the plot for the next iteration
    
# %%
from multiprocessing import Pool

def process_file(file):
    main_df, samplingrate = nk.read_acqknowledge(file)
    main_df[['MRI TR', 'Skin Conductance (EDA) - EDA100C-MRI', 'PPG']].plot()
    filepath = os.path.dirname(file)
    filename = os.path.splitext(os.path.basename(file))[0]
    plt.savefig(os.path.join(filepath, filename + '.png'))
    plt.clf()  # Clear the plot for the next iteration

# Rest of the code...

# Create a multiprocessing pool
pool = Pool(processes=4)

# Process files in parallel
pool.map(process_file, files)

# Close the pool to release resources
pool.close()
pool.join()
# %%
