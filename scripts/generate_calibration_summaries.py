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


__author__ = "Michael Sun"
__version__ = "1.0.4"
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
    
    flist=glob.glob(sub_dir+r"\*_events.tsv")                               # Collect a list of all the event files
    run = [int(f) for f in flist]

    # Extracting data from a list of filenames
    bodysites=[]
    runs=[]
    for file in flist:
        runs.append(int(re.search('run-(.*)_events.tsv', file).group(1)))
        bodysites.append(re.search('acq-(.*)_run', file).group(1))
    # reorder runs by bodysite
    bodysites=[x for _, x in sorted(zip(runs, bodysites))]
    flist=[x for _, x in sorted(zip(runs, flist))]

    data=pd.read_csv(flist[0],sep='\t')                                     # read in the tsv
    for file in flist[1:]:                                                     # For each file
        data=pd.concat([data,pd.read_csv(file,sep='\t')])                # read in the tsv

    date=np.unique(data['date'])[0]
    SID=np.unique(data['SID'])[0]
    age=None
    sex=np.unique(data['sex'])[0]
    handedness=np.unique(data['handedness'])[0]

    
    repetition=         # Gather every condition==PainBinary
    body_site=          # Gather every body_site
    temperature=        # Gather every temperature
    pain=               # Gather every condition=PainBinary
    intensity=          # Gather every condition==IntensityRating
    tolerance=          # Gather every ToleranceRating

    bids_filename = sub_dir + os.sep + u'sub-SID%06d_task-%s.tsv' % (int(data['SID']), 'bodyCalibration')
    bids_df=pd.DataFrame(pd.DataFrame(bodyCalibration_bids_total, columns = ['repetition', 'body_site', 'temperature', 'pain', 'intensity', 'tolerance']))




    
    write_location=loc
    w=open(write_location, 'a')

    os.chdir(sub_dir) #gets the path of the directory the python script is sitting in
    rootdir = os.getcwd()

    # for rootdir, dirs, files in os.walk(rootdir): #collects all files and subdirectory in current directory
    #     for subdir in dirs: #runs on only subdirectory
    #         directory=os.path.join(rootdir, subdir) #gets path of current subdirectory
    #         for filename in os.listdir(directory): #gets all files in subdirectory and runs through them
    #             if filename[-4:len(filename)] != '.tsv': #if file is not a .tsv file, prints to console (for debugging)
    #                 print(filename,': is not a run')
    #                 continue
    #             read_tsv(filename)



    averaged_data=[]
    averaged_filename = sub_dir + os.sep + u'sub-SID%06d_task-%s_participants.tsv' % (int(expInfo['DBIC Number']), expName)
    averaged_data.extend([bids_df['date'], bids_df['DBIC Number'], calculate_age(bids_df['date']), bids_df['date'], bids_df['sex'], bids_df['handedness'], bids_df['body_site'],
                        round_to_halfdegree(bids_df.loc[(bids_df['body_site']=='Left Arm') & (bids_df['repetition']!=1) & (bids_df['pain']==1) & (bids_df['tolerance']==1)]['temperature'].mean()), 
                        round_to_halfdegree(bids_df.loc[(bids_df['body_site']=='Right Arm') & (bids_df['repetition']!=1) & (bids_df['pain']==1) & (bids_df['tolerance']==1)]['temperature'].mean()), 
                        round_to_halfdegree(bids_df.loc[(bids_df['body_site']=='Left Leg') & (bids_df['repetition']!=1) & (bids_df['pain']==1) & (bids_df['tolerance']==1)]['temperature'].mean()), 
                        round_to_halfdegree(bids_df.loc[(bids_df['body_site']=='Right Leg') & (bids_df['repetition']!=1) & (bids_df['pain']==1) & (bids_df['tolerance']==1)]['temperature'].mean()), 
                        round_to_halfdegree(bids_df.loc[(bids_df['body_site']=='Left Face') & (bids_df['repetition']!=1) & (bids_df['pain']==1) & (bids_df['tolerance']==1)]['temperature'].mean()), 
                        round_to_halfdegree(bids_df.loc[(bids_df['body_site']=='Right Face') & (bids_df['repetition']!=1) & (bids_df['pain']==1) & (bids_df['tolerance']==1)]['temperature'].mean()), 
                        round_to_halfdegree(bids_df.loc[(bids_df['body_site']=='Chest') & (bids_df['repetition']!=1) & (bids_df['pain']==1) & (bids_df['tolerance']==1)]['temperature'].mean()), 
                        round_to_halfdegree(bids_df.loc[(bids_df['body_site']=='Abdomen') & (bids_df['repetition']!=1) & (bids_df['pain']==1) & (bids_df['tolerance']==1)]['temperature'].mean()),
                        bids_df.loc[(bids_df['body_site']=='Left Arm') & (bids_df['repetition']!=1) & (bids_df['pain']==1) & (bids_df['tolerance']==1)]['intensity'].mean(), bids_df.loc[(bids_df['body_site']=='Right Arm') & (bids_df['repetition']!=1) & (bids_df['pain']==1) & (bids_df['tolerance']==1)]['intensity'].mean(), 
                        bids_df.loc[(bids_df['body_site']=='Left Leg') & (bids_df['repetition']!=1) & (bids_df['pain']==1) & (bids_df['tolerance']==1)]['intensity'].mean(), bids_df.loc[(bids_df['body_site']=='Right Leg') & (bids_df['repetition']!=1) & (bids_df['pain']==1) & (bids_df['tolerance']==1)]['intensity'].mean(), 
                        bids_df.loc[(bids_df['body_site']=='Left Face') & (bids_df['repetition']!=1) & (bids_df['pain']==1) & (bids_df['tolerance']==1)]['intensity'].mean(), bids_df.loc[(bids_df['body_site']=='Right Face') & (bids_df['repetition']!=1) & (bids_df['pain']==1) & (bids_df['tolerance']==1)]['intensity'].mean(), 
                        bids_df.loc[(bids_df['body_site']=='Chest') & (bids_df['repetition']!=1) & (bids_df['pain']==1) & (bids_df['tolerance']==1)]['intensity'].mean(), bids_df.loc[(bids_df['body_site']=='Abdomen') & (bids_df['repetition']!=1) & (bids_df['pain']==1) & (bids_df['tolerance']==1)]['intensity'].mean()])

    averaged_df = pd.DataFrame(data = [averaged_data], columns = ['date','DBIC_id','age','dob','sex','handedness','calibration_order',
                                                        'leftarm_ht','rightarm_ht','leftleg_ht','rightleg_ht','leftface_ht','rightface_ht','chest_ht','abdomen_ht',
                                                        'leftarm_i','rightarm_i','leftleg_i','rightleg_i','leftface_i','rightface_i','chest_i','abdomen_i'])

    w.close()


# Should run something like this:
# Python cannot handle Windows filepaths 
dir=r'C:\Users\Admin\Documents\GitHub\canlab\WASABI_public\fMRI Tasks\N-Of-Many\WASABI bodyCalibration\data\sub-SID002292\ses-01'
genCalibrationSummaries(dir)
# Done