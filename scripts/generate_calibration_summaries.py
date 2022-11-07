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

from datetime import date

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


def genCalibrationSummaries(sub_dir, expInfo, expName, loc):
    write_location=loc
    w=open(write_location, 'a')

    os.chdir(sub_dir) #gets the path of the directory the python script is sitting in
    rootdir = os.getcwd()

    for rootdir, dirs, files in os.walk(rootdir): #collects all files and subdirectory in current directory
    for subdir in dirs: #runs on only subdirectory
        directory=os.path.join(rootdir, subdir) #gets path of current subdirectory
        for filename in os.listdir(directory): #gets all files in subdirectory and runs through them
            if filename[-4:len(filename)] != '.tsv': #if file is not a .tsv file, prints to console (for debugging)
                print(filename,': is not a run')
                continue
            read_tsv(filename)


    bids_filename = sub_dir + os.sep + u'sub-SID%06d_task-%s.tsv' % (int(expInfo['DBIC Number']), expName)
    bids_df=pd.DataFrame(pd.DataFrame(bodyCalibration_bids_total, columns = ['repetition', 'body_site', 'temperature', 'pain', 'intensity', 'tolerance']))

    averaged_data=[]
    averaged_filename = sub_dir + os.sep + u'sub-SID%06d_task-%s_participants.tsv' % (int(expInfo['DBIC Number']), expName)
    averaged_data.extend([expInfo['date'], expInfo['DBIC Number'], calculate_age(expInfo['dob (mm/dd/yyyy)']), expInfo['dob (mm/dd/yyyy)'], expInfo['sex'], expInfo['handedness'], bodySites,
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