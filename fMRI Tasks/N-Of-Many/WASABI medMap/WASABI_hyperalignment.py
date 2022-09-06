#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This experiment was created using PsychoPy3 Experiment Builder (v2020.2.10),
    on January 28, 2021, at 23:04
If you publish work using this script the most relevant publication is:

    Peirce J, Gray JR, Simpson S, MacAskill M, Höchenberger R, Sogo H, Kastman E, Lindeløv JK. (2019) 
        PsychoPy2: Experiments in behavior made easy Behav Res 51: 195. 
        https://doi.org/10.3758/s13428-018-01193-y
        
This python script was extensively modified in order to work in the Dartmouth Brain Imaging Center environment reading in signals coming from a 
Siemens 3T fMRI scanner. Physiological data is acquired with a Biopac MP150 Physiological data acquisition device via LabJack U3.

Some measures have been taken to minimize experimental latency. PTB/Psychopy style is used to initialize all objects prior to screen flipping as much as possible.

Data is written in BIDS 1.4.1 format, as separate tab-separated-value (.tsv) files for each run per subject, (UTF-8 encoding). 
Following this format:
all data headers are in lower snake_case.

The paradigm will generate a files of name:
sub-XX_task-hyperalignment_events.tsv

headers:
'onset'	'duration'	'condition'	'biopac_channel'

0a. Import Libraries

"""

from __future__ import absolute_import, division

from psychopy import locale_setup
from psychopy import prefs
prefs.hardware['audioLib'] = ['PTB']
from psychopy import sound, gui, visual, core, data, event, logging, clock
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)

import numpy as np  # whole numpy lib is available, prepend 'np.'
from numpy import (sin, cos, tan, log, log10, pi, average,
                   sqrt, std, deg2rad, rad2deg, linspace, asarray)
from numpy.random import random, randint, normal, shuffle
import os  # handy system and path functions
import sys  # to get file system encoding

from psychopy.hardware import keyboard

from builtins import str
from builtins import range

import pandas as pd
import collections
try:
    from collections import OrderedDict
except ImportError:
    OrderedDict=dict

from WASABI_psychopy_utilities import *
from WASABI_config import *

__author__ = "Michael Sun"
__version__ = "2.0.0"
__email__ = "msun@dartmouth.edu"
__status__ = "Production"

"""
1. Experimental Parameters
"""
# Paths
# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)
main_dir = _thisDir
# video_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir, os.path.pardir, 'WASABI hyperalignment', 'stimuli', 'videos')
video_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stimuli', 'videos')


"""
2. Start Experimental Dialog Boxes
"""
# Upload participant file: Browse for file
# Store info about the experiment session
psychopyVersion = '2020.2.10'
expName = 'hyperalignment-movie'  # from the Builder filename that created this script

if debug == 1:
    expInfo = {
    'DBIC Number': '99',
    'first(1) or second(2) day': '1',
    'gender': 'm',
    'session': '1',
    'handedness': 'r', 
    'scanner': 'MS'
    }
else:
    expInfo = {
    'DBIC Number': '',
    'first(1) or second(2) day': '',
    'gender': '',
    'session': '',
    'handedness': '', 
    'scanner': ''
    }
    subjectInfoBox("Hyperalignment Scan", expInfo)

""" 
3. Setup the Window
fullscr = False for testing, True for running participants
"""

win=setupWindow()
# store frame rate of monitor if we can measure it
expInfo['frameRate'] = win.getActualFrameRate()
if expInfo['frameRate'] != None:
    frameDur = 1.0 / round(expInfo['frameRate'])
else:
    frameDur = 1.0 / 60.0  # could not measure, so guess

"""
4. Preload Movie
"""
# Preload Movie for Hyperalignment
# movie=preloadMovie(win, "inscapes-movie", os.path.join(video_dir,'01_Inscapes_NoScannerSound_h264.wmv'))

if expInfo['first(1) or second(2) day']=='1':
    movie=preloadMovie(win, "kungfury1", os.path.join(video_dir,'kungfury1.mp4'))
    movieCode=kungfury1
if expInfo['first(1) or second(2) day']=='2':
    movie=preloadMovie(win, "kungfury2", os.path.join(video_dir,'kungfury2.mp4'))
    movieCode=kungfury2

"""
5. Prepare files to write
"""
sub_dir = os.path.join(_thisDir, 'data', 'sub-SID%06d' % (int(expInfo['DBIC Number'])), 'ses-%02d' % (int(expInfo['session'])))
if not os.path.exists(sub_dir):
    os.makedirs(sub_dir)

hyperalignment_bids=pd.DataFrame()

"""
6. run the Hyperalignment Scan 
"""
fmriStart=confirmRunStart(win)
hyperalignment_bids=showMovie(win, movie, movie.name, movieCode)
"""
7. Save hyperalignment data into its own .TSV
""" 
hyperalignment_bids_data = pd.DataFrame([hyperalignment_bids])
hyperalignment_bids_filename = sub_dir + os.sep + u'sub-SID%06d_ses-%02d_task-%s_acq-%s_events.tsv' % (int(expInfo['DBIC Number']), int(expInfo['session']), expName, 'hyperalignment'+expInfo['first(1) or second(2) day'])
hyperalignment_bids_data.to_csv(hyperalignment_bids_filename, sep="\t")

"""
8. Wrap Up
""" 
endScan(win)
win.close()  # close the window
core.quit()

"""
End of Experiment
"""