#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
0a. Import Libraries
"""

from __future__ import absolute_import, division

import numpy as np  # whole numpy lib is available, prepend 'np.'
from numpy import (sin, cos, tan, log, log10, pi, average,
                   sqrt, std, deg2rad, rad2deg, linspace, asarray)
from numpy.random import random, randint, normal, shuffle
import os  # handy system and path functions
import sys  # to get file system encoding

from builtins import str
from builtins import range

import pandas as pd
import collections
try:
    from collections import OrderedDict
except ImportError:
    OrderedDict=dict

import random
from datetime import datetime

import glob
import re

# Set the options
pd.set_option('display.max_rows', None)       # None means show all rows
pd.set_option('display.max_columns', None)    # None means show all columns
pd.set_option('display.max_colwidth', None)   # None means show full width of columns
pd.set_option('display.width', None)          # None means auto-detect the display width


__author__ = "Michael Sun"
__version__ = "1.0.0"
__email__ = "msun@dartmouth.edu"
__status__ = "Production"


# For setting the heat-trial stimulation
def round_down(num, divisor):
    return num-(num%divisor)

# For setting the calibrated average heat
def round_to(n, precision):
    correction = 0.5 if n >= 0 else -0.5
    # check if n is nan before casting to int
    try:
        return int( n/precision+correction ) * precision
    except:
        return np.nan

def round_to_halfdegree(n):
    return round_to(n, 0.5)

from datetime import datetime

def calculate_age(born):
    b_date = datetime.strptime(born, '%m/%d/%Y')
    return (datetime.today() - b_date).days/365

def read_tsv(filename):

    global w
    data = filename.split('_')  #
    header = data[0] + ',' + data[1] + ',' + data[3][4:] + ',' + data[4] + ','
    f_proper = os.path.join(directory, filename)
    f = open(f_proper, "r")
    f.readline()  # gets rid of header
    temps = []
    end = ''
    for line in f:
        line = line.strip()
        line = line.split('\t')
        if line[-1][0].isnumeric() and line[1] not in ['Valence Rating:', 'Intensity Rating:', 'Comfort Rating:']:
            num = float(line[-1])
            if num > 30 and num not in temps:
                temps.append(num)
        elif line[1] in ['Valence Rating:', 'Intensity Rating:', 'Comfort Rating:']:
            end += line[1] + ',' + str(line[-1]) + ','
    w.write(header + str(min(temps)) + ',' + str(max(temps)) + ',' + end + '\n')
    f.close()

def genCalibrationSummaries(sub_dir):
    # This function should take in a subject directory and spit out two files:
    # genCalibrationSummaries(r'C:\Users\Admin\Documents\GitHub\canlab\WASABI_public\fMRI Tasks\N-Of-Many\WASABI bodyCalibration\data\sub-SID00XXXX\ses-01') =>
    # 1. sub-SID00XXXX_task-bodyCalibration.tsv
    # 2. sub-SID00XXXX_task-bodyCalibration_participants.tsv
    # These 2 files should be output in the same directory.
    
    # Generate *bodyCalibration.tsv
    
    # Assume sub_dir is already defined and points to the correct directory
    flist = glob.glob(sub_dir + r"\*_events.tsv")

    # Debugging: Print all filenames to ensure they are being found
    print("All filenames found:", flist)

    # Extract the run numbers and bodysites from the filenames
    runs = [int(re.search('run-(\d+)_', file).group(1)) for file in flist]
    bodysites = [re.search('acq-(.*?)_run', file).group(1) for file in flist]

    # Debugging: Print the extracted run numbers and bodysites
    print("Extracted run numbers:", runs)
    print("Extracted bodysites:", bodysites)

    # Sort runs and bodysites together
    sorted_runs_bodysites = sorted(zip(runs, bodysites))

    # Debugging: Print the sorted runs and bodysites
    print("Sorted runs and bodysites:", sorted_runs_bodysites)

    # Now extract the sorted runs and bodysites
    sorted_runs, sorted_bodysites = zip(*sorted_runs_bodysites)

    # Sort flist using the sorted order of runs
    sorted_flist = [file for run, file in sorted(zip(runs, flist))]

    # Debugging: Print the sorted flist
    print("Sorted file list:", sorted_flist)
    
    # Initialize DataFrame
    data=pd.read_csv(sorted_flist[0],sep='\t')          # read in the tsv
    
    # Function to shift and insert NaN
    def shift_and_insert_nan(df, indices):
        nan_row = pd.DataFrame(np.nan, index=[0], columns=df.columns)
        for index in sorted(indices, reverse=True):
            df = pd.concat([df.iloc[:index], nan_row, df.iloc[index:]]).reset_index(drop=True)
        return df   
    
    # Initialize lists to store IntensityRating and ToleranceRating
    intensity_ratings = []
    tolerance_ratings = []
    # Process each file
    for file in sorted_flist[0:]:
        # Read the file
        temp_data = pd.read_csv(file, sep='\t')

        # Extract IntensityRating and ToleranceRating
        intensity = temp_data[temp_data['condition'] == 'IntensityRating']['value'].tolist()
        tolerance = temp_data[temp_data['condition'] == 'ToleranceRating']['value'].tolist()

        # Remove last IntensityRating entry for each file, if not empty
        if intensity:
            intensity.pop()

        # Identify indices where PainBinary is -1
        pain_binary_indices = temp_data[temp_data['condition'] == 'PainBinary'].reset_index(drop=True)
        pain_binary_indices = pain_binary_indices.index[pain_binary_indices['value'] == -1].tolist()
    
        # Function to insert NaN at specific indices
        def insert_nan_at_indices(lst, indices):
            # Sort indices in ascending order
            for index in sorted(indices):
                # Insert NaN at the correct index
                lst.insert(index, np.nan)
            return lst

        # Apply function to intensity and tolerance
        intensity = insert_nan_at_indices(intensity, pain_binary_indices)
        tolerance = insert_nan_at_indices(tolerance, pain_binary_indices)

        # Append to the lists
        intensity_ratings.extend(intensity)
        tolerance_ratings.extend(tolerance)
        
        if file==sorted_flist[0]:
            data = temp_data
        else:
            data = pd.concat([data, temp_data])
        
    # Reset index of the final DataFrame
    data.reset_index(drop=True, inplace=True)

    date=np.unique(data['date'])[0]
    SID=np.unique(data['SID'])[0]
    age=None
    sex=np.unique(data['sex'])[0]
    handedness=np.unique(data['handedness'])[0]

    body_site= data['body_site'].dropna() # Gather every body_site
    # Create a temporary DataFrame for body_sites with their first occurrence indices
    repetition = body_site.to_frame(name='body_site').groupby('body_site').cumcount() + 1
    temperature= data['temperature'].dropna() # Gather every temperature
    pain= data.loc[data['condition'] == 'PainBinary', 'value']# Gather every condition=PainBinary
    # intensity= data.loc[data['condition'] == 'IntensityRating', 'value']# Gather every condition==IntensityRating
    # intensity=intensity.drop(intensity.index[7::8]) # Drop every 8th observation (i.e. every 8th IntensityRating)
    # tolerance= data.loc[data['condition'] == 'ToleranceRating', 'value'] # Gather every ToleranceRating
    intensity=intensity_ratings
    tolerance=tolerance_ratings
   
    bids_filename = sub_dir + os.sep + u'sub-SID%06d_task-%s.tsv' % (int(SID), 'bodyCalibration')
    bids_df = pd.DataFrame({
        'repetition': pd.Series(repetition).reset_index(drop=True),
        'body_site': pd.Series(body_site).reset_index(drop=True),
        'temperature': pd.Series(temperature).reset_index(drop=True),
        'pain': pd.Series(pain).reset_index(drop=True),
        'intensity': pd.Series(intensity).reset_index(drop=True),
        'tolerance': pd.Series(tolerance).reset_index(drop=True)
    })
    bids_df.to_csv(bids_filename, sep='\t', index=False)

    # Generate *bodyCalibration_participants.tsv
    averaged_data=[]
    averaged_filename = sub_dir + os.sep + u'sub-SID%06d_task-%s_participants.tsv' % (int(SID),'bodyCalibration')
    
    # Define the body sites you are interested in
    body_sites = [
        'Left Arm', 'Right Arm', 'Left Leg', 'Right Leg', 
        'Left Face', 'Right Face', 'Chest', 'Abdomen'
    ]
    
    # Initialize an empty list for the averaged data
    averaged_data = {
        'date': date,
        'DBIC_id': SID,
        # 'age': calculate_age(date),
        # 'dob': dob,  # dob seems to be the same as date here, which might be incorrect
        'sex': sex,
        'handedness': handedness,
        'calibration_order': sorted_bodysites  # This assumes bodysites is a pre-calculated list or value
    }
    
    # Loop over each body site and calculate the average temperature and intensity
    for site in body_sites:
        condition = (bids_df['body_site'] == site) & \
                    (bids_df['repetition'] != 1) & \
                    (bids_df['pain'] == 1) & \
                    (bids_df['tolerance'] == 1)
                    
        averaged_data[f'{site.replace(" ", "").lower()}_ht'] = round_to_halfdegree(bids_df.loc[condition]['temperature'].mean())
        averaged_data[f'{site.replace(" ", "").lower()}_i'] = bids_df.loc[condition]['intensity'].mean()

    # Convert the dictionary to a DataFrame
    averaged_df = pd.DataFrame([averaged_data])

    # Specify the column order if necessary
    column_order = [
        'date', 
        'DBIC_id', 
        # 'age', 
        # 'dob', 
        'sex', 
        'handedness', 
        'calibration_order'
    ] + [f'{site.replace(" ", "").lower()}_ht' for site in body_sites] + [f'{site.replace(" ", "").lower()}_i' for site in body_sites]

    averaged_df = averaged_df[column_order]
    
    # Save the participant summary
    averaged_filename = os.path.join(sub_dir, f'sub-SID{SID:06}_task-bodyCalibration_participants.tsv')
    averaged_df = pd.DataFrame([averaged_data])
    averaged_df.to_csv(averaged_filename, sep='\t', index=False)

# Step 1: You will want to run the above code first to load the function genCalibrationSummaries() into memory, before calling it below:
# Highlight all of the above, right click > Run in Interactive Window > Run Selection/Line in Interactive Window

# Should run something like this:
# Python cannot handle Windows filepaths without an 'r' prefix
# dir=r'C:\Users\Dartmouth\Documents\GitHub\canlab\WASABI_public\fMRI Tasks\N-Of-Many\WASABI bodyCalibration\data\sub-SID002743\ses-01'
dir=r'C:\Users\Michael\Documents\GitHub\canlab\WASABI_public\fMRI Tasks\N-Of-Many\WASABI bodyCalibration\data\sub-SID002990\ses-01'
# dir=r'C:\dbic_computer_path_to\WASABI_Public\fMRI Tasks\N-Of-Many\WASABI bodyCalibration\data\sub-SID003000\ses-01'
genCalibrationSummaries(dir)

# Step 2: Edit your path to dir with the desired subject ID, and the path on your local machine.
# Step 3: Highlight the above call to dir and genCalibrationSummaries(), right click > Run in Interactive Window > Run Selection/Line in Interactive Window

# Done