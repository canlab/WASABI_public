#%%
import glob
import re
import pathlib
import sys 
sys.path.append("..")
from pathlib import Path 
import shutil
import os
import platform

from pkg_resources import resource_filename as pkgrf 

# %%
platform.system()
print(os.getcwd())
# cd to the write place
if platform.system() == 'Darwin':
    os.chdir("/dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI/1080_wasabi")
elif platform.system() == 'Windows':
    os.chdir(r"\\dartfs-hpc\rc\lab\C\CANlab\labdata\data\WASABI\1080_wasabi")
    # os.chdir("F:\\Dropbox (Dartmouth College)\\CANLab Projects\\WASABI\\Admin\\NDA_WASABI_NOM")
elif platform.system() == 'Linux':
    os.chdir("/dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI/1080_wasabi")

print(os.getcwd())
#%%
# returns string path to testdata
# TEST_DATA = pkgrf("cubids", "testdata")

# should give you the full path 
tmp_path = Path().resolve()
#print(tmp_path)

# dest path
data_root = tmp_path / "testdata"
data_root = tmp_path

# ensure path does not already exist in cwd
# if data_root.exists():
#     shutil.rmtree(str(data_root))

# # equivalent of command line "cp"
# cwd = shutil.copytree(TEST_DATA, str(data_root))
# %%
## FIELDMAPS AND INTENDEDFOR FIELDS:
# get a list of fieldmaps:

fmaps = pathlib.Path(data_root).rglob("*fmap/*.json")

fmaps = [x for x in fmaps]

fmaps[:10]

# %%
import json

def read_intendedfor(path):
    
    with open(str(path), 'r') as infile:
        data = json.load(infile)
        
    return data.get('IntendedFor')

#%%
# Test if it works for one file
read_intendedfor(fmaps[0])
# %%
mapping = {}

for fm in fmaps:
    
    intfor = read_intendedfor(fm)
    
    mapping[str(fm)] = intfor
# %%
all_files = [str(x) for x in pathlib.Path(data_root).rglob("*.nii*")]

for k, v in mapping.items():
    
    if not v:
        
        print("{}: This fieldmap is not intended for any files!".format(k))
        
        continue
        
    for fi in v:
        
        if any([fi in x for x in all_files]):
            
            print("{}: This fieldmap has a file".format(k))
            
        else:
            
            print("{}: The file this fieldmap is intended for doesn't exist".format(k))
# %%
import pandas as pd
df = pd.DataFrame(list(mapping.items()), columns=['Fmap', 'IntendedFor Files'])

#%%
# Loop through the keys and values in the dictionary and add them to the table_data list
table_data=[]
for key, value in mapping.items():
    # Use the explode() function to create a new row for each element of the list in the second column
    value_exploded = pd.Series(value).explode().tolist()
    for v in value_exploded:
        table_data.append([key, v])


#%%
# set max_rows and max_columns options
# Set the maximum column width to 200
pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_rows', None) 
pd.set_option('display.width', None)
print(pd.DataFrame(table_data, columns=['Fmap', 'IntendedFor Files']))

# %%
df=pd.DataFrame(table_data, columns=['Fmap', 'IntendedFor Files'])
df.to_csv('IntendedForList.csv', index=False)

print('Output written to IntendedForList.csv')


# %%
# Requires prettyprinter
# ! pip install prettyprinter

from prettyprinter import pformat
print(pformat(df))

# %%
