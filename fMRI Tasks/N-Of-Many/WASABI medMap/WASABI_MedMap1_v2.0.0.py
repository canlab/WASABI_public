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

This paradigm is run as 2 parts of a MedMap paradigm for 2 body sites: Left Face and Right Leg. 

One day will consist of 8 total runs of either Left Face or Right Leg interchanging between each run. Each run will feature 6 heat trials at 49 degrees C. 

As a consequence, in one day, correct running of these paradigms will generate 8x files of the names:
sub-SIDXXXXX_ses-XX_task-medmap_acq-[bodySite]_run-X_events.tsv

Each file will consist of the following headers:
onset   duration    intensity   bodySite    temperature condition   pretrial-jitter

Troubleshooting Tips:
If you get window-related errors, make sure to downgrade pyglet to 1.4.1:
pip uninstall pyglet
pip install pyglet==1.4.1

0a. Import Libraries
"""

from __future__ import absolute_import, division

from psychopy import locale_setup
from psychopy import prefs
prefs.hardware['audioLib'] = ['PTB'] # Set a preferred audio library to PsychToolBox (best), so psychopy doesn't yell at you.
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

import random
from datetime import datetime

from WASABI_psychopy_utilities import *


##### Master Controller Paradigm #####

## Try this
# import WASABI_hyperalignment
# import WASABI_pinelLocalizer
# import WASABI_distractmap

if __name__ == '__main__':
    arg1 = u"Hey "
    arg2 = u"Steve."

    result1 = hyperalignment.run(arg1, arg2)

    arg3 = u" How're "
    arg4 = u"you?"

    result2 = pinellocalizer.run(result1, arg1, arg2)
    print(result2)

## This is a less good solution
# os.chdir('experiment2')
# execfile('blah.py')

#####

__author__ = "Michael Sun"
__version__ = "2.0.0"
__email__ = "msun@dartmouth.edu"
__status__ = "Development"

"""  
0b. Beta-Testing Togglers
Set to 1 during development, 0 during production
"""
debug = 0
autorespond = 0
# Device togglers
biopac_exists = 0
thermode_exists = 0


"""
0c. Autoresponding objects
"""
class simKeys:
    '''
    an object to simulate key presses    
    keyList: a list of keys/ to watch
    name: randomly selected from keyList
    rtRange: [min RT, max RT] where min and max RT are sepecified in ms
        
    '''
    def __init__(self, keyList, rtRange):
        self.name=np.random.choice(keyList)
        self.rt = np.random.choice(np.linspace(rtRange[0], rtRange[1])/1000)

# pick an RT
thisRT=randint(0,5)
thisSimKey=simKeys(keyList=['space'], 
    rtRange=[200,1000])


"""
0d. Helper functions
"""

def rescale(self, width=0, height=0, operation='', units=None, log=True):
    '''
    Function for rescaling the size of an object such as your ImageStim.
    '''
    (old_width,old_height) = self.size
    if all([height,width]):
        pass
    elif height:
        ratio = height/old_height
        width = old_width * ratio
    elif width:
        ratio = width/old_width
        height = old_height * ratio
    self.setSize([width,height],operation,units,log)
 
visual.ImageStim.rescale = rescale


def round_down(num, divisor):
    '''
    Function for rounding a number down.
    '''
    return num-(num%divisor)

# For setting the calibrated average heat
def round_to(n, precision):
    '''
    Function for rounding a number to the nearest precision point e.g., .5.
    '''
    correction = 0.5 if n >= 0 else -0.5
    # check if n is nan before casting to int
    try:
        return int( n/precision+correction ) * precision
    except:
        return np.nan

def round_to_halfdegree(n):
    '''
    Wrapper function for rounding a temperature to its closest half-degree.
    '''
    return round_to(n, 0.5)

"""
0e. Prepare Devices: Biopac Psychophysiological Acquisition
"""  
# Biopac parameters _________________________________________________
# Relevant Biopac commands: 
#     To send a Biopac marker code to Acqknowledge, replace the FIO number with a value between 0-255(dec), or an 8-bit word(bin) 
#     For instance, the following code would send a value of 15 by setting the first 4 bits to “1": biopac.getFeedback(u3.PortStateWrite(State = [15, 0, 0]))
#     Toggling each of the FIO 8 channels directly: biopac.setFIOState(fioNum = 0:7, state=1)
#     Another command that may work: biopac.setData(byte)

task_ID=2
task_start=7

instructions=15
leftface_heat=17
rightleg_heat=22

instruction_code=198

pain_binary=42
intensity_rating=43

valence_rating=39
trialIntensity_rating=40
comfort_rating=41

avoid_rating = 200
relax_rating = 201
taskattention_rating = 202
boredom_rating = 203
alertness_rating = 204
posthx_rating = 205
negthx_rating = 206
self_rating = 207
other_rating = 208
imagery_rating = 209
present_rating = 210
intensity_rating=211


# Hyperalignment movie
hyperalignment_intro = 212
inscapes=214

# Pinel Localizer

between_run_msg=45

end_task = 197

if biopac_exists == 1:
    # Initialize LabJack U3 Device, which is connected to the Biopac MP150 psychophysiological amplifier data acquisition device
    # This involves importing the labjack U3 Parallelport to USB library
    # U3 Troubleshooting:
    # Check to see if u3 was imported correctly with: help('u3')
    # Check to see if u3 is calibrated correctly with: cal_data = biopac.getCalibrationData()
    # Check to see the data at the FIO, EIO, and CIO ports: biopac.getFeedback(u3.PortStateWrite(State = [0, 0, 0]))
    try:
        from psychopy.hardware.labjacks import U3
        # from labjack import u3
    except ImportError:
        import u3
    # Function defining setData to use the FIOports (address 6000)
    def biopacSetData(self, byte, endian='big', address=6000): 
        if endian=='big':
            byteStr = '{0:08b}'.format(byte)[-1::-1]
        else:
            byteStr = '{0:08b}'.format(byte)
        [self.writeRegister(address+pin, int(entry)) for (pin, entry) in enumerate(byteStr)]
    biopac = U3()
    biopac.setData = biopacSetData
    # Set all FIO bits to digital output and set to low (i.e. “0")
    # The list in square brackets represent what’s desired for the FIO, EIO, CIO ports. We will only change the FIO port's state.
    biopac.configIO(FIOAnalog=0, EIOAnalog=0)
    for FIONUM in range(8):
        biopac.setFIOState(fioNum = FIONUM, state=0)
    # Set all channels to 0 before the experiment begins.
    biopac.setData(biopac, 0)

# Medoc TSA2 parameters ______________________________________________
# Initialize the Medoc TSA2 thermal stimulation delivery device
    # Medoc Troubleshooting:
    # To find the computer IP address, check with MMS Arbel's External Control (or Windows ipconfig alternatively)
    # Communication port is always 20121
    # Relevant Medoc commands:
    #     Prepare a program: sendCommand('select_tp', config.START_CALIBRATION)
    #     Poll the Machine to know if it's ready for another command: poll_for_change("[RUNNING/IDLE]", poll_interval=0.5, poll_max = -1 (unlimited), verbose=False, server_lag=1)
    #           Select "RUNNING" if you are using a "Manual Trigger" and a SELECT_TP has already been sent. Select "IDLE" if you are using an "Auto" Trigger design
    #     Trigger a prepared program: sendCommand('trigger')
    #     Pause a program: sendCommand('pause')
    #     Stop a program: sendCommand('stop')
if thermode_exists == 1:
    # Import medocControl library, python library custom written for Medoc with pyMedoc pollforchange functionality. 
    # Make sure medocControl.py is in the same directory 
    from medocControl import *

"""
1. Experimental Parameters
Clocks, folder paths, etc.
"""
# Clocks
globalClock = core.Clock()  # to track the time since experiment started
routineTimer = core.CountdownTimer()  # to track time remaining of each (non-slip) routine 
# Paths
# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)
main_dir = _thisDir
stimuli_dir = main_dir + os.sep + "stimuli"
video_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir, os.path.pardir, 'WASABI hyperalignment', 'stimuli', 'videos')

# Brings up the Calibration/Data folder to load the appropriate calibration data right away.
calibration_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir, 'WASABI bodyCalibration', 'data')

"""
2. Start Experimental Dialog Boxes
"""
psychopyVersion = '2020.2.10'
if debug == 1:
    expInfo = {
    'DBIC Number': '99',
    'first(1) or second(2) day': 1,
    'gender': 'm',
    'session': '99',
    'handedness': 'r', 
    'scanner': 'MS',
    'run': '1',
    'body sites': ''
    }
else:
    expInfo = {
    'DBIC Number': '',
    'first(1) or second(2) day': '', 
    'gender': '',
    'session': '',
    'handedness': '', 
    'scanner': '',
    'run': '',
    'body sites': '' 
    }

# Load the subject's calibration file and ensure that it is valid
# Upload participant file: Browse for file
# Store info about the experiment session
if debug!=1:
    dlg1 = gui.fileOpenDlg(tryFilePath=calibration_dir, tryFileName="", prompt="Select participant calibration file (*_task-bodyCalibration_participants.tsv)", allowed="Calibration files (*.tsv)")
    if dlg1!=None:
        if "_task-bodyCalibration_participants.tsv" in dlg1[0]:
            # Read in participant info csv and convert to a python dictionary
            a = pd.read_csv(dlg1[0], delimiter='\t', index_col=0, header=0, squeeze=True)
            if a.shape == (1,23):
                participant_settingsHeat = {}
                p_info = [dict(zip(a.iloc[i].index.values, a.iloc[i].values)) for i in range(len(a))][0]
                expInfo['DBIC Number'] = p_info['DBIC_id']
                expInfo['gender'] = p_info['gender']
                expInfo['handedness'] = p_info['handedness']
                # Heat Settings
                participant_settingsHeat['Left Face'] = p_info['leftface_ht']
                participant_settingsHeat['Right Face'] = p_info['rightface_ht']
                participant_settingsHeat['Left Arm'] = p_info['leftarm_ht']
                participant_settingsHeat['Right Arm'] = p_info['rightarm_ht']
                participant_settingsHeat['Left Leg'] = p_info['leftleg_ht']
                participant_settingsHeat['Right Leg'] = p_info['rightleg_ht']
                participant_settingsHeat['Chest'] = p_info['chest_ht']
                participant_settingsHeat['Abdomen'] = p_info['abdomen_ht']
                ses_num = str(1)

                expInfo2 = {
                'session': ses_num,
                'first(1) or second(2) day': '',
                'scanner': '',
                'run': 1, # If re-inserting participant midday
                'body sites': '' # If inputting a list of body sites, make sure to delimit them with ', ' with the trailing space.
                }

                # dlg2 = gui.DlgFromDict(title="WASABI MedMap", dictionary=expInfo2, sortKeys=False) 
                expInfo2=subjectInfoBox("WASABI MedMap Scan", expInfo2)
                expInfo['session'] = expInfo2['session']
                expInfo['scanner'] = expInfo2['scanner']
                # if dlg2.OK == False:
                #     core.quit()  # user pressed cancel
            else:
                errorDlg1 = gui.Dlg(title="Error - invalid file")
                errorDlg1.addText("Selected file is not a valid calibration file. Data is incorrectly formatted. (Wrong dimensions)")
                errorDlg1.show()
                dlg1=None
        else:
            errorDlg2 = gui.Dlg(title="Error - invalid file")
            errorDlg2.addText("Selected file is not a valid calibration file. Name is not formatted sub-SIDXXXXXX_task-bodyCalibration_participant.tsv")
            errorDlg2.show()
            dlg1=None
    if dlg1==None:
        ## This is used if an appropriate calibration is not selected. Generate a list of temperature choices.
        ## Limit the entries of this to hot temperatures (32-49 degrees in half-degree-steps)
        participant_settingsHeat = {
            'Left Face': [44,44.5,45,45.5,46,46.5,47,47.5,48,48.5],    # Calibrated Temp for left face
            'Right Face': [44,44.5,45,45.5,46,46.5,47,47.5,48,48.5],   # Calibrated Temp for right face
            'Left Arm': [44,44.5,45,45.5,46,46.5,47,47.5,48,48.5],     # Calibrated Temp for left arm
            'Right Arm': [44,44.5,45,45.5,46,46.5,47,47.5,48,48.5],    # Calibrated Temp for right arm
            'Left Leg': [44,44.5,45,45.5,46,46.5,47,47.5,48,48.5],     # Calibrated Temp for left leg
            'Right Leg': [44,44.5,45,45.5,46,46.5,47,47.5,48,48.5],    # Calibrated Temp for right leg
            'Chest': [44,44.5,45,45.5,46,46.5,47,47.5,48,48.5],        # Calibrated Temp for chest
            'Abdomen': [44,44.5,45,45.5,46,46.5,47,47.5,48,48.5]       # Calibrated Temp for abdomen
            }

        # dlg2 = gui.DlgFromDict(title="WASABI MedMap Scan", dictionary=expInfo, sortKeys=False)
        # if dlg2.OK == False:
        #     core.quit()  # user pressed cancel
        subjectInfoBox("WASABI MedMap Scan", expInfo)
        pphDlg = gui.DlgFromDict(participant_settingsHeat, 
                                title='Participant Heat Parameters')
        if pphDlg.OK == False:
            core.quit()
else:
    participant_settingsHeat = {
        'Left Face': 48.5,
        'Right Face': 48.5,
        'Left Arm': 48.5,
        'Right Arm': 48.5,
        'Left Leg': 48.5,
        'Right Leg': 48.5,
        'Chest': 48.5,
        'Abdomen': 48.5
    }

if expInfo['first(1) or second(2) day'] ==1:
    expName = 'MedMap1-conditioning'
elif expInfo['first(1) or second(2) day']==2:
    expName = 'MedMap2-test'  

# expInfo['date'] = data.getDateStr()  # add a simple timestamp
expInfo['psychopyVersion'] = psychopyVersion
expInfo['expName'] = expName

"""
3. Configure the Stimuli Arrays
"""
if expInfo['body sites']=="":
    bodySites1 = ['Right Leg', 'Left Face', 'Right Leg', 'Left Face', 'Right Leg', 'Left Face', 'Right Leg', 'Left Face']
    bodySites2 = ['Left Face', 'Right Leg', 'Left Face', 'Right Leg', 'Left Face', 'Right Leg', 'Left Face', 'Right Leg'] 

    # bodySites1 = ['Left Face', 'Left Face', 'Left Face', 'Left Face']

    if int(expInfo['DBIC Number'])%2==0:
        bodySites=bodySites1
    else:
        bodySites=bodySites2
else:
    bodySites=list(expInfo['body sites'].split(", "))

# If bodysites and run order need to be manually set for the participant, in a pinch, uncomment below and edit:
# bodySites = ["Left Leg"]

expInfo['body_site_order'] = str(bodySites)
expInfo['expName'] = expName


# Hyperalignment
movieOrder = [OrderedDict([('runSeq',
            [
            # OrderedDict([('moviefile', os.path.join(video_dir,'kungfury.mp4'))]),
            OrderedDict([('moviefile', os.path.join(video_dir,'01_Inscapes_NoScannerSound_h264.wmv'))])
            ] 
        )])
        ]
movie_code = [ # kungfury, 
                inscapes]

""" 
4. Setup the Window
fullscr = False for testing, True for running participants
"""
# if debug == 1: 
#     win = visual.Window(
#             size=[1280, 720], fullscr=False, 
#             screen=0,   # Change this to the appropriate display 
#             winType='pyglet', allowGUI=True, allowStencil=False,
#             monitor='testMonitor', color=[-1.000,-1.000,-1.000], colorSpace='rgb',
#             blendMode='avg', useFBO=True, 
#             units='height')
# else: 
#     win = visual.Window(
#             size=[1920, 1080], fullscr=True, 
#             screen=-1,   # Change this to the appropriate fMRI projector 
#             winType='pyglet', allowGUI=True, allowStencil=False,
#             monitor='testMonitor', color=[-1.000,-1.000,-1.000], colorSpace='rgb',
#             blendMode='avg', useFBO=True, 
#             units='height')
# # store frame rate of monitor if we can measure it
# expInfo['frameRate'] = win.getActualFrameRate()
# if expInfo['frameRate'] != None:
#     frameDur = 1.0 / round(expInfo['frameRate'])
# else:
#     frameDur = 1.0 / 60.0  # could not measure, so guess

# win.mouseVisible = False # Make the mouse invisible for the remainder of the experiment

win=setupWindow()

"""
5. Prepare Experimental Dictionaries for Body-Site Cues and Medoc Temperature Programs
"""
## Check gender for Chest cue
Chest_imgPath = os.sep.join([stimuli_dir,"cue","ChestF.png"])
if expInfo['gender'] in {"M", "m", "Male", "male"}:
    Chest_imgPath = os.sep.join([stimuli_dir,"cue","ChestM.png"])
elif expInfo['gender'] in {"F", "f", "Female", "female"}:
    Chest_imgPath = os.sep.join([stimuli_dir,"cue","ChestF.png"])
bodysite_word2img = {"Left Face": os.sep.join([stimuli_dir,"cue","LeftFace.png"]), 
                          "Right Face": os.sep.join([stimuli_dir,"cue","RightFace.png"]), 
                          "Left Arm": os.sep.join([stimuli_dir,"cue","LeftArm.png"]), 
                          "Right Arm": os.sep.join([stimuli_dir,"cue","RightArm.png"]), 
                          "Left Leg": os.sep.join([stimuli_dir,"cue","LeftLeg.png"]), 
                          "Right Leg": os.sep.join([stimuli_dir,"cue","RightLeg.png"]), 
                          "Chest": Chest_imgPath,
                          "Abdomen": os.sep.join([stimuli_dir,"cue","Abdomen.png"]) 
                        }
bodysite_word2heatcode = {"Left Face": leftface_heat, 
                        "Right Leg": rightleg_heat
                        }

# Set up a dictionary for all the configured Medoc programs for the main thermode
thermode1_temp2program = {}
with open("thermode1_programs.txt") as f:
    for line in f:
       (key, val) = line.split()
       thermode1_temp2program[float(key)] = int(val)

"""
5. Prepare files to write
"""
sub_dir = os.path.join(_thisDir, 'data', 'sub-SID%06d' % (int(expInfo['DBIC Number'])), 'ses-%02d' % (int(expInfo['session'])))
if not os.path.exists(sub_dir):
    os.makedirs(sub_dir)

# psypy_medmap_filename = os.path.join(sub_dir, 'SID%06d_ses-%02d_task-%s_%s' % (int(expInfo['DBIC Number']), int(expInfo['session']), expName, expInfo['date'])
# psypy_hyperalignment_filename = os.path.join(sub_dir, 'sub-SID%06d_ses-%02d_task-%s_%s' % (int(expInfo['DBIC Number']), int(expInfo['session']), "hyperalignment-movie", expInfo['date'])
# psypy_pinellocalizer_filename = os.path.join(sub_dir, 'sub-SID%06d_ses-%02d_task-%s_%s' % (int(expInfo['DBIC Number']), int(expInfo['session']), "pinelLocalizer", expInfo['date'])
# psypy_distractMap_filename = os.path.join(sub_dir, 'sub-SID%06d_ses-%02d_task-%s_%s' % (int(expInfo['DBIC Number']), int(expInfo['session']), "distractMap", expInfo['date'])

# An ExperimentHandler isn't essential but helps with data saving
thisExp = data.ExperimentHandler(name=expName, version='',
    extraInfo=expInfo, runtimeInfo=None,
    # originPath='C:\\Users\\Michael\\Downloads\\counterbalance-multiple-tasks-demo.py',
    savePickle=True, saveWideText=True,
    dataFileName=psypy_medmap_filename)
# save a log file for detail verbose info
logFile = logging.LogFile(psypy_filename+'.log', level=logging.EXP)
logging.console.setLevel(logging.WARNING)  # this outputs to the screen, not a file

endExpNow = False  # flag for 'escape' or other condition => quit the exp
frameTolerance = 0.001  # how close to onset before 'same' frame

# Create python lists to later concatenate or convert into pandas dataframes
medmap_bids_trial = []
medmap_bids = []

# hyperalign_bids_trial = []
# hyperalign_bids = []

## Others?

"""
5. Initialize Trial-level Components
"""
# General Instructional Text
start_msg = 'Please wait. \nThe scan will begin shortly. \n Experimenter press [s] to continue.'
s_text='[s]-press confirmed.'
in_between_run_msg = 'Thank you.\n Please wait for the next scan to start \n Experimenter press [e] to continue.'
end_msg = 'Please wait for instructions from the experimenter'

## Instruction Parameters
ExperienceInstruction = "Experience the following sensations as they come."
InstructionText = ExperienceInstruction
instructioncode = instruction_code
InstructionCondition = "Instruction"

# Rating question text
painText="Was that painful?"
trialIntensityText="How intense was the heat stimulation?"

totalTrials = 6 # Figure out how many trials would be equated to 5 minutes
stimtrialTime = 25 # This becomes very unreliable with the use of poll_for_change().

ratingTime = 5 # Rating Time limit in seconds during the inter-stimulus-interval

if debug == 1:
    stimtrialTime = 1 # This becomes very unreliable with the use of poll_for_change().
    totalTrials = 1
# create a default keyboard (e.g. to check for escape)
defaultKeyboard = keyboard.Keyboard()

# Pre-rating audio ding to wake participants up.
rating_sound=mySound=sound.Sound('B', octave=5, stereo=1, secs=.5)  
## When you want to play the sound, run this line of code:
# rating_sound.play()

# # Initialize components for Routine "BodySiteInstruction"
# BodySiteInstructionClock = core.Clock()
# BodySiteInstructionRead = keyboard.Keyboard()
# BodySiteInstructionText = visual.TextStim(win, name='BodySiteInstructionText', 
#     text="Experimenter: Please place thermodes on the designated body-site.",
#     font = 'Arial',
#     pos=(0, -.2), height=0.05, wrapWidth=1.6, ori=0, 
#     color='white', colorSpace='rgb', opacity=1, 
#     languageStyle='LTR',
#     depth=0.0, 
#     anchorHoriz='center')
# BodySiteImg = visual.ImageStim(
#     win=win,
#     name='BodySiteImg', 
#     mask=None,
#     ori=0, pos=(0, 0), size=(.40,.40),
#     color=[1,1,1], colorSpace='rgb', opacity=1,
#     flipHoriz=False, flipVert=False,
#     texRes=512, interpolate=True, depth=0.0)

# # Initialize components for Routine "Instructions"
# InstructionsClock = core.Clock()
# Instructions = visual.TextStim(win=win, name='Instructions',
#     text='Welcome to the scan\nPlease read the following instructions \nvery carefully.\n\n\n\nExperimenter press [Space] to continue.',
#     font='Arial', wrapWidth=1.75,
#     pos=(0, 0.0), units='height', height=0.05, 
#     color='white', colorSpace='rgb', opacity=1)

# # Initialize components for Routine "Fixation"
# FixationClock = core.Clock()
# fixation = visual.TextStim(win=win, name='fixation',
#     text='+',
#     font='Arial',
#     pos=(0, 0), height=0.05, wrapWidth=None, ori=0, 
#     color='white', colorSpace='rgb', opacity=1, 
#     languageStyle='LTR',
#     depth=-2.0)

# # Initialize components for each Rating
# TIME_INTERVAL = 0.005   # Speed at which slider ratings udpate
# ratingScaleWidth=1.5
# ratingScaleHeight=.4
# sliderMin = -.75
# sliderMax = .75
# bipolar_verts = [(sliderMin, .2),    # left point
#                         (sliderMax, .2),    # right point
#                         (0, -.2)]           # bottom-point
# unipolar_verts = [(sliderMin, .2), # left point
#             (sliderMax, .2),     # right point
#             (sliderMin, -.2)]   # bottom-point, # bottom-point

# ## These Ratings are taken after every heat stimulation
# painText="Was that painful?"
# intensityText="How intense was the heat stimulation?"

# # Initialize components for Routine "PainBinary"
# PainBinaryClock = core.Clock()
# PainBinary = visual.Rect(win, height=ratingScaleHeight, width=0, pos= [0, 0], fillColor='red', lineColor='black')
# PainMouse = event.Mouse(win=win)
# PainMouse.mouseClock = core.Clock()
# PainAnchors = visual.ImageStim(
#     win=win,
#     image= os.sep.join([stimuli_dir,"ratingscale","YesNo.png"]),
#     name='PainQuestion', 
#     mask=None,
#     ori=0, pos=(0, 0), size=(1, .25),
#     color=[1,1,1], colorSpace='rgb', opacity=1,
#     flipHoriz=False, flipVert=False,
#     texRes=512, interpolate=True, depth=0.0)
# PainPrompt = visual.TextStim(win, name='PainPrompt', 
#     text=painText,
#     font = 'Arial',
#     pos=(0, 0.3), height=0.05, wrapWidth=None, ori=0, 
#     color='white', colorSpace='rgb', opacity=1, 
#     languageStyle='LTR',
#     depth=0.0,
#     anchorHoriz='center')


IntensityText = 'HOW INTENSE was the WORST heat you experienced?'
# # Initialize components for Routine "IntensityRating"
# IntensityRatingClock = core.Clock()
# IntensityMouse = event.Mouse(win=win)
# IntensityMouse.mouseClock = core.Clock()
# IntensityRating = visual.Rect(win, height=ratingScaleHeight, width=abs(sliderMin), pos= [sliderMin/2, -.1], fillColor='red', lineColor='black')
# IntensityBlackTriangle = visual.ShapeStim(
#     win, 
#     vertices=[(sliderMin, .2), # left point
#             (sliderMax, .2),     # right point
#             (sliderMin, -.2)],   # bottom-point, 
#     fillColor='black', lineColor='black')
# IntensityAnchors = visual.ImageStim(
#     win=win,
#     image= os.sep.join([stimuli_dir,"ratingscale","intensityScale.png"]),
#     name='intensityAnchors', 
#     mask=None,
#     ori=0, pos=(0, -0.09), size=(1.5, .4),
#     color=[1,1,1], colorSpace='rgb', opacity=1,
#     flipHoriz=False, flipVert=False,
#     texRes=512, interpolate=True, depth=0.0)
# IntensityPrompt = visual.TextStim(win, name='IntensityPrompt', 
#     text=intensityText,
#     font = 'Arial',
#     pos=(0, 0.3), height=0.05, wrapWidth=None, ori=0, 
#     color='white', colorSpace='rgb', opacity=1, 
#     languageStyle='LTR',
#     depth=0.0,
#     anchorHoriz='center')

# ## The following ratings are in the post run section

# # Initialize components for Routine "ComfortRating"
ComfortText = "How comfortable do you feel right now?" # (Bipolar)
# ComfortRatingClock = core.Clock()
# ComfortMouse = event.Mouse(win=win, visible=False)
# ComfortMouse.mouseClock = core.Clock()
# ComfortRating = visual.Rect(win, height=ratingScaleHeight, width=abs(sliderMin), pos= [sliderMin/2, -.1], fillColor='red', lineColor='black')
# ComfortBlackTriangle = visual.ShapeStim(
#     win, 
#     vertices=bipolar_verts,
#     fillColor='black', lineColor='black')
# ComfortAnchors = visual.ImageStim(
#     win=win,
#     image= os.sep.join([stimuli_dir,"ratingscale","ComfortScale.png"]),
#     name='ComfortAnchors', 
#     mask=None,
#     ori=0, pos=(0, -0.09), size=(1.5, .4),
#     color=[1,1,1], colorSpace='rgb', opacity=1,
#     flipHoriz=False, flipVert=False,
#     texRes=512, interpolate=True, depth=0.0)
# ComfortPrompt = visual.TextStim(win, name='ComfortPrompt', 
#     text=ComfortText,
#     font = 'Arial',
#     pos=(0, 0.3), height=0.05, wrapWidth=None, ori=0, 
#     color='white', colorSpace='rgb', opacity=1, 
#     languageStyle='LTR',
#     depth=0.0,
#     anchorHoriz='center')

# # Initialize components for Routine "ValenceRating"
ValenceText = "HOW UNPLEASANT was the WORST heat you experienced?"  # 0 -- Most Unpleasant (Unipolar)
# ValenceRatingClock = core.Clock()
# ValenceMouse = event.Mouse(win=win, visible=False)
# ValenceMouse.mouseClock = core.Clock()
# ValenceRating = visual.Rect(win, height=ratingScaleHeight, width=abs(sliderMin), pos= [sliderMin/2, -.1], fillColor='red', lineColor='black')
# ValenceBlackTriangle = visual.ShapeStim(
#     win, 
#     vertices=unipolar_verts,
#     fillColor='black', lineColor='black')
# ValenceAnchors = visual.ImageStim(
#     win=win,
#     image= os.sep.join([stimuli_dir,"ratingscale","postvalenceScale.png"]),
#     name='ValenceAnchors', 
#     mask=None,
#     ori=0, pos=(0, -0.09), size=(1.5, .4),
#     color=[1,1,1], colorSpace='rgb', opacity=1,
#     flipHoriz=False, flipVert=False,
#     texRes=512, interpolate=True, depth=0.0)
# ValencePrompt = visual.TextStim(win, name='ValencePrompt', 
#     text=ValenceText,
#     font = 'Arial',
#     pos=(0, 0.3), height=0.05, wrapWidth=None, ori=0, 
#     color='white', colorSpace='rgb', opacity=1, 
#     languageStyle='LTR',
#     depth=0.0,
#     anchorHoriz='center')

# # Initialize components for Routine "AvoidRating"
AvoidText = "Please rate HOW MUCH you want to avoid this experience in the future?" # Not at all -- Most(Unipolar)
# AvoidRatingClock = core.Clock()
# AvoidMouse = event.Mouse(win=win, visible=False)
# AvoidMouse.mouseClock = core.Clock()
# AvoidRating = visual.Rect(win, height=ratingScaleHeight, width=abs(sliderMin), pos= [sliderMin/2, -.1], fillColor='red', lineColor='black')
# AvoidBlackTriangle = visual.ShapeStim(
#     win, 
#     vertices=unipolar_verts,
#     fillColor='black', lineColor='black')
# AvoidAnchors = visual.ImageStim(
#     win=win,
#     image= os.sep.join([stimuli_dir,"ratingscale","AvoidScale.png"]),
#     name='AvoidAnchors', 
#     mask=None,
#     ori=0, pos=(0, -0.09), size=(1.5, .4),
#     color=[1,1,1], colorSpace='rgb', opacity=1,
#     flipHoriz=False, flipVert=False,
#     texRes=512, interpolate=True, depth=0.0)
# AvoidPrompt = visual.TextStim(win, name='AvoidPrompt', 
#     text=AvoidText,
#     font = 'Arial',
#     pos=(0, 0.3), height=0.05, wrapWidth=None, ori=0, 
#     color='white', colorSpace='rgb', opacity=1, 
#     languageStyle='LTR',
#     depth=0.0,
#     anchorHoriz='center')

# # Initialize components for Routine "RelaxRating"
RelaxText = "How relaxed are you feeling right now?" # Least relaxed -- Most Relaxed (Unipolar)
# RelaxRatingClock = core.Clock()
# RelaxMouse = event.Mouse(win=win, visible=False)
# RelaxMouse.mouseClock = core.Clock()
# RelaxRating = visual.Rect(win, height=ratingScaleHeight, width=abs(sliderMin), pos= [sliderMin/2, -.1], fillColor='red', lineColor='black')
# RelaxBlackTriangle = visual.ShapeStim(
#     win, 
#     vertices=unipolar_verts,
#     fillColor='black', lineColor='black')
# RelaxAnchors = visual.ImageStim(
#     win=win,
#     image= os.sep.join([stimuli_dir,"ratingscale","RelaxScale.png"]),
#     name='RelaxAnchors', 
#     mask=None,
#     ori=0, pos=(0, -0.09), size=(1.5, .4),
#     color=[1,1,1], colorSpace='rgb', opacity=1,
#     flipHoriz=False, flipVert=False,
#     texRes=512, interpolate=True, depth=0.0)
# RelaxPrompt = visual.TextStim(win, name='RelaxPrompt', 
#     text=RelaxText,
#     font = 'Arial',
#     pos=(0, 0.3), height=0.05, wrapWidth=None, ori=0, 
#     color='white', colorSpace='rgb', opacity=1, 
#     languageStyle='LTR',
#     depth=0.0,
#     anchorHoriz='center')

# # Initialize components for Routine "TaskAttentionRating"
TaskAttentionText = "During the last scan, how well could you keep your attention on the task?" # Not at all -- Best (Unipolar)
# TaskAttentionRatingClock = core.Clock()
# TaskAttentionMouse = event.Mouse(win=win, visible=False)
# TaskAttentionMouse.mouseClock = core.Clock()
# TaskAttentionRating = visual.Rect(win, height=ratingScaleHeight, width=abs(sliderMin), pos= [sliderMin/2, -.1], fillColor='red', lineColor='black')
# TaskAttentionBlackTriangle = visual.ShapeStim(
#     win, 
#     vertices=unipolar_verts,
#     fillColor='black', lineColor='black')
# TaskAttentionAnchors = visual.ImageStim(
#     win=win,
#     image= os.sep.join([stimuli_dir,"ratingscale","TaskAttentionScale.png"]),
#     name='TaskAttentionAnchors', 
#     mask=None,
#     ori=0, pos=(0, -0.09), size=(1.5, .4),
#     color=[1,1,1], colorSpace='rgb', opacity=1,
#     flipHoriz=False, flipVert=False,
#     texRes=512, interpolate=True, depth=0.0)
# TaskAttentionPrompt = visual.TextStim(win, name='TaskAttentionPrompt', 
#     text=TaskAttentionText,
#     font = 'Arial',
#     pos=(0, 0.3), height=0.05, wrapWidth=None, ori=0, 
#     color='white', colorSpace='rgb', opacity=1, 
#     languageStyle='LTR',
#     depth=0.0,
#     anchorHoriz='center')

# # Initialize components for Routine "BoredomRating"
BoredomText = "During the last scan, how bored were you?" # Not bored at all -- Extremely Bored (Unipolar)
# BoredomRatingClock = core.Clock()
# BoredomMouse = event.Mouse(win=win, visible=False)
# BoredomMouse.mouseClock = core.Clock()
# BoredomRating = visual.Rect(win, height=ratingScaleHeight, width=abs(sliderMin), pos= [sliderMin/2, -.1], fillColor='red', lineColor='black')
# BoredomBlackTriangle = visual.ShapeStim(
#     win, 
#     vertices=unipolar_verts,
#     fillColor='black', lineColor='black')
# BoredomAnchors = visual.ImageStim(
#     win=win,
#     image= os.sep.join([stimuli_dir,"ratingscale","BoredomScale.png"]),
#     name='BoredomAnchors', 
#     mask=None,
#     ori=0, pos=(0, -0.09), size=(1.5, .4),
#     color=[1,1,1], colorSpace='rgb', opacity=1,
#     flipHoriz=False, flipVert=False,
#     texRes=512, interpolate=True, depth=0.0)
# BoredomPrompt = visual.TextStim(win, name='BoredomPrompt', 
#     text=BoredomText,
#     font = 'Arial',
#     pos=(0, 0.3), height=0.05, wrapWidth=None, ori=0, 
#     color='white', colorSpace='rgb', opacity=1, 
#     languageStyle='LTR',
#     depth=0.0,
#     anchorHoriz='center')

# # Initialize components for Routine "AlertnessRating"
AlertnessText = "During the last scan how sleepy vs. alert were you?" # Extremely Sleepy - Neutral - Extremely Alert (Bipolar)
# AlertnessRatingClock = core.Clock()
# AlertnessMouse = event.Mouse(win=win, visible=False)
# AlertnessMouse.mouseClock = core.Clock()
# AlertnessRating = visual.Rect(win, height=ratingScaleHeight, width=abs(sliderMin), pos= [sliderMin/2, -.1], fillColor='red', lineColor='black')
# AlertnessBlackTriangle = visual.ShapeStim(
#     win, 
#     vertices=bipolar_verts,
#     fillColor='black', lineColor='black')
# AlertnessAnchors = visual.ImageStim(
#     win=win,
#     image= os.sep.join([stimuli_dir,"ratingscale","AlertnessScale.png"]),
#     name='AlertnessAnchors', 
#     mask=None,
#     ori=0, pos=(0, -0.09), size=(1.5, .4),
#     color=[1,1,1], colorSpace='rgb', opacity=1,
#     flipHoriz=False, flipVert=False,
#     texRes=512, interpolate=True, depth=0.0)
# AlertnessPrompt = visual.TextStim(win, name='AlertnessPrompt', 
#     text=AlertnessText,
#     font = 'Arial',
#     pos=(0, 0.3), height=0.05, wrapWidth=None, ori=0, 
#     color='white', colorSpace='rgb', opacity=1, 
#     languageStyle='LTR',
#     depth=0.0,
#     anchorHoriz='center')

# # Initialize components for Routine "PosThxRating"
PosThxText = "The thoughts I experienced during the last scan were POSITIVE" # Strongly disagree - Neither - Strongly Agree (Bipolar)
# PosThxRatingClock = core.Clock()
# PosThxMouse = event.Mouse(win=win, visible=False)
# PosThxMouse.mouseClock = core.Clock()
# PosThxRating = visual.Rect(win, height=ratingScaleHeight, width=abs(sliderMin), pos= [sliderMin/2, -.1], fillColor='red', lineColor='black')
# PosThxBlackTriangle = visual.ShapeStim(
#     win, 
#     vertices=bipolar_verts,
#     fillColor='black', lineColor='black')
# PosThxAnchors = visual.ImageStim(
#     win=win,
#     image= os.sep.join([stimuli_dir,"ratingscale","PosThxScale.png"]),
#     name='PosThxAnchors', 
#     mask=None,
#     ori=0, pos=(0, -0.09), size=(1.5, .4),
#     color=[1,1,1], colorSpace='rgb', opacity=1,
#     flipHoriz=False, flipVert=False,
#     texRes=512, interpolate=True, depth=0.0)
# PosThxPrompt = visual.TextStim(win, name='PosThxPrompt', 
#     text=PosThxText,
#     font = 'Arial',
#     pos=(0, 0.3), height=0.05, wrapWidth=None, ori=0, 
#     color='white', colorSpace='rgb', opacity=1, 
#     languageStyle='LTR',
#     depth=0.0,
#     anchorHoriz='center')

# # Initialize components for Routine "NegThxRating"
NegThxText = "The thoughts I experienced during the last scan were NEGATIVE" # Strongly disagree - Neither - Strongly agree (bipolar)
# NegThxRatingClock = core.Clock()
# NegThxMouse = event.Mouse(win=win, visible=False)
# NegThxMouse.mouseClock = core.Clock()
# NegThxRating = visual.Rect(win, height=ratingScaleHeight, width=abs(sliderMin), pos= [sliderMin/2, -.1], fillColor='red', lineColor='black')
# NegThxBlackTriangle = visual.ShapeStim(
#     win, 
#     vertices=bipolar_verts,
#     fillColor='black', lineColor='black')
# NegThxAnchors = visual.ImageStim(
#     win=win,
#     image= os.sep.join([stimuli_dir,"ratingscale","NegThxScale.png"]),
#     name='NegThxAnchors', 
#     mask=None,
#     ori=0, pos=(0, -0.09), size=(1.5, .4),
#     color=[1,1,1], colorSpace='rgb', opacity=1,
#     flipHoriz=False, flipVert=False,
#     texRes=512, interpolate=True, depth=0.0)
# NegThxPrompt = visual.TextStim(win, name='NegThxPrompt', 
#     text=NegThxText,
#     font = 'Arial',
#     pos=(0, 0.3), height=0.05, wrapWidth=None, ori=0, 
#     color='white', colorSpace='rgb', opacity=1, 
#     languageStyle='LTR',
#     depth=0.0,
#     anchorHoriz='center')

# # Initialize components for Routine "SelfRating"
SelfText = "The thoughts I experienced during the last scan were related to myself" # Strongly disagree -- Neither -- Strongly Agree (Bipolar)
# SelfRatingClock = core.Clock()
# SelfMouse = event.Mouse(win=win, visible=False)
# SelfMouse.mouseClock = core.Clock()
# SelfRating = visual.Rect(win, height=ratingScaleHeight, width=abs(sliderMin), pos= [sliderMin/2, -.1], fillColor='red', lineColor='black')
# SelfBlackTriangle = visual.ShapeStim(
#     win, 
#     vertices=bipolar_verts,
#     fillColor='black', lineColor='black')
# SelfAnchors = visual.ImageStim(
#     win=win,
#     image= os.sep.join([stimuli_dir,"ratingscale","SelfScale.png"]),
#     name='SelfAnchors', 
#     mask=None,
#     ori=0, pos=(0, -0.09), size=(1.5, .4),
#     color=[1,1,1], colorSpace='rgb', opacity=1,
#     flipHoriz=False, flipVert=False,
#     texRes=512, interpolate=True, depth=0.0)
# SelfPrompt = visual.TextStim(win, name='SelfPrompt', 
#     text=SelfText,
#     font = 'Arial',
#     pos=(0, 0.3), height=0.05, wrapWidth=None, ori=0, 
#     color='white', colorSpace='rgb', opacity=1, 
#     languageStyle='LTR',
#     depth=0.0,
#     anchorHoriz='center')

# # Initialize components for Routine "OtherRating"
OtherText = "The thoughts I experienced during the last scan concerned other people." # Strongly disagree - Neither - Strongly agree (Bipolar)
# OtherRatingClock = core.Clock()
# OtherMouse = event.Mouse(win=win, visible=False)
# OtherMouse.mouseClock = core.Clock()
# OtherRating = visual.Rect(win, height=ratingScaleHeight, width=abs(sliderMin), pos= [sliderMin/2, -.1], fillColor='red', lineColor='black')
# OtherBlackTriangle = visual.ShapeStim(
#     win, 
#     vertices=bipolar_verts,
#     fillColor='black', lineColor='black')
# OtherAnchors = visual.ImageStim(
#     win=win,
#     image= os.sep.join([stimuli_dir,"ratingscale","OtherScale.png"]),
#     name='OtherAnchors', 
#     mask=None,
#     ori=0, pos=(0, -0.09), size=(1.5, .4),
#     color=[1,1,1], colorSpace='rgb', opacity=1,
#     flipHoriz=False, flipVert=False,
#     texRes=512, interpolate=True, depth=0.0)
# OtherPrompt = visual.TextStim(win, name='OtherPrompt', 
#     text=OtherText,
#     font = 'Arial',
#     pos=(0, 0.3), height=0.05, wrapWidth=None, ori=0, 
#     color='white', colorSpace='rgb', opacity=1, 
#     languageStyle='LTR',
#     depth=0.0,
#     anchorHoriz='center')

# # Initialize components for Routine "ImageryRating"
ImageryText = "The thoughts I experienced during the last scan were experienced with clear and vivid mental imagery" # Strongly disagree - Neither - Strongly agree (bipolar)
# ImageryRatingClock = core.Clock()
# ImageryMouse = event.Mouse(win=win, visible=False)
# ImageryMouse.mouseClock = core.Clock()
# ImageryRating = visual.Rect(win, height=ratingScaleHeight, width=abs(sliderMin), pos= [sliderMin/2, -.1], fillColor='red', lineColor='black')
# ImageryBlackTriangle = visual.ShapeStim(
#     win, 
#     vertices=bipolar_verts,
#     fillColor='black', lineColor='black')
# ImageryAnchors = visual.ImageStim(
#     win=win,
#     image= os.sep.join([stimuli_dir,"ratingscale","ImageryScale.png"]),
#     name='ImageryAnchors', 
#     mask=None,
#     ori=0, pos=(0, -0.09), size=(1.5, .4),
#     color=[1,1,1], colorSpace='rgb', opacity=1,
#     flipHoriz=False, flipVert=False,
#     texRes=512, interpolate=True, depth=0.0)
# ImageryPrompt = visual.TextStim(win, name='ImageryPrompt', 
#     text=ImageryText,
#     font = 'Arial',
#     pos=(0, 0.3), height=0.05, wrapWidth=None, ori=0, 
#     color='white', colorSpace='rgb', opacity=1, 
#     languageStyle='LTR',
#     depth=0.0,
#     anchorHoriz='center')

# # Initialize components for Routine "PresentRating"
PresentText = "The thoughts I experienced during the last scan pertained to the immediate PRESENT (the here and now)" # Strongly disagree - Neither - Strongly agree (bipolar)
# PresentRatingClock = core.Clock()
# PresentMouse = event.Mouse(win=win, visible=False)
# PresentMouse.mouseClock = core.Clock()
# PresentRating = visual.Rect(win, height=ratingScaleHeight, width=abs(sliderMin), pos= [sliderMin/2, -.1], fillColor='red', lineColor='black')
# PresentBlackTriangle = visual.ShapeStim(
#     win, 
#     vertices=bipolar_verts,
#     fillColor='black', lineColor='black')
# PresentAnchors = visual.ImageStim(
#     win=win,
#     image= os.sep.join([stimuli_dir,"ratingscale","PresentScale.png"]),
#     name='PresentAnchors', 
#     mask=None,
#     ori=0, pos=(0, -0.09), size=(1.5, .4),
#     color=[1,1,1], colorSpace='rgb', opacity=1,
#     flipHoriz=False, flipVert=False,
#     texRes=512, interpolate=True, depth=0.0)
# PresentPrompt = visual.TextStim(win, name='PresentPrompt', 
#     text=PresentText,
#     font = 'Arial',
#     pos=(0, 0.3), height=0.05, wrapWidth=None, ori=0, 
#     color='white', colorSpace='rgb', opacity=1, 
#     languageStyle='LTR',
#     depth=0.0,
#     anchorHoriz='center')

# Create some handy timers
globalClock = core.Clock()  # to track the time since experiment started
routineTimer = core.CountdownTimer()  # to track time remaining of each (non-slip) routine 

if biopac_exists:
    biopac.setData(biopac, 0)
    biopac.setData(biopac, task_ID) # Start demarcation of the T1 task in Biopac Acqknowledge

win.mouseVisible = False

"""
6. Welcome Instructions
"""
# Instructions.draw()
# win.flip()
# continueRoutine=True
# while continueRoutine == True:
#     if 'space' in event.getKeys(keyList = 'space'):
#         continueRoutine = False

## Replace above with:
showText("Instructions", InstructionText)


# if expInfo['first(1) or second(2) half']==1:
#     runhalf=range(len(bodySites)-2)
# else:
#     runhalf=range(len(bodySites)-2, len(bodySites))

# for runs in runhalf:

if expInfo['run']>1:
    runRange=range(expInfo['run']-1, 8)
else:
    runRange=range(len(bodySites))

for runs in runRange:
    # ratingTime = 5 # Intensity Rating Time limit in seconds during the inter-trial-interval
    # # Reset intensity scale parameters:
    # intensityText = "How intense was that overall?" # (Unipolar)
    # IntensityAnchors = visual.ImageStim(
    #     win=win,
    #     image= os.sep.join([stimuli_dir,"ratingscale","intensityScale.png"]),
    #     name='intensityAnchors', 
    #     mask=None,
    #     ori=0, pos=(0, -0.09), size=(1.5, .4),
    #     color=[1,1,1], colorSpace='rgb', opacity=1,
    #     flipHoriz=False, flipVert=False,
    #     texRes=512, interpolate=True, depth=0.0)
    """
    7. Body-Site Instructions: Instruct the Experimenter on the Body Sites to attach thermodes to at the beginning of each run 
    """
    # # ------Prepare to start Routine "BodySiteInstruction"-------
    # routineTimer.reset()

    # continueRoutine = True
    # # update component parameters for each repeat
    # BodySiteInstructionRead.keys = []
    # BodySiteInstructionRead.rt = []
    # _BodySiteInstructionRead_allKeys = []
    # # Update instructions and cues based on current run's body-sites:
    # if runs == 0 or runs == 1 or runs==6 or runs==7:
    #     BodySiteInstructionText.text="Experimenter: \nPlease place the thermode on the: \n" + bodySites[runs].lower() + "\n\n Prepare the site for stimulation"
    # else:
    #     BodySiteInstructionText.text="Experimenter: \nPlease place the thermode on the: \n" + bodySites[runs].lower() + "\n\n Apply the Lidoderm analgesic cream"
    # # keep track of which components have finished
    # BodySiteInstructionComponents = [BodySiteInstructionText, BodySiteImg, BodySiteInstructionRead]

    # for thisComponent in BodySiteInstructionComponents:
    #     thisComponent.tStart = None
    #     thisComponent.tStop = None
    #     thisComponent.tStartRefresh = None
    #     thisComponent.tStopRefresh = None
    #     if hasattr(thisComponent, 'status'):
    #         thisComponent.status = NOT_STARTED
    # # reset timers
    # t = 0
    # _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    # BodySiteInstructionClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    # frameN = -1

    # # -------Run Routine "BodySiteInstruction"-------
    # while continueRoutine:
    #     # get current time
    #     t = BodySiteInstructionClock.getTime()
    #     tThisFlip = win.getFutureFlipTime(clock=BodySiteInstructionClock)
    #     tThisFlipGlobal = win.getFutureFlipTime(clock=None)
    #     frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    #     # update/draw components on each frame
        
    #     # *BodySiteInstructionText* updates
    #     if BodySiteInstructionText.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         BodySiteInstructionText.frameNStart = frameN  # exact frame index
    #         BodySiteInstructionText.tStart = t  # local t and not account for scr refresh
    #         BodySiteInstructionText.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(BodySiteInstructionText, 'tStartRefresh')  # time at next scr refresh
    #         BodySiteInstructionText.setAutoDraw(True)

    #     # *BodySiteImg* updates
    #     if BodySiteImg.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
    #         BodySiteImg.image = bodysite_word2img[bodySites[runs]]
    #         BodySiteImg.pos = (0, .2)
    #         # keep track of start time/frame for later
    #         BodySiteImg.frameNStart = frameN  # exact frame index
    #         BodySiteImg.tStart = t  # local t and not account for scr refresh
    #         BodySiteImg.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(BodySiteImg, 'tStartRefresh')  # time at next scr refresh
    #         BodySiteImg.setAutoDraw(True)
        
    #     # *BodySiteInstructionRead* updates
    #     waitOnFlip = False
    #     if BodySiteInstructionRead.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         BodySiteInstructionRead.frameNStart = frameN  # exact frame index
    #         BodySiteInstructionRead.tStart = t  # local t and not account for scr refresh
    #         BodySiteInstructionRead.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(BodySiteInstructionRead, 'tStartRefresh')  # time at next scr refresh
    #         BodySiteInstructionRead.status = STARTED
    #         # keyboard checking is just starting
    #         waitOnFlip = True
    #         win.callOnFlip(print, "Cueing Off All Biopac Channels")            
    #         win.callOnFlip(print, "Showing BodySite Instructions")
    #         win.callOnFlip(print, "Cueing Biopac Channel: " + str(instructions))
    #         if biopac_exists == 1:
    #             win.callOnFlip(biopac.setData, biopac, 0)
    #             win.callOnFlip(biopac.setData, biopac, instructions)
    #         win.callOnFlip(BodySiteInstructionRead.clock.reset)  # t=0 on next screen flip
    #         win.callOnFlip(BodySiteInstructionRead.clearEvents, eventType='keyboard')  # clear events on next screen flip
    #     if BodySiteInstructionRead.status == STARTED and not waitOnFlip:
    #         theseKeys = BodySiteInstructionRead.getKeys(keyList=['space'], waitRelease=False)
    #         _BodySiteInstructionRead_allKeys.extend(theseKeys)
    #         if len(_BodySiteInstructionRead_allKeys):
    #             BodySiteInstructionRead.keys = _BodySiteInstructionRead_allKeys[-1].name  # just the last key pressed
    #             BodySiteInstructionRead.rt = _BodySiteInstructionRead_allKeys[-1].rt
    #             # a response ends the routine
    #             continueRoutine = False
        
    #     # Autoresponder
    #     if t >= thisSimKey.rt and autorespond == 1:
    #         _BodySiteInstructionRead_allKeys.extend([thisSimKey]) 

    #     # check for quit (typically the Esc key)
    #     if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
    #         core.quit()
        
    #     # check if all components have finished
    #     if not continueRoutine:  # a component has requested a forced-end of Routine
    #         break
    #     continueRoutine = False  # will revert to True if at least one component still running
    #     for thisComponent in BodySiteInstructionComponents:
    #         if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
    #             continueRoutine = True
    #             break  # at least one component has not yet finished
        
    #     # refresh the screen
    #     if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
    #         win.flip()

    # # -------Ending Routine "BodySiteInstruction"-------
    # print("CueOff Channel: " + str(instructions))
    # if biopac_exists == 1:
    #     biopac.setData(biopac, 0)
    # for thisComponent in BodySiteInstructionComponents:
    #     if hasattr(thisComponent, "setAutoDraw"):
    #         thisComponent.setAutoDraw(False)
    # thisExp.addData('BodySiteInstructionText.started', BodySiteInstructionText.tStartRefresh)
    # thisExp.addData('BodySiteImg.started', BodySiteImg.tStartRefresh)
    # thisExp.addData('BodySiteImg.stopped', BodySiteImg.tStopRefresh)
    # # check responses
    # if BodySiteInstructionRead.keys in ['', [], None]:  # No response was made
    #     BodySiteInstructionRead.keys = None
    # thisExp.addData('BodySiteInstructionRead.keys',BodySiteInstructionRead.keys)
    # if BodySiteInstructionRead.keys != None:  # we had a response
    #     thisExp.addData('BodySiteInstructionRead.rt', BodySiteInstructionRead.rt)
    # thisExp.addData('BodySiteInstructionRead.started', BodySiteInstructionRead.tStartRefresh)
    # thisExp.addData('BodySiteInstructionRead.stopped', BodySiteInstructionRead.tStopRefresh)
    # # the Routine "BodySiteInstruction" was not non-slip safe, so reset the non-slip timer
    # routineTimer.reset()

   
    # Update instructions and cues based on current run's body-sites:
    if runs == 0 or runs == 1 or runs==6 or runs==7:
        bodysiteInstruction="Experimenter: \nPlease place the thermode on the: \n" + bodySites[runs].lower() + "\n\n Prepare the site for stimulation"
    else:
        bodysiteInstruction="Experimenter: \nPlease place the thermode on the: \n" + bodySites[runs].lower() + "\n\n Apply the Lidoderm analgesic cream"
    showTextAndImg("Bodysite Instruction", bodysiteInstruction, imgname=bodySites[runs], imgPath=bodysite_word2img[bodySites[runs]], biopacCode=instructions)

    ## Conditioning parameters; Ideally this should be read from the participanst file 
    if runs==0 or runs==1:
        temperature = participant_settingsHeat[bodySites[runs]]
        thermodeCommand=thermode1_temp2program[temperature]
        ConditionName="Control"
        # Highest tolerable temperature
    if runs==2 or runs==3:
        temperature = 44
        thermodeCommand=thermode1_temp2program[temperature]
        ConditionName="Placebo"
        # Warm and not hot temperature
    if runs==4 or runs==5 or runs==6 or runs==7:
        temperature=round_to_halfdegree(participant_settingsHeat[bodySites[runs]]-((participant_settingsHeat[bodySites[runs]]-44)/2))
        thermodeCommand=thermode1_temp2program[temperature] # midway between max and 44 warm
        if runs==4 or runs==5:
            ConditionName="Placebo"
        if runs==6 or runs==7:
            ConditionName="Control"

    ## If only 4 Runs:
    # if runs==0:
    #     thermodeCommand=135 # 49 degrees
    #     temperature=49
    # if runs==1:
    #     thermodeCommand=125 # 44 degrees
    #     temperature=44
    # if runs==2:
    #     thermodeCommand=125 # 44 degrees
    #     temperature=44
    # if runs==3:
    #     thermodeCommand=131 # 47 degrees
    #     temperature=49

    """
    8. Start Scanner
    """
    # start = visual.TextStim(win, text=start_msg, height=.05, color=win.rgb + 0.5)
    # start.draw()  # Automatically draw every frame
    # win.flip()
    # fmriStart = globalClock.getTime()   # Start the clock
    # if autorespond != 1:   
    #     TR = 0.46
        
    #     continueRoutine = True
    #     event.clearEvents()
    #     while continueRoutine == True:
    #         if 's' in event.getKeys(keyList = 's'):         # experimenter start key - safe key before fMRI trigger
    #             s_confirm = visual.TextStim(win, text=s_text, height =.05, color="green", pos=(0.0, -.3))
    #             start.draw()
    #             s_confirm.draw()
    #             win.flip()
    #             event.clearEvents()
    #             while continueRoutine == True:
    #                 if '5' in event.getKeys(keyList = '5'): # fMRI trigger
    #                     fmriStart = globalClock.getTime()   # Start the clock
    #                     timer = core.CountdownTimer()   # Wait 6 TRs, Dummy Scans
    #                     timer.add(TR*6)
    #                     while timer.getTime() > 0:
    #                         continue
    #                     continueRoutine = False

    # Replace above with the following code:
    fmriStart=confirmRunStart()

    """
    9. Set Trial parameters
    """
    jitter2 = None  # Reset Jitter2

    bodySiteData = bodySites[runs]
    # temperature = participant_settingsHeat[bodySites[runs]]
    BiopacChannel = bodysite_word2heatcode[bodySites[runs]]
    routineTimer.reset()

    """
    10. Start Trial Loop
    """
    for r in range(totalTrials): # 16 repetitions
        """
        11. Show the Instructions prior to the First Trial
        """
        if r == 0:      # First trial
            Instructions.setText(InstructionText)
            Instructions.draw()
            if biopac_exists:
                biopac.setData(biopac, 0)
                biopac.setData(biopac, instructioncode)
            onset = globalClock.getTime() - fmriStart
            win.flip()

            timer = core.CountdownTimer()
            timer.add(5)
            while timer.getTime() > 0:
                continue
            
            # Replace the above code with 
            # trialData=showText("Instructions", InstructionText, biopacCode=instructioncode)
                        
            # medmap_bids_trial = []
            
            # medmap_bids_trial.extend((onset, globalClock.getTime() - fmriStart - onset, None, bodySites[runs], temperature, InstructionCondition, None))

            # medmap_bids.append(medmap_bids_trial)
            medmap_bids.append(showText("Instructions", InstructionText, biopacCode=instructioncode))

            routineTimer.reset()

        # Select Medoc Thermal Program
        if thermode_exists == 1:
            sendCommand('select_tp', thermodeCommand)

        """ 
        12. Pre-Heat Fixation Cross
        """
        if not jitter2 and r == 0:
            jitter1 = random.choice([3,5,7])
        if not jitter2 and r != 0:
            jitter1 = random.choice([58,60,62])
        elif jitter2 == 3:
            jitter1 = 62
        elif jitter2 == 5:
            jitter1 = 60
        elif jitter2 == 7:
            jitter1 = 58

        # # ------Prepare to start Routine "Fixation"-------
        # continueRoutine = True

        # routineTimer.add(jitter1)
        # # update component parameters for each repeat
        # # keep track of which components have finished
        # FixationComponents = [fixation]
        # for thisComponent in FixationComponents:
        #     thisComponent.tStart = None
        #     thisComponent.tStop = None
        #     thisComponent.tStartRefresh = None
        #     thisComponent.tStopRefresh = None
        #     if hasattr(thisComponent, 'status'):
        #         thisComponent.status = NOT_STARTED
        # # reset timers
        # t = 0
        # _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        # FixationClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
        # frameN = -1

        # # -------Run Routine "Fixation"-------
        # while continueRoutine and routineTimer.getTime() > 0:
        #     # get current time
        #     t = FixationClock.getTime()
        #     tThisFlip = win.getFutureFlipTime(clock=FixationClock)
        #     tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        #     frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        #     # update/draw components on each frame
            
        #     # *fixation* updates
        #     if fixation.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        #         # keep track of start time/frame for later
        #         fixation.frameNStart = frameN  # exact frame index
        #         fixation.tStart = t  # local t and not account for scr refresh
        #         fixation.tStartRefresh = tThisFlipGlobal  # on global time
        #         win.timeOnFlip(fixation, 'tStartRefresh')  # time at next scr refresh
        #         # if biopac_exists:
        #         #     win.callOnFlip(biopac.setData, biopac, 0)
        #         #     win.callOnFlip(biopac.setData, biopac, medmap_fixation)
        #         fixation.setAutoDraw(True)
        #     if fixation.status == STARTED:
        #         # is it time to stop? (based on global clock, using actual start)
        #         if tThisFlipGlobal > fixation.tStartRefresh + jitter1-frameTolerance:
        #             # keep track of stop time/frame for later
        #             fixation.tStop = t  # not accounting for scr refresh
        #             fixation.frameNStop = frameN  # exact frame index
        #             win.timeOnFlip(fixation, 'tStopRefresh')  # time at next scr refresh
        #             fixation.setAutoDraw(False)
            
        #     # check for quit (typically the Esc key)
        #     if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
        #         core.quit()
            
        #     # check if all components have finished
        #     if not continueRoutine:  # a component has requested a forced-end of Routine
        #         break
        #     continueRoutine = False  # will revert to True if at least one component still running
        #     for thisComponent in FixationComponents:
        #         if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
        #             continueRoutine = True
        #             break  # at least one component has not yet finished
            
        #     # refresh the screen
        #     if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        #         win.flip()

        # # -------Ending Routine "Fixation"-------
        # if biopac_exists:
        #     win.callOnFlip(biopac.setData, biopac, 0)
        # for thisComponent in FixationComponents:
        #     if hasattr(thisComponent, "setAutoDraw"):
        #         thisComponent.setAutoDraw(False)
        # thisExp.addData('fixation.started', fixation.tStartRefresh)
        # thisExp.addData('fixation.stopped', fixation.tStopRefresh)

        # routineTimer.reset()

        # Replace above with 
        medmap_bids.append(showFixation(t=jitter1, biopacCode=medmap_prefixation))

        """ 
        13. Heat-Trial Fixation Cross
        """
        if thermode_exists == 1:
            sendCommand('trigger') # Trigger the thermode
        medmap_bids.append(showFixation(t=stimtrialTime, biopacCode=BiopacChannel))

        # ------Prepare to start Routine "Fixation"-------
        # Trigger Thermal Program

        # Replace below with 


        # continueRoutine = True

        # routineTimer.add(stimtrialTime)

        # # update component parameters for each repeat
        # # keep track of which components have finished
        # FixationComponents = [fixation]
        # for thisComponent in FixationComponents:
        #     thisComponent.tStart = None
        #     thisComponent.tStop = None
        #     thisComponent.tStartRefresh = None
        #     thisComponent.tStopRefresh = None
        #     if hasattr(thisComponent, 'status'):
        #         thisComponent.status = NOT_STARTED
        # # reset timers
        # t = 0
        # _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        # FixationClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
        # frameN = -1

        # # -------Run Routine "Fixation"-------
        # onset = globalClock.getTime() - fmriStart           # Record onset time of the trial
        # while continueRoutine and routineTimer.getTime() > 0:
        #     # get current time
        #     t = FixationClock.getTime()
        #     tThisFlip = win.getFutureFlipTime(clock=FixationClock)
        #     tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        #     frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        #     # update/draw components on each frame
            
        #     # *fixation* updates
        #     if fixation.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        #         # keep track of start time/frame for later
        #         fixation.frameNStart = frameN  # exact frame index
        #         fixation.tStart = t  # local t and not account for scr refresh
        #         fixation.tStartRefresh = tThisFlipGlobal  # on global time
        #         win.timeOnFlip(fixation, 'tStartRefresh')  # time at next scr refresh
        #         if biopac_exists:
        #             win.callOnFlip(biopac.setData, biopac, 0)
        #             win.callOnFlip(biopac.setData, biopac, BiopacChannel)
        #         fixation.setAutoDraw(True)
        #     if fixation.status == STARTED:
        #         # is it time to stop? (based on global clock, using actual start)
        #         if tThisFlipGlobal > fixation.tStartRefresh + stimtrialTime-frameTolerance:
        #             # keep track of stop time/frame for later
        #             fixation.tStop = t  # not accounting for scr refresh
        #             fixation.frameNStop = frameN  # exact frame index
        #             win.timeOnFlip(fixation, 'tStopRefresh')  # time at next scr refresh
        #             fixation.setAutoDraw(False)
            
        #     # check for quit (typically the Esc key)
        #     if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
        #         core.quit()
            
        #     # check if all components have finished
        #     if not continueRoutine:  # a component has requested a forced-end of Routine
        #         break
        #     continueRoutine = False  # will revert to True if at least one component still running
        #     for thisComponent in FixationComponents:
        #         if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
        #             continueRoutine = True
        #             break  # at least one component has not yet finished
            
        #     # refresh the screen
        #     if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        #         win.flip()

        # # -------Ending Routine "Fixation"-------
        # if biopac_exists:
        #     win.callOnFlip(biopac.setData, biopac, 0)
        # for thisComponent in FixationComponents:
        #     if hasattr(thisComponent, "setAutoDraw"):
        #         thisComponent.setAutoDraw(False)
        # thisExp.addData('fixation.started', fixation.tStartRefresh)
        # thisExp.addData('fixation.stopped', fixation.tStopRefresh)

        # medmap_bids_trial = []

        # medmap_bids_trial.extend((onset, t, None, bodySites[runs], temperature, ConditionName, jitter1))

        # medmap_bids.append(medmap_bids_trial)

        # routineTimer.reset()

        """
        # BIDS Dictionaries should be updated something like this way:
        # iterate through showFixation(), attaching the values to keys in medmap_bids_trial.

        # medmap_bids_trial['rating']=
        # medmap_bids_trial['bodysite']=
        # medmap_bids_trial['temperature']=
        # medmap_bids.append(list(medmap_bids_trial.values())        
        """


        """
        14. Post-Heat Fixation Cross
        """
        jitter2 = random.choice([3,5,7])
        
        medmap_bids.append(showFixation(t=jitter2, biopacCode=medmap_postfixation))

        rating_sound.play()
        
        # # ------Prepare to start Routine "Fixation"-------
        # continueRoutine = True
        # routineTimer.add(jitter2)

        # # update component parameters for each repeat
        # # keep track of which components have finished
        # FixationComponents = [fixation]
        # for thisComponent in FixationComponents:
        #     thisComponent.tStart = None
        #     thisComponent.tStop = None
        #     thisComponent.tStartRefresh = None
        #     thisComponent.tStopRefresh = None
        #     if hasattr(thisComponent, 'status'):
        #         thisComponent.status = NOT_STARTED
        # # reset timers
        # t = 0
        # _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        # FixationClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
        # frameN = -1

        # # -------Run Routine "Fixation"-------
        # while continueRoutine and routineTimer.getTime() > 0:
        #     # get current time
        #     t = FixationClock.getTime()
        #     tThisFlip = win.getFutureFlipTime(clock=FixationClock)
        #     tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        #     frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        #     # update/draw components on each frame
            
        #     # *fixation* updates
        #     if fixation.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        #         # keep track of start time/frame for later
        #         fixation.frameNStart = frameN  # exact frame index
        #         fixation.tStart = t  # local t and not account for scr refresh
        #         fixation.tStartRefresh = tThisFlipGlobal  # on global time
        #         win.timeOnFlip(fixation, 'tStartRefresh')  # time at next scr refresh
        #         # if biopac_exists:
        #         #     win.callOnFlip(biopac.setData, biopac, 0)
        #         #     win.callOnFlip(biopac.setData, biopac, nback_fixation)
        #         fixation.setAutoDraw(True)
        #     if fixation.status == STARTED:
        #         # is it time to stop? (based on global clock, using actual start)
        #         if tThisFlipGlobal > fixation.tStartRefresh + jitter2-frameTolerance:
        #             # keep track of stop time/frame for later
        #             fixation.tStop = t  # not accounting for scr refresh
        #             fixation.frameNStop = frameN  # exact frame index
        #             win.timeOnFlip(fixation, 'tStopRefresh')  # time at next scr refresh
        #             fixation.setAutoDraw(False)
            
        #     # check for quit (typically the Esc key)
        #     if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
        #         core.quit()
            
        #     # check if all components have finished
        #     if not continueRoutine:  # a component has requested a forced-end of Routine
        #         break
        #     continueRoutine = False  # will revert to True if at least one component still running
        #     for thisComponent in FixationComponents:
        #         if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
        #             continueRoutine = True
        #             break  # at least one component has not yet finished
            
        #     # refresh the screen
        #     if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        #         win.flip()

        # # -------Ending Routine "Fixation"-------
        # if biopac_exists:
        #     win.callOnFlip(biopac.setData, biopac, 0)
        # for thisComponent in FixationComponents:
        #     if hasattr(thisComponent, "setAutoDraw"):
        #         thisComponent.setAutoDraw(False)
        # thisExp.addData('fixation.started', fixation.tStartRefresh)
        # thisExp.addData('fixation.stopped', fixation.tStopRefresh)
        # routineTimer.reset()


        """
        8f. Begin post-trial self-report questions
        """        

        ############ ASK PAIN BINARY Question #######################################
        # # ------Prepare to start Routine "PainBinary"-------
        # continueRoutine = True
        # routineTimer.add(ratingTime)
        # # update component parameters for each repeat
        # # setup some python lists for storing info about the mouse
        
        # PainMouse = event.Mouse(win=win, visible=False) # Re-initialize PainMouse
        # PainMouse.setPos((0,0))
        # timeAtLastInterval = 0
        # mouseX = 0
        # oldMouseX = 0
        # PainBinary.width = 0
        # PainBinary.pos = (0,0)
        
        # # keep track of which components have finished
        # PainBinaryComponents = [PainMouse, PainBinary, PainAnchors, PainPrompt]
        # for thisComponent in PainBinaryComponents:
        #     thisComponent.tStart = None
        #     thisComponent.tStop = None
        #     thisComponent.tStartRefresh = None
        #     thisComponent.tStopRefresh = None
        #     if hasattr(thisComponent, 'status'):
        #         thisComponent.status = NOT_STARTED
        # # reset timers
        # t = 0
        # _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        # PainBinaryClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
        # frameN = -1

        # # -------Run Routine "PainBinary"-------
        # onset = globalClock.getTime() - fmriStart           # Record onset time of the trial
        # while continueRoutine:
        #     # get current time
        #     t = PainBinaryClock.getTime()
        #     tThisFlip = win.getFutureFlipTime(clock=PainBinaryClock)
        #     tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        #     frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        #     # update/draw components on each frame

        #     timeNow = globalClock.getTime()
        #     if (timeNow - timeAtLastInterval) > TIME_INTERVAL:
        #         mouseRel=PainMouse.getRel()
        #         mouseX=oldMouseX + mouseRel[0]
            
        #     if mouseX==0:
        #         PainBinary.width = 0
        #     else:
        #         if mouseX>0:
        #             PainBinary.pos = (.28,0)
        #             sliderValue=1
        #         elif mouseX<0:
        #             PainBinary.pos = (-.4,0)
        #             sliderValue=-1
        #         PainBinary.width = .5

        #     timeAtLastInterval = timeNow
        #     oldMouseX=mouseX

        #     # *PainMouse* updates
        #     if PainMouse.status == NOT_STARTED and t >= 0.0-frameTolerance:
        #         # keep track of start time/frame for later
        #         PainMouse.frameNStart = frameN  # exact frame index
        #         PainMouse.tStart = t  # local t and not account for scr refresh
        #         PainMouse.tStartRefresh = tThisFlipGlobal  # on global time
        #         win.timeOnFlip(PainMouse, 'tStartRefresh')  # time at next scr refresh
        #         PainMouse.status = STARTED
        #         PainMouse.mouseClock.reset()
        #         prevButtonState = PainMouse.getPressed()  # if button is down already this ISN'T a new click
        #     if PainMouse.status == STARTED:  # only update if started and not finished!
        #         if tThisFlipGlobal > PainMouse.tStartRefresh + ratingTime-frameTolerance:
        #             # keep track of stop time/frame for later
        #             PainMouse.tStop = t  # not accounting for scr refresh
        #             PainMouse.frameNStop = frameN  # exact frame index
        #             PainMouse.status = FINISHED
        #         buttons = PainMouse.getPressed()
        #         if buttons != prevButtonState:  # button state changed?
        #             prevButtonState = buttons
        #             if sum(buttons) > 0:  # state changed to a new click
        #                 # abort routine on response
        #                 continueRoutine = False

        #     # *PainBinary* updates
        #     if PainBinary.status == NOT_STARTED and t >= 0.0-frameTolerance:
        #         # keep track of start time/frame for later
        #         PainBinary.frameNStart = frameN  # exact frame index
        #         PainBinary.tStart = t  # local t and not account for scr refresh
        #         PainBinary.tStartRefresh = tThisFlipGlobal  # on global time
        #         win.callOnFlip(print, "Show Pain Rating")
        #         if biopac_exists == 1:
        #             win.callOnFlip(biopac.setData, biopac, 0)
        #             win.callOnFlip(biopac.setData, biopac, pain_binary)
        #         win.timeOnFlip(PainBinary, 'tStartRefresh')  # time at next scr refresh
        #         PainBinary.setAutoDraw(True)
        #     if PainBinary.status == STARTED:
        #         # is it time to stop? (based on global clock, using actual start)
        #         if tThisFlipGlobal > PainBinary.tStartRefresh + ratingTime-frameTolerance:
        #             # keep track of stop time/frame for later
        #             PainBinary.tStop = t  # not accounting for scr refresh
        #             PainBinary.frameNStop = frameN  # exact frame index
        #             win.timeOnFlip(PainBinary, 'tStopRefresh')  # time at next scr refresh
        #             PainBinary.setAutoDraw(False)
            
        #     # *PainAnchors* updates
        #     if PainAnchors.status == NOT_STARTED and t >= 0.0-frameTolerance:
        #         # keep track of start time/frame for later
        #         PainAnchors.frameNStart = frameN  # exact frame index
        #         PainAnchors.tStart = t  # local t and not account for scr refresh
        #         PainAnchors.tStartRefresh = tThisFlipGlobal  # on global time
        #         win.timeOnFlip(PainAnchors, 'tStartRefresh')  # time at next scr refresh
        #         PainAnchors.setAutoDraw(True)
        #     if PainAnchors.status == STARTED:
        #         # is it time to stop? (based on global clock, using actual start)
        #         if tThisFlipGlobal > PainAnchors.tStartRefresh + ratingTime-frameTolerance:
        #             # keep track of stop time/frame for later
        #             PainAnchors.tStop = t  # not accounting for scr refresh
        #             PainAnchors.frameNStop = frameN  # exact frame index
        #             win.timeOnFlip(PainAnchors, 'tStopRefresh')  # time at next scr refresh
        #             PainAnchors.setAutoDraw(False)

        #     # *PainPrompt* updates
        #     if PainPrompt.status == NOT_STARTED and t >= 0.0-frameTolerance:
        #         # keep track of start time/frame for later
        #         PainPrompt.frameNStart = frameN  # exact frame index
        #         PainPrompt.tStart = t  # local t and not account for scr refresh
        #         PainPrompt.tStartRefresh = tThisFlipGlobal  # on global time
        #         win.timeOnFlip(PainPrompt, 'tStartRefresh')  # time at next scr refresh
        #         PainPrompt.setAutoDraw(True)
        #     if PainPrompt.status == STARTED:
        #         # is it time to stop? (based on global clock, using actual start)
        #         if tThisFlipGlobal > PainPrompt.tStartRefresh + ratingTime-frameTolerance:
        #             # keep track of stop time/frame for later
        #             PainPrompt.tStop = t  # not accounting for scr refresh
        #             PainPrompt.frameNStop = frameN  # exact frame index
        #             win.timeOnFlip(PainPrompt, 'tStopRefresh')  # time at next scr refresh
        #             PainPrompt.setAutoDraw(False)

        #     # Autoresponder
        #     if t >= thisSimKey.rt and autorespond == 1:
        #         sliderValue = random.randint(-100,100)
        #         continueRoutine = False

        #     # check for quit (typically the Esc key)
        #     if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
        #         core.quit()
            
        #     # check if all components have finished
        #     if not continueRoutine:  # a component has requested a forced-end of Routine
        #         break
        #     continueRoutine = False  # will revert to True if at least one component still running
        #     for thisComponent in PainBinaryComponents:
        #         if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
        #             continueRoutine = True
        #             break  # at least one component has not yet finished
            
        #     # refresh the screen
        #     if continueRoutine:
        #         win.flip()

        # # -------Ending Routine "PainBinary"-------
        # print("CueOff Channel " + str(pain_binary))
        # for thisComponent in PainBinaryComponents:
        #     if hasattr(thisComponent, "setAutoDraw"):
        #         thisComponent.setAutoDraw(False)
        # # store data for thisExp (ExperimentHandler)
        # thisExp.addData('PainBinary.response', sliderValue)
        # thisExp.addData('PainBinary.rt', timeNow-PainBinary.tStart)
        # thisExp.nextEntry()
        # thisExp.addData('PainBinary.started', PainBinary.tStart)
        # thisExp.addData('PainBinary.stopped', PainBinary.tStop)
        # painRating=sliderValue

        # medmap_bids_trial = []
        # medmap_bids_trial.extend((onset, globalClock.getTime() - fmriStart - onset, painRating, bodySites[runs], temperature, 'Pain Rating', jitter2))
        # medmap_bids.append(medmap_bids_trial)

        # # the Routine "PainBinary" was not non-slip safe, so reset the non-slip timer
        # routineTimer.reset()

        # replace above with 
        medmap_bids.append(showBinaryScale("PainBinary", painText, ratingTime, biopacCode=pain_binary))


        medmap_bids.append(showUnipolarScale("IntensityRating", trialIntensityText, ratingTime, biopacCode=trialIntensity_rating))


        ############ ASK PAIN INTENSITY #######################################
        # ------Prepare to start Routine "IntensityRating"-------
        # continueRoutine = True
        # routineTimer.add(ratingTime)
        # # update component parameters for each repeat
        # # keep track of which components have finished
        # IntensityMouse = event.Mouse(win=win, visible=False) # Re-initialize IntensityMouse
        # IntensityMouse.setPos((0,0))
        # timeAtLastInterval = 0
        # mouseX = 0
        # oldMouseX = 0
        # IntensityRating.width = abs(sliderMin)
        # IntensityRating.pos = [sliderMin/2, -.1]

        # IntensityRatingComponents = [IntensityMouse, IntensityBlackTriangle, IntensityRating, IntensityAnchors, IntensityPrompt]
        # for thisComponent in IntensityRatingComponents:
        #     thisComponent.tStart = None
        #     thisComponent.tStop = None
        #     thisComponent.tStartRefresh = None
        #     thisComponent.tStopRefresh = None
        #     if hasattr(thisComponent, 'status'):
        #         thisComponent.status = NOT_STARTED
        # # reset timers
        # t = 0
        # _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        # IntensityRatingClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
        # frameN = -1

        # # -------Run Routine "IntensityRating"-------
        # onset = globalClock.getTime() - fmriStart           # Record onset time of the trial
        # while continueRoutine:
        #     timeNow = globalClock.getTime()
        #     if (timeNow - timeAtLastInterval) > TIME_INTERVAL:
        #         mouseRel=IntensityMouse.getRel()
        #         mouseX=oldMouseX + mouseRel[0]
        #     IntensityRating.pos = ((sliderMin + mouseX)/2,0)
        #     IntensityRating.width = abs((mouseX-sliderMin))
        #     if mouseX > sliderMax:
        #         mouseX = sliderMax
        #     if mouseX < sliderMin:
        #         mouseX = sliderMin
        #     timeAtLastInterval = timeNow
        #     oldMouseX=mouseX
        #     sliderValue = (mouseX - sliderMin) / (sliderMax - sliderMin) * 100

        #     # get current time
        #     t = IntensityRatingClock.getTime()
        #     tThisFlip = win.getFutureFlipTime(clock=IntensityRatingClock)
        #     tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        #     frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        #     # update/draw components on each frame
            
        #     # *IntensityMouse* updates
        #     if IntensityMouse.status == NOT_STARTED and t >= 0.0-frameTolerance:
        #         # keep track of start time/frame for later
        #         IntensityMouse.frameNStart = frameN  # exact frame index
        #         IntensityMouse.tStart = t  # local t and not account for scr refresh
        #         IntensityMouse.tStartRefresh = tThisFlipGlobal  # on global time
        #         win.timeOnFlip(IntensityMouse, 'tStartRefresh')  # time at next scr refresh
        #         IntensityMouse.status = STARTED
        #         IntensityMouse.mouseClock.reset()
        #         prevButtonState = IntensityMouse.getPressed()  # if button is down already this ISN'T a new click
        #     if IntensityMouse.status == STARTED:  # only update if started and not finished!
        #         if tThisFlipGlobal > IntensityMouse.tStartRefresh + ratingTime-frameTolerance:
        #             # keep track of stop time/frame for later
        #             IntensityMouse.tStop = t  # not accounting for scr refresh
        #             IntensityMouse.frameNStop = frameN  # exact frame index
        #             IntensityMouse.status = FINISHED
        #         buttons = IntensityMouse.getPressed()
        #         if buttons != prevButtonState:  # button state changed?
        #             prevButtonState = buttons
        #             if sum(buttons) > 0:  # state changed to a new click
        #                 # abort routine on response
        #                 continueRoutine = False
            
        #     # *IntensityRating* updates
        #     if IntensityRating.status == NOT_STARTED and t >= 0.0-frameTolerance:
        #         # keep track of start time/frame for later
        #         IntensityRating.frameNStart = frameN  # exact frame index
        #         IntensityRating.tStart = t  # local t and not account for scr refresh
        #         IntensityRating.tStartRefresh = tThisFlipGlobal  # on global time
        #         win.callOnFlip(print, "Show Intensity Rating")
        #         if biopac_exists == 1:
        #             win.callOnFlip(biopac.setData, biopac, 0)
        #             win.callOnFlip(biopac.setData, biopac, intensity_rating)
        #         win.timeOnFlip(IntensityRating, 'tStartRefresh')  # time at next scr refresh
        #         IntensityRating.setAutoDraw(True)
        #     if IntensityRating.status == STARTED:
        #         # is it time to stop? (based on global clock, using actual start)
        #         if tThisFlipGlobal > IntensityRating.tStartRefresh + ratingTime-frameTolerance:
        #             # keep track of stop time/frame for later
        #             IntensityRating.tStop = t  # not accounting for scr refresh
        #             IntensityRating.frameNStop = frameN  # exact frame index
        #             win.timeOnFlip(IntensityRating, 'tStopRefresh')  # time at next scr refresh
        #             IntensityRating.setAutoDraw(False)
            
        #     # *IntensityBlackTriangle* updates
        #     if IntensityBlackTriangle.status == NOT_STARTED and t >= 0.0-frameTolerance:
        #         # keep track of start time/frame for later
        #         IntensityBlackTriangle.frameNStart = frameN  # exact frame index
        #         IntensityBlackTriangle.tStart = t  # local t and not account for scr refresh
        #         IntensityBlackTriangle.tStartRefresh = tThisFlipGlobal  # on global time
        #         win.timeOnFlip(IntensityBlackTriangle, 'tStartRefresh')  # time at next scr refresh
        #         IntensityBlackTriangle.setAutoDraw(True)
        #     if IntensityBlackTriangle.status == STARTED:
        #         # is it time to stop? (based on global clock, using actual start)
        #         if tThisFlipGlobal > IntensityBlackTriangle.tStartRefresh + ratingTime-frameTolerance:
        #             # keep track of stop time/frame for later
        #             IntensityBlackTriangle.tStop = t  # not accounting for scr refresh
        #             IntensityBlackTriangle.frameNStop = frameN  # exact frame index
        #             win.timeOnFlip(IntensityBlackTriangle, 'tStopRefresh')  # time at next scr refresh
        #             IntensityBlackTriangle.setAutoDraw(False)
            
        #     # *IntensityAnchors* updates
        #     if IntensityAnchors.status == NOT_STARTED and t >= 0.0-frameTolerance:
        #         # keep track of start time/frame for later
        #         IntensityAnchors.frameNStart = frameN  # exact frame index
        #         IntensityAnchors.tStart = t  # local t and not account for scr refresh
        #         IntensityAnchors.tStartRefresh = tThisFlipGlobal  # on global time
        #         win.timeOnFlip(IntensityAnchors, 'tStartRefresh')  # time at next scr refresh
        #         IntensityAnchors.setAutoDraw(True)
        #     if IntensityAnchors.status == STARTED:
        #         # is it time to stop? (based on global clock, using actual start)
        #         if tThisFlipGlobal > IntensityAnchors.tStartRefresh + ratingTime-frameTolerance:
        #             # keep track of stop time/frame for later
        #             IntensityAnchors.tStop = t  # not accounting for scr refresh
        #             IntensityAnchors.frameNStop = frameN  # exact frame index
        #             win.timeOnFlip(IntensityAnchors, 'tStopRefresh')  # time at next scr refresh
        #             IntensityAnchors.setAutoDraw(False)
            
        #     # *IntensityPrompt* updates
        #     if IntensityPrompt.status == NOT_STARTED and t >= 0.0-frameTolerance:
        #         # keep track of start time/frame for later
        #         IntensityPrompt.frameNStart = frameN  # exact frame index
        #         IntensityPrompt.tStart = t  # local t and not account for scr refresh
        #         IntensityPrompt.tStartRefresh = tThisFlipGlobal  # on global time
        #         win.timeOnFlip(IntensityPrompt, 'tStartRefresh')  # time at next scr refresh
        #         IntensityPrompt.setAutoDraw(True)
        #     if IntensityPrompt.status == STARTED:
        #         # is it time to stop? (based on global clock, using actual start)
        #         if tThisFlipGlobal > IntensityPrompt.tStartRefresh + ratingTime-frameTolerance:
        #             # keep track of stop time/frame for later
        #             IntensityPrompt.tStop = t  # not accounting for scr refresh
        #             IntensityPrompt.frameNStop = frameN  # exact frame index
        #             win.timeOnFlip(IntensityPrompt, 'tStopRefresh')  # time at next scr refresh
        #             IntensityPrompt.setAutoDraw(False)

        #     # Autoresponder
        #     if t >= thisSimKey.rt and autorespond == 1:
        #         sliderValue = random.randint(0,100)
        #         continueRoutine = False

        #     # check for quit (typically the Esc key)
        #     if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
        #         core.quit()
            
        #     # check if all components have finished
        #     if not continueRoutine:  # a component has requested a forced-end of Routine
        #         break
        #     continueRoutine = False  # will revert to True if at least one component still running
        #     for thisComponent in IntensityRatingComponents:
        #         if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
        #             continueRoutine = True
        #             break  # at least one component has not yet finished

        #     # refresh the screen
        #     if continueRoutine:
        #         win.flip()

        # # -------Ending Routine "IntensityRating"-------
        # print("CueOff Channel " + str(intensity_rating))
        # for thisComponent in IntensityRatingComponents:
        #     if hasattr(thisComponent, "setAutoDraw"):
        #         thisComponent.setAutoDraw(False)
        # # store data for thisExp (ExperimentHandler)
        # thisExp.addData('IntensityRating.response', sliderValue)
        # thisExp.addData('IntensityRating.rt', timeNow - IntensityRating.tStart)
        # thisExp.nextEntry()
        # thisExp.addData('IntensityRating.started', IntensityRating.tStart)
        # thisExp.addData('IntensityRating.stopped', IntensityRating.tStop)

        # medmap_bids_trial = []
        # medmap_bids_trial.extend((onset, globalClock.getTime() - fmriStart - onset, sliderValue, bodySites[runs], temperature, 'Intensity Rating', None))
        # medmap_bids.append(medmap_bids_trial)

        # # the Routine "IntensityRating" was not non-slip safe, so reset the non-slip timer
        # routineTimer.reset()

        ########################## END SELF REPORT #######################################################
    rating_sound.stop() # I think a stop needs to be introduced in order to play again.
    rating_sound.play()

    """
    16. Begin post-run self-report questions
    """        
    # Update Rating Time
    ratingTime = 60 # Limit answering time to 1-minute per question

    medmap_bids.append(showBipolarScale("ComfortRating", ComfortText, ratingTime, biopacCode=comfort_rating))
    ########### ASK Body Comfort ###########################################

    # ------Prepare to start Routine "ComfortRating"-------
    # continueRoutine = True
    # routineTimer.add(ratingTime)
    # # update component parameters for each repeat
    # # ComfortRating.reset()
    # ComfortMouse = event.Mouse(win=win, visible=False) # Re-initialize ComfortMouse
    # ComfortMouse.setPos((0,0))
    # timeAtLastInterval = 0
    # mouseX = 0
    # oldMouseX = 0
    # ComfortRating.width = 0
    # ComfortRating.pos = (0,0)

    # # keep track of which components have finished
    # ComfortRatingComponents = [ComfortMouse, ComfortRating, ComfortBlackTriangle, ComfortAnchors, ComfortPrompt]
    # for thisComponent in ComfortRatingComponents:
    #     thisComponent.tStart = None
    #     thisComponent.tStop = None
    #     thisComponent.tStartRefresh = None
    #     thisComponent.tStopRefresh = None
    #     if hasattr(thisComponent, 'status'):
    #         thisComponent.status = NOT_STARTED
    # # reset timers
    # t = 0
    # _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    # ComfortRatingClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    # frameN = -1

    # # -------Run Routine "ComfortRating"-------
    # while continueRoutine:
    #     # get current time
    #     t = ComfortRatingClock.getTime()
    #     tThisFlip = win.getFutureFlipTime(clock=ComfortRatingClock)
    #     tThisFlipGlobal = win.getFutureFlipTime(clock=None)
    #     frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    #     # update/draw components on each frame

    #     timeNow = globalClock.getTime()
    #     if (timeNow - timeAtLastInterval) > TIME_INTERVAL:
    #         mouseRel=ComfortMouse.getRel()
    #         mouseX=oldMouseX + mouseRel[0]
    #     ComfortRating.pos = (mouseX/2,0)
    #     ComfortRating.width = abs(mouseX)
    #     if mouseX > sliderMax:
    #         mouseX = sliderMax
    #     if mouseX < sliderMin:
    #         mouseX = sliderMin
    #     timeAtLastInterval = timeNow
    #     oldMouseX=mouseX
    #     sliderValue = ((mouseX - sliderMin) / (sliderMax - sliderMin) * 200)-100

    #     # *ComfortMouse* updates
    #     if ComfortMouse.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         ComfortMouse.frameNStart = frameN  # exact frame index
    #         ComfortMouse.tStart = t  # local t and not account for scr refresh
    #         ComfortMouse.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(ComfortMouse, 'tStartRefresh')  # time at next scr refresh
    #         ComfortMouse.status = STARTED
    #         ComfortMouse.mouseClock.reset()
    #         prevButtonState = ComfortMouse.getPressed()  # if button is down already this ISN'T a new click
    #     if ComfortMouse.status == STARTED:  # only update if started and not finished!
    #         if tThisFlipGlobal > ComfortMouse.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             ComfortMouse.tStop = t  # not accounting for scr refresh
    #             ComfortMouse.frameNStop = frameN  # exact frame index
    #             ComfortMouse.status = FINISHED
    #         buttons = ComfortMouse.getPressed()
    #         if buttons != prevButtonState:  # button state changed?
    #             prevButtonState = buttons
    #             if sum(buttons) > 0:  # state changed to a new click
    #                 # abort routine on response
    #                 continueRoutine = False

    #     # *ComfortRating* updates
    #     if ComfortRating.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         ComfortRating.frameNStart = frameN  # exact frame index
    #         ComfortRating.tStart = t  # local t and not account for scr refresh
    #         ComfortRating.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.callOnFlip(print, "Show Comfort Rating")
    #         if biopac_exists == 1:
    #             win.callOnFlip(biopac.setData, biopac, 0)
    #             win.callOnFlip(biopac.setData, biopac, comfort_rating)
    #         win.timeOnFlip(ComfortRating, 'tStartRefresh')  # time at next scr refresh
    #         ComfortRating.setAutoDraw(True)
    #     if ComfortRating.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > ComfortRating.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             ComfortRating.tStop = t  # not accounting for scr refresh
    #             ComfortRating.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(ComfortRating, 'tStopRefresh')  # time at next scr refresh
    #             ComfortRating.setAutoDraw(False)
        
    #     # *ComfortBlackTriangle* updates
    #     if ComfortBlackTriangle.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         ComfortBlackTriangle.frameNStart = frameN  # exact frame index
    #         ComfortBlackTriangle.tStart = t  # local t and not account for scr refresh
    #         ComfortBlackTriangle.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(ComfortBlackTriangle, 'tStartRefresh')  # time at next scr refresh
    #         ComfortBlackTriangle.setAutoDraw(True)
    #     if ComfortBlackTriangle.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > ComfortBlackTriangle.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             ComfortBlackTriangle.tStop = t  # not accounting for scr refresh
    #             ComfortBlackTriangle.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(ComfortBlackTriangle, 'tStopRefresh')  # time at next scr refresh
    #             ComfortBlackTriangle.setAutoDraw(False)

    #     # *ComfortAnchors* updates
    #     if ComfortAnchors.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         ComfortAnchors.frameNStart = frameN  # exact frame index
    #         ComfortAnchors.tStart = t  # local t and not account for scr refresh
    #         ComfortAnchors.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(ComfortAnchors, 'tStartRefresh')  # time at next scr refresh
    #         ComfortAnchors.setAutoDraw(True)
    #     if ComfortAnchors.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > ComfortAnchors.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             ComfortAnchors.tStop = t  # not accounting for scr refresh
    #             ComfortAnchors.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(ComfortAnchors, 'tStopRefresh')  # time at next scr refresh
    #             ComfortAnchors.setAutoDraw(False)
        
    #     # *ComfortPrompt* updates
    #     if ComfortPrompt.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         ComfortPrompt.frameNStart = frameN  # exact frame index
    #         ComfortPrompt.tStart = t  # local t and not account for scr refresh
    #         ComfortPrompt.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(ComfortPrompt, 'tStartRefresh')  # time at next scr refresh
    #         ComfortPrompt.setAutoDraw(True)
    #     if ComfortPrompt.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > ComfortPrompt.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             ComfortPrompt.tStop = t  # not accounting for scr refresh
    #             ComfortPrompt.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(ComfortPrompt, 'tStopRefresh')  # time at next scr refresh
    #             ComfortPrompt.setAutoDraw(False)
    #     # Autoresponder
    #     if t >= thisSimKey.rt and autorespond == 1:
    #         sliderValue = random.randint(-100,100)
    #         continueRoutine = False

    #     # check for quit (typically the Esc key)
    #     if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
    #         core.quit()
        
    #     # check if all components have finished
    #     if not continueRoutine:  # a component has requested a forced-end of Routine
    #         break
    #     continueRoutine = False  # will revert to True if at least one component still running
    #     for thisComponent in ComfortRatingComponents:
    #         if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
    #             continueRoutine = True
    #             break  # at least one component has not yet finished
        
    #     # refresh the screen
    #     if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
    #         win.flip()

    # # -------Ending Routine "ComfortRating"-------
    # print("CueOff Channel " + str(comfort_rating))
    # for thisComponent in ComfortRatingComponents:
    #     if hasattr(thisComponent, "setAutoDraw"):
    #         thisComponent.setAutoDraw(False)
    # # store data for thisExp (ExperimentHandler)
    # thisExp.addData('ComfortRating.response', sliderValue)
    # thisExp.addData('ComfortRating.rt', timeNow - ComfortRating.tStart)
    # thisExp.nextEntry()
    # thisExp.addData('ComfortRating.started', ComfortRating.tStart)
    # thisExp.addData('ComfortRating.stopped', ComfortRating.tStop)
    # medmap_bids.append(["Comfort Rating:", sliderValue])
    # # the Routine "ComfortRating" was not non-slip safe, so reset the non-slip timer
    # routineTimer.reset()



    medmap_bids.append(showBipolarScale("ValenceRating", ValenceText, ratingTime, biopacCode=valence_rating))
    ############ ASK PAIN Valence #######################################
    # ------Prepare to start Routine "ValenceRating"-------
    # continueRoutine = True
    # routineTimer.add(ratingTime)
    # # update component parameters for each repeat
    # # setup some python lists for storing info about the mouse

    # ValenceMouse = event.Mouse(win=win, visible=False) # Re-initialize ValenceMouse
    # ValenceMouse.setPos((0,0))
    # timeAtLastInterval = 0
    # mouseX = 0
    # oldMouseX = 0

    # # keep track of which components have finished
    # ValenceRatingComponents = [ValenceMouse, ValenceRating, ValenceBlackTriangle, ValenceAnchors, ValencePrompt]
    # for thisComponent in ValenceRatingComponents:
    #     thisComponent.tStart = None
    #     thisComponent.tStop = None
    #     thisComponent.tStartRefresh = None
    #     thisComponent.tStopRefresh = None
    #     if hasattr(thisComponent, 'status'):
    #         thisComponent.status = NOT_STARTED
    # # reset timers
    # t = 0
    # _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    # ValenceRatingClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    # frameN = -1

    # # -------Run Routine "ValenceRating"-------
    # while continueRoutine:
    #     # get current time
    #     t = ValenceRatingClock.getTime()
    #     tThisFlip = win.getFutureFlipTime(clock=ValenceRatingClock)
    #     tThisFlipGlobal = win.getFutureFlipTime(clock=None)
    #     frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    #     # update/draw components on each frame

    #     timeNow = globalClock.getTime()
    #     if (timeNow - timeAtLastInterval) > TIME_INTERVAL:
    #         mouseRel=ValenceMouse.getRel()
    #         mouseX=oldMouseX + mouseRel[0]
    #     ValenceRating.pos = ((sliderMin + mouseX)/2,0)
    #     ValenceRating.width = abs((mouseX-sliderMin))
    #     if mouseX > sliderMax:
    #         mouseX = sliderMax
    #     if mouseX < sliderMin:
    #         mouseX = sliderMin
    #     timeAtLastInterval = timeNow
    #     oldMouseX=mouseX
    #     sliderValue = ((mouseX - sliderMin) / (sliderMax - sliderMin) * 200)-100

    #     # *ValenceMouse* updates
    #     if ValenceMouse.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         ValenceMouse.frameNStart = frameN  # exact frame index
    #         ValenceMouse.tStart = t  # local t and not account for scr refresh
    #         ValenceMouse.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(ValenceMouse, 'tStartRefresh')  # time at next scr refresh
    #         ValenceMouse.status = STARTED
    #         ValenceMouse.mouseClock.reset()
    #         prevButtonState = ValenceMouse.getPressed()  # if button is down already this ISN'T a new click
    #     if ValenceMouse.status == STARTED:  # only update if started and not finished!
    #         if tThisFlipGlobal > ValenceMouse.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             ValenceMouse.tStop = t  # not accounting for scr refresh
    #             ValenceMouse.frameNStop = frameN  # exact frame index
    #             ValenceMouse.status = FINISHED
    #         buttons = ValenceMouse.getPressed()
    #         if buttons != prevButtonState:  # button state changed?
    #             prevButtonState = buttons
    #             if sum(buttons) > 0:  # state changed to a new click
    #                 # abort routine on response
    #                 continueRoutine = False

    #     # *ValenceRating* updates
    #     if ValenceRating.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         ValenceRating.frameNStart = frameN  # exact frame index
    #         ValenceRating.tStart = t  # local t and not account for scr refresh
    #         ValenceRating.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.callOnFlip(print, "Show Valence Rating")
    #         if biopac_exists == 1:
    #             win.callOnFlip(biopac.setData, biopac, 0)
    #             win.callOnFlip(biopac.setData, biopac, valence_rating)
    #         win.timeOnFlip(ValenceRating, 'tStartRefresh')  # time at next scr refresh
    #         ValenceRating.setAutoDraw(True)
    #     if ValenceRating.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > ValenceRating.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             ValenceRating.tStop = t  # not accounting for scr refresh
    #             ValenceRating.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(ValenceRating, 'tStopRefresh')  # time at next scr refresh
    #             ValenceRating.setAutoDraw(False)
        
    #     # *ValenceBlackTriangle* updates
    #     if ValenceBlackTriangle.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         ValenceBlackTriangle.frameNStart = frameN  # exact frame index
    #         ValenceBlackTriangle.tStart = t  # local t and not account for scr refresh
    #         ValenceBlackTriangle.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(ValenceBlackTriangle, 'tStartRefresh')  # time at next scr refresh
    #         ValenceBlackTriangle.setAutoDraw(True)
    #     if ValenceBlackTriangle.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > ValenceBlackTriangle.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             ValenceBlackTriangle.tStop = t  # not accounting for scr refresh
    #             ValenceBlackTriangle.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(ValenceBlackTriangle, 'tStopRefresh')  # time at next scr refresh
    #             ValenceBlackTriangle.setAutoDraw(False)

    #     # *ValenceAnchors* updates
    #     if ValenceAnchors.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         ValenceAnchors.frameNStart = frameN  # exact frame index
    #         ValenceAnchors.tStart = t  # local t and not account for scr refresh
    #         ValenceAnchors.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(ValenceAnchors, 'tStartRefresh')  # time at next scr refresh
    #         ValenceAnchors.setAutoDraw(True)
    #     if ValenceAnchors.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > ValenceAnchors.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             ValenceAnchors.tStop = t  # not accounting for scr refresh
    #             ValenceAnchors.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(ValenceAnchors, 'tStopRefresh')  # time at next scr refresh
    #             ValenceAnchors.setAutoDraw(False)

    #     # *ValencePrompt* updates
    #     if ValencePrompt.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         ValencePrompt.frameNStart = frameN  # exact frame index
    #         ValencePrompt.tStart = t  # local t and not account for scr refresh
    #         ValencePrompt.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(ValencePrompt, 'tStartRefresh')  # time at next scr refresh
    #         ValencePrompt.setAutoDraw(True)
    #     if ValencePrompt.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > ValencePrompt.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             ValencePrompt.tStop = t  # not accounting for scr refresh
    #             ValencePrompt.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(ValencePrompt, 'tStopRefresh')  # time at next scr refresh
    #             ValencePrompt.setAutoDraw(False)

    #     # Autoresponder
    #     if t >= thisSimKey.rt and autorespond == 1:
    #         sliderValue = random.randint(-100,100)
    #         continueRoutine = False

    #     # check for quit (typically the Esc key)
    #     if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
    #         core.quit()
        
    #     # check if all components have finished
    #     if not continueRoutine:  # a component has requested a forced-end of Routine
    #         break
    #     continueRoutine = False  # will revert to True if at least one component still running
    #     for thisComponent in ValenceRatingComponents:
    #         if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
    #             continueRoutine = True
    #             break  # at least one component has not yet finished
        
    #     # refresh the screen
    #     if continueRoutine:
    #         win.flip()

    # # -------Ending Routine "ValenceRating"-------
    # print("CueOff Channel " + str(valence_rating))
    # for thisComponent in ValenceRatingComponents:
    #     if hasattr(thisComponent, "setAutoDraw"):
    #         thisComponent.setAutoDraw(False)
    # # store data for thisExp (ExperimentHandler)
    # thisExp.addData('ValenceRating.response', sliderValue)
    # thisExp.addData('ValenceRating.rt', timeNow-ValenceRating.tStart)
    # thisExp.nextEntry()
    # thisExp.addData('ValenceRating.started', ValenceRating.tStart)
    # thisExp.addData('ValenceRating.stopped', ValenceRating.tStop)
    # medmap_bids.append(["Valence Rating:", sliderValue])
    # # the Routine "ValenceRating" was not non-slip safe, so reset the non-slip timer
    # routineTimer.reset()

    medmap_bids.append(showUnipolarScale("IntensityRating", IntensityText, ratingTime, biopacCode=comfort_rating))

    ############ ASK PAIN Intensity #######################################

    # ------Prepare to start Routine "IntensityRating"-------
    ## Prompt update ##
    ## 0 -- Most intense (Unipolar)
    # IntensityPrompt.text = 'HOW INTENSE was the WORST heat you experienced?'
    # IntensityAnchors = visual.ImageStim(
    #     win=win,
    #     image= os.sep.join([stimuli_dir,"ratingscale","postintensityScale.png"]),
    #     name='intensityAnchors', 
    #     mask=None,
    #     ori=0, pos=(0, -0.09), size=(1.5, .4),
    #     color=[1,1,1], colorSpace='rgb', opacity=1,
    #     flipHoriz=False, flipVert=False,
    #     texRes=512, interpolate=True, depth=0.0)

    # continueRoutine = True
    # routineTimer.add(ratingTime)
    # # update component parameters for each repeat
    # # keep track of which components have finished
    # IntensityMouse = event.Mouse(win=win, visible=False) # Re-initialize IntensityMouse
    # IntensityMouse.setPos((0,0))
    # timeAtLastInterval = 0
    # mouseX = 0
    # oldMouseX = 0
    # IntensityRating.width = abs(sliderMin)
    # IntensityRating.pos = [sliderMin/2, -.1]
    # IntensityRating.fillColor='red'

    # IntensityRatingComponents = [IntensityMouse, IntensityBlackTriangle, IntensityRating, IntensityAnchors, IntensityPrompt]
    # for thisComponent in IntensityRatingComponents:
    #     thisComponent.tStart = None
    #     thisComponent.tStop = None
    #     thisComponent.tStartRefresh = None
    #     thisComponent.tStopRefresh = None
    #     if hasattr(thisComponent, 'status'):
    #         thisComponent.status = NOT_STARTED
    # # reset timers
    # t = 0
    # _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    # IntensityRatingClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    # frameN = -1

    # # -------Run Routine "IntensityRating"-------
    # while continueRoutine:
    #     timeNow = globalClock.getTime()
    #     if (timeNow - timeAtLastInterval) > TIME_INTERVAL:
    #         mouseRel=IntensityMouse.getRel()
    #         mouseX=oldMouseX + mouseRel[0]
    #     IntensityRating.pos = ((sliderMin + mouseX)/2,0)
    #     IntensityRating.width = abs((mouseX-sliderMin))
    #     if mouseX > sliderMax:
    #         mouseX = sliderMax
    #     if mouseX < sliderMin:
    #         mouseX = sliderMin
    #     timeAtLastInterval = timeNow
    #     oldMouseX=mouseX
    #     sliderValue = (mouseX - sliderMin) / (sliderMax - sliderMin) * 100

    #     # get current time
    #     t = IntensityRatingClock.getTime()
    #     tThisFlip = win.getFutureFlipTime(clock=IntensityRatingClock)
    #     tThisFlipGlobal = win.getFutureFlipTime(clock=None)
    #     frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    #     # update/draw components on each frame
        
    #     # *IntensityMouse* updates
    #     if IntensityMouse.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         IntensityMouse.frameNStart = frameN  # exact frame index
    #         IntensityMouse.tStart = t  # local t and not account for scr refresh
    #         IntensityMouse.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(IntensityMouse, 'tStartRefresh')  # time at next scr refresh
    #         IntensityMouse.status = STARTED
    #         IntensityMouse.mouseClock.reset()
    #         prevButtonState = IntensityMouse.getPressed()  # if button is down already this ISN'T a new click
    #     if IntensityMouse.status == STARTED:  # only update if started and not finished!
    #         if tThisFlipGlobal > IntensityMouse.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             IntensityMouse.tStop = t  # not accounting for scr refresh
    #             IntensityMouse.frameNStop = frameN  # exact frame index
    #             IntensityMouse.status = FINISHED
    #         buttons = IntensityMouse.getPressed()
    #         if buttons != prevButtonState:  # button state changed?
    #             prevButtonState = buttons
    #             if sum(buttons) > 0:  # state changed to a new click
    #                 # abort routine on response
    #                 continueRoutine = False
        
    #     # *IntensityRating* updates
    #     if IntensityRating.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         IntensityRating.frameNStart = frameN  # exact frame index
    #         IntensityRating.tStart = t  # local t and not account for scr refresh
    #         IntensityRating.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.callOnFlip(print, "Show Intensity Rating")
    #         if biopac_exists == 1:
    #             win.callOnFlip(biopac.setData, biopac, 0)
    #             win.callOnFlip(biopac.setData, biopac, intensity_rating)
    #         win.timeOnFlip(IntensityRating, 'tStartRefresh')  # time at next scr refresh
    #         IntensityRating.setAutoDraw(True)
    #     if IntensityRating.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > IntensityRating.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             IntensityRating.tStop = t  # not accounting for scr refresh
    #             IntensityRating.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(IntensityRating, 'tStopRefresh')  # time at next scr refresh
    #             IntensityRating.setAutoDraw(False)
        
    #     # *IntensityBlackTriangle* updates
    #     if IntensityBlackTriangle.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         IntensityBlackTriangle.frameNStart = frameN  # exact frame index
    #         IntensityBlackTriangle.tStart = t  # local t and not account for scr refresh
    #         IntensityBlackTriangle.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(IntensityBlackTriangle, 'tStartRefresh')  # time at next scr refresh
    #         IntensityBlackTriangle.setAutoDraw(True)
    #     if IntensityBlackTriangle.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > IntensityBlackTriangle.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             IntensityBlackTriangle.tStop = t  # not accounting for scr refresh
    #             IntensityBlackTriangle.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(IntensityBlackTriangle, 'tStopRefresh')  # time at next scr refresh
    #             IntensityBlackTriangle.setAutoDraw(False)
        
    #     # *IntensityAnchors* updates
    #     if IntensityAnchors.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         IntensityAnchors.frameNStart = frameN  # exact frame index
    #         IntensityAnchors.tStart = t  # local t and not account for scr refresh
    #         IntensityAnchors.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(IntensityAnchors, 'tStartRefresh')  # time at next scr refresh
    #         IntensityAnchors.setAutoDraw(True)
    #     if IntensityAnchors.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > IntensityAnchors.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             IntensityAnchors.tStop = t  # not accounting for scr refresh
    #             IntensityAnchors.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(IntensityAnchors, 'tStopRefresh')  # time at next scr refresh
    #             IntensityAnchors.setAutoDraw(False)
        
    #     # *IntensityPrompt* updates
    #     if IntensityPrompt.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         IntensityPrompt.frameNStart = frameN  # exact frame index
    #         IntensityPrompt.tStart = t  # local t and not account for scr refresh
    #         IntensityPrompt.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(IntensityPrompt, 'tStartRefresh')  # time at next scr refresh
    #         IntensityPrompt.setAutoDraw(True)
    #     if IntensityPrompt.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > IntensityPrompt.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             IntensityPrompt.tStop = t  # not accounting for scr refresh
    #             IntensityPrompt.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(IntensityPrompt, 'tStopRefresh')  # time at next scr refresh
    #             IntensityPrompt.setAutoDraw(False)

    #     # Autoresponder
    #     if t >= thisSimKey.rt and autorespond == 1:
    #         sliderValue = random.randint(0,100)
    #         continueRoutine = False

    #     # check for quit (typically the Esc key)
    #     if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
    #         core.quit()
        
    #     # check if all components have finished
    #     if not continueRoutine:  # a component has requested a forced-end of Routine
    #         break
    #     continueRoutine = False  # will revert to True if at least one component still running
    #     for thisComponent in IntensityRatingComponents:
    #         if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
    #             continueRoutine = True
    #             break  # at least one component has not yet finished

    #     # refresh the screen
    #     if continueRoutine:
    #         win.flip()

    # # -------Ending Routine "IntensityRating"-------
    # print("CueOff Channel " + str(intensity_rating))
    # for thisComponent in IntensityRatingComponents:
    #     if hasattr(thisComponent, "setAutoDraw"):
    #         thisComponent.setAutoDraw(False)
    # # store data for thisExp (ExperimentHandler)
    # thisExp.addData('IntensityRating.response', sliderValue)
    # thisExp.addData('IntensityRating.rt', timeNow - IntensityRating.tStart)
    # thisExp.nextEntry()
    # thisExp.addData('IntensityRating.started', IntensityRating.tStart)
    # thisExp.addData('IntensityRating.stopped', IntensityRating.tStop)
    # medmap_bids.append(["Intensity Rating:", sliderValue])
    # # the Routine "IntensityRating" was not non-slip safe, so reset the non-slip timer
    # routineTimer.reset()

    medmap_bids.append(showBipolarScale("AvoidanceRating", AvoidText, ratingTime, biopacCode=avoid_rating))

    ############ ASK PAIN Avoidance #######################################
    # # ------Prepare to start Routine "AvoidRating"-------
    # continueRoutine = True
    # routineTimer.add(ratingTime)
    # # update component parameters for each repeat
    # # AvoidRating.reset()
    # AvoidMouse = event.Mouse(win=win, visible=False) # Re-initialize AvoidMouse
    # AvoidMouse.setPos((0,0))
    # timeAtLastInterval = 0
    # mouseX = 0
    # oldMouseX = 0
    # AvoidRating.width = abs(sliderMin)
    # AvoidRating.pos = [sliderMin/2, -.1]

    # # keep track of which components have finished
    # AvoidRatingComponents = [AvoidMouse, AvoidRating, AvoidBlackTriangle, AvoidAnchors, AvoidPrompt]
    # for thisComponent in AvoidRatingComponents:
    #     thisComponent.tStart = None
    #     thisComponent.tStop = None
    #     thisComponent.tStartRefresh = None
    #     thisComponent.tStopRefresh = None
    #     if hasattr(thisComponent, 'status'):
    #         thisComponent.status = NOT_STARTED
    # # reset timers
    # t = 0
    # _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    # AvoidRatingClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    # frameN = -1

    # # -------Run Routine "AvoidRating"-------
    # while continueRoutine:
    #     # get current time
    #     t = AvoidRatingClock.getTime()
    #     tThisFlip = win.getFutureFlipTime(clock=AvoidRatingClock)
    #     tThisFlipGlobal = win.getFutureFlipTime(clock=None)
    #     frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    #     # update/draw components on each frame

    #     timeNow = globalClock.getTime()
    #     if (timeNow - timeAtLastInterval) > TIME_INTERVAL:
    #         mouseRel=AvoidMouse.getRel()
    #         mouseX=oldMouseX + mouseRel[0]
    #     AvoidRating.pos = ((sliderMin + mouseX)/2,0)
    #     AvoidRating.width = abs((mouseX-sliderMin))
    #     if mouseX > sliderMax:
    #         mouseX = sliderMax
    #     if mouseX < sliderMin:
    #         mouseX = sliderMin
    #     timeAtLastInterval = timeNow
    #     oldMouseX=mouseX
    #     sliderValue = (mouseX - sliderMin) / (sliderMax - sliderMin) * 100

    #     # *AvoidMouse* updates
    #     if AvoidMouse.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         AvoidMouse.frameNStart = frameN  # exact frame index
    #         AvoidMouse.tStart = t  # local t and not account for scr refresh
    #         AvoidMouse.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(AvoidMouse, 'tStartRefresh')  # time at next scr refresh
    #         AvoidMouse.status = STARTED
    #         AvoidMouse.mouseClock.reset()
    #         prevButtonState = AvoidMouse.getPressed()  # if button is down already this ISN'T a new click
    #     if AvoidMouse.status == STARTED:  # only update if started and not finished!
    #         if tThisFlipGlobal > AvoidMouse.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             AvoidMouse.tStop = t  # not accounting for scr refresh
    #             AvoidMouse.frameNStop = frameN  # exact frame index
    #             AvoidMouse.status = FINISHED
    #         buttons = AvoidMouse.getPressed()
    #         if buttons != prevButtonState:  # button state changed?
    #             prevButtonState = buttons
    #             if sum(buttons) > 0:  # state changed to a new click
    #                 # abort routine on response
    #                 continueRoutine = False

    #     # *AvoidRating* updates
    #     if AvoidRating.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         AvoidRating.frameNStart = frameN  # exact frame index
    #         AvoidRating.tStart = t  # local t and not account for scr refresh
    #         AvoidRating.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.callOnFlip(print, "Show Avoid Rating")
    #         if biopac_exists == 1:
    #             win.callOnFlip(biopac.setData, biopac, 0)
    #             win.callOnFlip(biopac.setData, biopac, avoid_rating)
    #         win.timeOnFlip(AvoidRating, 'tStartRefresh')  # time at next scr refresh
    #         AvoidRating.setAutoDraw(True)
    #     if AvoidRating.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > AvoidRating.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             AvoidRating.tStop = t  # not accounting for scr refresh
    #             AvoidRating.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(AvoidRating, 'tStopRefresh')  # time at next scr refresh
    #             AvoidRating.setAutoDraw(False)
        
    #     # *AvoidBlackTriangle* updates
    #     if AvoidBlackTriangle.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         AvoidBlackTriangle.frameNStart = frameN  # exact frame index
    #         AvoidBlackTriangle.tStart = t  # local t and not account for scr refresh
    #         AvoidBlackTriangle.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(AvoidBlackTriangle, 'tStartRefresh')  # time at next scr refresh
    #         AvoidBlackTriangle.setAutoDraw(True)
    #     if AvoidBlackTriangle.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > AvoidBlackTriangle.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             AvoidBlackTriangle.tStop = t  # not accounting for scr refresh
    #             AvoidBlackTriangle.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(AvoidBlackTriangle, 'tStopRefresh')  # time at next scr refresh
    #             AvoidBlackTriangle.setAutoDraw(False)

    #     # *AvoidAnchors* updates
    #     if AvoidAnchors.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         AvoidAnchors.frameNStart = frameN  # exact frame index
    #         AvoidAnchors.tStart = t  # local t and not account for scr refresh
    #         AvoidAnchors.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(AvoidAnchors, 'tStartRefresh')  # time at next scr refresh
    #         AvoidAnchors.setAutoDraw(True)
    #     if AvoidAnchors.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > AvoidAnchors.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             AvoidAnchors.tStop = t  # not accounting for scr refresh
    #             AvoidAnchors.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(AvoidAnchors, 'tStopRefresh')  # time at next scr refresh
    #             AvoidAnchors.setAutoDraw(False)
        
    #     # *AvoidPrompt* updates
    #     if AvoidPrompt.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         AvoidPrompt.frameNStart = frameN  # exact frame index
    #         AvoidPrompt.tStart = t  # local t and not account for scr refresh
    #         AvoidPrompt.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(AvoidPrompt, 'tStartRefresh')  # time at next scr refresh
    #         AvoidPrompt.setAutoDraw(True)
    #     if AvoidPrompt.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > AvoidPrompt.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             AvoidPrompt.tStop = t  # not accounting for scr refresh
    #             AvoidPrompt.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(AvoidPrompt, 'tStopRefresh')  # time at next scr refresh
    #             AvoidPrompt.setAutoDraw(False)
    #     # Autoresponder
    #     if t >= thisSimKey.rt and autorespond == 1:
    #         sliderValue = random.randint(-100,100)
    #         continueRoutine = False

    #     # check for quit (typically the Esc key)
    #     if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
    #         core.quit()
        
    #     # check if all components have finished
    #     if not continueRoutine:  # a component has requested a forced-end of Routine
    #         break
    #     continueRoutine = False  # will revert to True if at least one component still running
    #     for thisComponent in AvoidRatingComponents:
    #         if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
    #             continueRoutine = True
    #             break  # at least one component has not yet finished
        
    #     # refresh the screen
    #     if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
    #         win.flip()

    # # -------Ending Routine "AvoidRating"-------
    # print("CueOff Channel " + str(avoid_rating))
    # for thisComponent in AvoidRatingComponents:
    #     if hasattr(thisComponent, "setAutoDraw"):
    #         thisComponent.setAutoDraw(False)
    # # store data for thisExp (ExperimentHandler)
    # thisExp.addData('AvoidRating.response', sliderValue)
    # thisExp.addData('AvoidRating.rt', timeNow - AvoidRating.tStart)
    # thisExp.nextEntry()
    # thisExp.addData('AvoidRating.started', AvoidRating.tStart)
    # thisExp.addData('AvoidRating.stopped', AvoidRating.tStop)
    # medmap_bids.append(["Pain Avoidance Rating:", sliderValue])
    # # the Routine "AvoidRating" was not non-slip safe, so reset the non-slip timer
    # routineTimer.reset()

    medmap_bids.append(showBipolarScale("RelaxationRating", RelaxText, ratingTime, biopacCode=relax_rating))

    # ############ ASK Body Relaxation #######################################
    # # ------Prepare to start Routine "RelaxRating"-------
    # continueRoutine = True
    # routineTimer.add(ratingTime)
    # # update component parameters for each repeat
    # # RelaxRating.reset()
    # RelaxMouse = event.Mouse(win=win, visible=False) # Re-initialize RelaxMouse
    # RelaxMouse.setPos((0,0))
    # timeAtLastInterval = 0
    # mouseX = 0
    # oldMouseX = 0
    # RelaxRating.width = abs(sliderMin)
    # RelaxRating.pos = [sliderMin/2, -.1]

    # # keep track of which components have finished
    # RelaxRatingComponents = [RelaxMouse, RelaxRating, RelaxBlackTriangle, RelaxAnchors, RelaxPrompt]
    # for thisComponent in RelaxRatingComponents:
    #     thisComponent.tStart = None
    #     thisComponent.tStop = None
    #     thisComponent.tStartRefresh = None
    #     thisComponent.tStopRefresh = None
    #     if hasattr(thisComponent, 'status'):
    #         thisComponent.status = NOT_STARTED
    # # reset timers
    # t = 0
    # _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    # RelaxRatingClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    # frameN = -1

    # # -------Run Routine "RelaxRating"-------
    # while continueRoutine:
    #     # get current time
    #     t = RelaxRatingClock.getTime()
    #     tThisFlip = win.getFutureFlipTime(clock=RelaxRatingClock)
    #     tThisFlipGlobal = win.getFutureFlipTime(clock=None)
    #     frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    #     # update/draw components on each frame

    #     timeNow = globalClock.getTime()
    #     if (timeNow - timeAtLastInterval) > TIME_INTERVAL:
    #         mouseRel=RelaxMouse.getRel()
    #         mouseX=oldMouseX + mouseRel[0]
    #     RelaxRating.pos = ((sliderMin + mouseX)/2,0)
    #     RelaxRating.width = abs((mouseX-sliderMin))
    #     if mouseX > sliderMax:
    #         mouseX = sliderMax
    #     if mouseX < sliderMin:
    #         mouseX = sliderMin
    #     timeAtLastInterval = timeNow
    #     oldMouseX=mouseX
    #     sliderValue = (mouseX - sliderMin) / (sliderMax - sliderMin) * 100

    #     # *RelaxMouse* updates
    #     if RelaxMouse.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         RelaxMouse.frameNStart = frameN  # exact frame index
    #         RelaxMouse.tStart = t  # local t and not account for scr refresh
    #         RelaxMouse.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(RelaxMouse, 'tStartRefresh')  # time at next scr refresh
    #         RelaxMouse.status = STARTED
    #         RelaxMouse.mouseClock.reset()
    #         prevButtonState = RelaxMouse.getPressed()  # if button is down already this ISN'T a new click
    #     if RelaxMouse.status == STARTED:  # only update if started and not finished!
    #         if tThisFlipGlobal > RelaxMouse.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             RelaxMouse.tStop = t  # not accounting for scr refresh
    #             RelaxMouse.frameNStop = frameN  # exact frame index
    #             RelaxMouse.status = FINISHED
    #         buttons = RelaxMouse.getPressed()
    #         if buttons != prevButtonState:  # button state changed?
    #             prevButtonState = buttons
    #             if sum(buttons) > 0:  # state changed to a new click
    #                 # abort routine on response
    #                 continueRoutine = False

    #     # *RelaxRating* updates
    #     if RelaxRating.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         RelaxRating.frameNStart = frameN  # exact frame index
    #         RelaxRating.tStart = t  # local t and not account for scr refresh
    #         RelaxRating.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.callOnFlip(print, "Show Relax Rating")
    #         if biopac_exists == 1:
    #             win.callOnFlip(biopac.setData, biopac, 0)
    #             win.callOnFlip(biopac.setData, biopac, relax_rating)
    #         win.timeOnFlip(RelaxRating, 'tStartRefresh')  # time at next scr refresh
    #         RelaxRating.setAutoDraw(True)
    #     if RelaxRating.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > RelaxRating.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             RelaxRating.tStop = t  # not accounting for scr refresh
    #             RelaxRating.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(RelaxRating, 'tStopRefresh')  # time at next scr refresh
    #             RelaxRating.setAutoDraw(False)
        
    #     # *RelaxBlackTriangle* updates
    #     if RelaxBlackTriangle.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         RelaxBlackTriangle.frameNStart = frameN  # exact frame index
    #         RelaxBlackTriangle.tStart = t  # local t and not account for scr refresh
    #         RelaxBlackTriangle.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(RelaxBlackTriangle, 'tStartRefresh')  # time at next scr refresh
    #         RelaxBlackTriangle.setAutoDraw(True)
    #     if RelaxBlackTriangle.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > RelaxBlackTriangle.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             RelaxBlackTriangle.tStop = t  # not accounting for scr refresh
    #             RelaxBlackTriangle.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(RelaxBlackTriangle, 'tStopRefresh')  # time at next scr refresh
    #             RelaxBlackTriangle.setAutoDraw(False)

    #     # *RelaxAnchors* updates
    #     if RelaxAnchors.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         RelaxAnchors.frameNStart = frameN  # exact frame index
    #         RelaxAnchors.tStart = t  # local t and not account for scr refresh
    #         RelaxAnchors.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(RelaxAnchors, 'tStartRefresh')  # time at next scr refresh
    #         RelaxAnchors.setAutoDraw(True)
    #     if RelaxAnchors.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > RelaxAnchors.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             RelaxAnchors.tStop = t  # not accounting for scr refresh
    #             RelaxAnchors.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(RelaxAnchors, 'tStopRefresh')  # time at next scr refresh
    #             RelaxAnchors.setAutoDraw(False)
        
    #     # *RelaxPrompt* updates
    #     if RelaxPrompt.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         RelaxPrompt.frameNStart = frameN  # exact frame index
    #         RelaxPrompt.tStart = t  # local t and not account for scr refresh
    #         RelaxPrompt.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(RelaxPrompt, 'tStartRefresh')  # time at next scr refresh
    #         RelaxPrompt.setAutoDraw(True)
    #     if RelaxPrompt.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > RelaxPrompt.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             RelaxPrompt.tStop = t  # not accounting for scr refresh
    #             RelaxPrompt.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(RelaxPrompt, 'tStopRefresh')  # time at next scr refresh
    #             RelaxPrompt.setAutoDraw(False)
    #     # Autoresponder
    #     if t >= thisSimKey.rt and autorespond == 1:
    #         sliderValue = random.randint(-100,100)
    #         continueRoutine = False

    #     # check for quit (typically the Esc key)
    #     if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
    #         core.quit()
        
    #     # check if all components have finished
    #     if not continueRoutine:  # a component has requested a forced-end of Routine
    #         break
    #     continueRoutine = False  # will revert to True if at least one component still running
    #     for thisComponent in RelaxRatingComponents:
    #         if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
    #             continueRoutine = True
    #             break  # at least one component has not yet finished
        
    #     # refresh the screen
    #     if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
    #         win.flip()

    # # -------Ending Routine "RelaxRating"-------
    # print("CueOff Channel " + str(relax_rating))
    # for thisComponent in RelaxRatingComponents:
    #     if hasattr(thisComponent, "setAutoDraw"):
    #         thisComponent.setAutoDraw(False)
    # # store data for thisExp (ExperimentHandler)
    # thisExp.addData('RelaxRating.response', sliderValue)
    # thisExp.addData('RelaxRating.rt', timeNow - RelaxRating.tStart)
    # thisExp.nextEntry()
    # thisExp.addData('RelaxRating.started', RelaxRating.tStart)
    # thisExp.addData('RelaxRating.stopped', RelaxRating.tStop)
    # medmap_bids.append(["Body Relaxation Rating:", sliderValue])
    # # the Routine "RelaxRating" was not non-slip safe, so reset the non-slip timer
    # routineTimer.reset()


    medmap_bids.append(showBipolarScale("AttentionRating", TaskAttentionText, ratingTime, biopacCode=attention_rating))
    # ############ ASK Task Attention #######################################
    # # ------Prepare to start Routine "TaskAttentionRating"-------
    # continueRoutine = True
    # routineTimer.add(ratingTime)
    # # update component parameters for each repeat
    # # TaskAttentionRating.reset()
    # TaskAttentionMouse = event.Mouse(win=win, visible=False) # Re-initialize TaskAttentionMouse
    # TaskAttentionMouse.setPos((0,0))
    # timeAtLastInterval = 0
    # mouseX = 0
    # oldMouseX = 0
    # TaskAttentionRating.width = abs(sliderMin)
    # TaskAttentionRating.pos = [sliderMin/2, -.1]

    # # keep track of which components have finished
    # TaskAttentionRatingComponents = [TaskAttentionMouse, TaskAttentionRating, TaskAttentionBlackTriangle, TaskAttentionAnchors, TaskAttentionPrompt]
    # for thisComponent in TaskAttentionRatingComponents:
    #     thisComponent.tStart = None
    #     thisComponent.tStop = None
    #     thisComponent.tStartRefresh = None
    #     thisComponent.tStopRefresh = None
    #     if hasattr(thisComponent, 'status'):
    #         thisComponent.status = NOT_STARTED
    # # reset timers
    # t = 0
    # _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    # TaskAttentionRatingClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    # frameN = -1

    # # -------Run Routine "TaskAttentionRating"-------
    # while continueRoutine:
    #     # get current time
    #     t = TaskAttentionRatingClock.getTime()
    #     tThisFlip = win.getFutureFlipTime(clock=TaskAttentionRatingClock)
    #     tThisFlipGlobal = win.getFutureFlipTime(clock=None)
    #     frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    #     # update/draw components on each frame

    #     timeNow = globalClock.getTime()
    #     if (timeNow - timeAtLastInterval) > TIME_INTERVAL:
    #         mouseRel=TaskAttentionMouse.getRel()
    #         mouseX=oldMouseX + mouseRel[0]
    #     TaskAttentionRating.pos = ((sliderMin + mouseX)/2,0)
    #     TaskAttentionRating.width = abs((mouseX-sliderMin))
    #     if mouseX > sliderMax:
    #         mouseX = sliderMax
    #     if mouseX < sliderMin:
    #         mouseX = sliderMin
    #     timeAtLastInterval = timeNow
    #     oldMouseX=mouseX
    #     sliderValue = (mouseX - sliderMin) / (sliderMax - sliderMin) * 100

    #     # *TaskAttentionMouse* updates
    #     if TaskAttentionMouse.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         TaskAttentionMouse.frameNStart = frameN  # exact frame index
    #         TaskAttentionMouse.tStart = t  # local t and not account for scr refresh
    #         TaskAttentionMouse.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(TaskAttentionMouse, 'tStartRefresh')  # time at next scr refresh
    #         TaskAttentionMouse.status = STARTED
    #         TaskAttentionMouse.mouseClock.reset()
    #         prevButtonState = TaskAttentionMouse.getPressed()  # if button is down already this ISN'T a new click
    #     if TaskAttentionMouse.status == STARTED:  # only update if started and not finished!
    #         if tThisFlipGlobal > TaskAttentionMouse.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             TaskAttentionMouse.tStop = t  # not accounting for scr refresh
    #             TaskAttentionMouse.frameNStop = frameN  # exact frame index
    #             TaskAttentionMouse.status = FINISHED
    #         buttons = TaskAttentionMouse.getPressed()
    #         if buttons != prevButtonState:  # button state changed?
    #             prevButtonState = buttons
    #             if sum(buttons) > 0:  # state changed to a new click
    #                 # abort routine on response
    #                 continueRoutine = False

    #     # *TaskAttentionRating* updates
    #     if TaskAttentionRating.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         TaskAttentionRating.frameNStart = frameN  # exact frame index
    #         TaskAttentionRating.tStart = t  # local t and not account for scr refresh
    #         TaskAttentionRating.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.callOnFlip(print, "Show TaskAttention Rating")
    #         if biopac_exists == 1:
    #             win.callOnFlip(biopac.setData, biopac, 0)
    #             win.callOnFlip(biopac.setData, biopac, taskattention_rating)
    #         win.timeOnFlip(TaskAttentionRating, 'tStartRefresh')  # time at next scr refresh
    #         TaskAttentionRating.setAutoDraw(True)
    #     if TaskAttentionRating.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > TaskAttentionRating.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             TaskAttentionRating.tStop = t  # not accounting for scr refresh
    #             TaskAttentionRating.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(TaskAttentionRating, 'tStopRefresh')  # time at next scr refresh
    #             TaskAttentionRating.setAutoDraw(False)
        
    #     # *TaskAttentionBlackTriangle* updates
    #     if TaskAttentionBlackTriangle.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         TaskAttentionBlackTriangle.frameNStart = frameN  # exact frame index
    #         TaskAttentionBlackTriangle.tStart = t  # local t and not account for scr refresh
    #         TaskAttentionBlackTriangle.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(TaskAttentionBlackTriangle, 'tStartRefresh')  # time at next scr refresh
    #         TaskAttentionBlackTriangle.setAutoDraw(True)
    #     if TaskAttentionBlackTriangle.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > TaskAttentionBlackTriangle.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             TaskAttentionBlackTriangle.tStop = t  # not accounting for scr refresh
    #             TaskAttentionBlackTriangle.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(TaskAttentionBlackTriangle, 'tStopRefresh')  # time at next scr refresh
    #             TaskAttentionBlackTriangle.setAutoDraw(False)

    #     # *TaskAttentionAnchors* updates
    #     if TaskAttentionAnchors.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         TaskAttentionAnchors.frameNStart = frameN  # exact frame index
    #         TaskAttentionAnchors.tStart = t  # local t and not account for scr refresh
    #         TaskAttentionAnchors.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(TaskAttentionAnchors, 'tStartRefresh')  # time at next scr refresh
    #         TaskAttentionAnchors.setAutoDraw(True)
    #     if TaskAttentionAnchors.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > TaskAttentionAnchors.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             TaskAttentionAnchors.tStop = t  # not accounting for scr refresh
    #             TaskAttentionAnchors.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(TaskAttentionAnchors, 'tStopRefresh')  # time at next scr refresh
    #             TaskAttentionAnchors.setAutoDraw(False)
        
    #     # *TaskAttentionPrompt* updates
    #     if TaskAttentionPrompt.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         TaskAttentionPrompt.frameNStart = frameN  # exact frame index
    #         TaskAttentionPrompt.tStart = t  # local t and not account for scr refresh
    #         TaskAttentionPrompt.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(TaskAttentionPrompt, 'tStartRefresh')  # time at next scr refresh
    #         TaskAttentionPrompt.setAutoDraw(True)
    #     if TaskAttentionPrompt.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > TaskAttentionPrompt.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             TaskAttentionPrompt.tStop = t  # not accounting for scr refresh
    #             TaskAttentionPrompt.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(TaskAttentionPrompt, 'tStopRefresh')  # time at next scr refresh
    #             TaskAttentionPrompt.setAutoDraw(False)
    #     # Autoresponder
    #     if t >= thisSimKey.rt and autorespond == 1:
    #         sliderValue = random.randint(-100,100)
    #         continueRoutine = False

    #     # check for quit (typically the Esc key)
    #     if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
    #         core.quit()
        
    #     # check if all components have finished
    #     if not continueRoutine:  # a component has requested a forced-end of Routine
    #         break
    #     continueRoutine = False  # will revert to True if at least one component still running
    #     for thisComponent in TaskAttentionRatingComponents:
    #         if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
    #             continueRoutine = True
    #             break  # at least one component has not yet finished
        
    #     # refresh the screen
    #     if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
    #         win.flip()

    # # -------Ending Routine "TaskAttentionRating"-------
    # print("CueOff Channel " + str(taskattention_rating))
    # for thisComponent in TaskAttentionRatingComponents:
    #     if hasattr(thisComponent, "setAutoDraw"):
    #         thisComponent.setAutoDraw(False)
    # # store data for thisExp (ExperimentHandler)
    # thisExp.addData('TaskAttentionRating.response', sliderValue)
    # thisExp.addData('TaskAttentionRating.rt', timeNow - TaskAttentionRating.tStart)
    # thisExp.nextEntry()
    # thisExp.addData('TaskAttentionRating.started', TaskAttentionRating.tStart)
    # thisExp.addData('TaskAttentionRating.stopped', TaskAttentionRating.tStop)
    # medmap_bids.append(["TaskAttention Rating:", sliderValue])
    # # the Routine "TaskAttentionRating" was not non-slip safe, so reset the non-slip timer
    # routineTimer.reset()


    medmap_bids.append(showBipolarScale("BoredomRating", BoredomText, ratingTime, biopacCode=boredom_rating))
    ############ ASK Boredom #######################################
    # # ------Prepare to start Routine "BoredomRating"-------
    # continueRoutine = True
    # routineTimer.add(ratingTime)
    # # update component parameters for each repeat
    # # BoredomRating.reset()
    # BoredomMouse = event.Mouse(win=win, visible=False) # Re-initialize BoredomMouse
    # BoredomMouse.setPos((0,0))
    # timeAtLastInterval = 0
    # mouseX = 0
    # oldMouseX = 0
    # BoredomRating.width = abs(sliderMin)
    # BoredomRating.pos = [sliderMin/2, -.1]

    # # keep track of which components have finished
    # BoredomRatingComponents = [BoredomMouse, BoredomRating, BoredomBlackTriangle, BoredomAnchors, BoredomPrompt]
    # for thisComponent in BoredomRatingComponents:
    #     thisComponent.tStart = None
    #     thisComponent.tStop = None
    #     thisComponent.tStartRefresh = None
    #     thisComponent.tStopRefresh = None
    #     if hasattr(thisComponent, 'status'):
    #         thisComponent.status = NOT_STARTED
    # # reset timers
    # t = 0
    # _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    # BoredomRatingClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    # frameN = -1

    # # -------Run Routine "BoredomRating"-------
    # while continueRoutine:
    #     # get current time
    #     t = BoredomRatingClock.getTime()
    #     tThisFlip = win.getFutureFlipTime(clock=BoredomRatingClock)
    #     tThisFlipGlobal = win.getFutureFlipTime(clock=None)
    #     frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    #     # update/draw components on each frame

    #     timeNow = globalClock.getTime()
    #     if (timeNow - timeAtLastInterval) > TIME_INTERVAL:
    #         mouseRel=BoredomMouse.getRel()
    #         mouseX=oldMouseX + mouseRel[0]
    #     BoredomRating.pos = ((sliderMin + mouseX)/2,0)
    #     BoredomRating.width = abs((mouseX-sliderMin))
    #     if mouseX > sliderMax:
    #         mouseX = sliderMax
    #     if mouseX < sliderMin:
    #         mouseX = sliderMin
    #     timeAtLastInterval = timeNow
    #     oldMouseX=mouseX
    #     sliderValue = (mouseX - sliderMin) / (sliderMax - sliderMin) * 100

    #     # *BoredomMouse* updates
    #     if BoredomMouse.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         BoredomMouse.frameNStart = frameN  # exact frame index
    #         BoredomMouse.tStart = t  # local t and not account for scr refresh
    #         BoredomMouse.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(BoredomMouse, 'tStartRefresh')  # time at next scr refresh
    #         BoredomMouse.status = STARTED
    #         BoredomMouse.mouseClock.reset()
    #         prevButtonState = BoredomMouse.getPressed()  # if button is down already this ISN'T a new click
    #     if BoredomMouse.status == STARTED:  # only update if started and not finished!
    #         if tThisFlipGlobal > BoredomMouse.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             BoredomMouse.tStop = t  # not accounting for scr refresh
    #             BoredomMouse.frameNStop = frameN  # exact frame index
    #             BoredomMouse.status = FINISHED
    #         buttons = BoredomMouse.getPressed()
    #         if buttons != prevButtonState:  # button state changed?
    #             prevButtonState = buttons
    #             if sum(buttons) > 0:  # state changed to a new click
    #                 # abort routine on response
    #                 continueRoutine = False

    #     # *BoredomRating* updates
    #     if BoredomRating.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         BoredomRating.frameNStart = frameN  # exact frame index
    #         BoredomRating.tStart = t  # local t and not account for scr refresh
    #         BoredomRating.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.callOnFlip(print, "Show Boredom Rating")
    #         if biopac_exists == 1:
    #             win.callOnFlip(biopac.setData, biopac, 0)
    #             win.callOnFlip(biopac.setData, biopac, boredom_rating)
    #         win.timeOnFlip(BoredomRating, 'tStartRefresh')  # time at next scr refresh
    #         BoredomRating.setAutoDraw(True)
    #     if BoredomRating.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > BoredomRating.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             BoredomRating.tStop = t  # not accounting for scr refresh
    #             BoredomRating.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(BoredomRating, 'tStopRefresh')  # time at next scr refresh
    #             BoredomRating.setAutoDraw(False)
        
    #     # *BoredomBlackTriangle* updates
    #     if BoredomBlackTriangle.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         BoredomBlackTriangle.frameNStart = frameN  # exact frame index
    #         BoredomBlackTriangle.tStart = t  # local t and not account for scr refresh
    #         BoredomBlackTriangle.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(BoredomBlackTriangle, 'tStartRefresh')  # time at next scr refresh
    #         BoredomBlackTriangle.setAutoDraw(True)
    #     if BoredomBlackTriangle.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > BoredomBlackTriangle.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             BoredomBlackTriangle.tStop = t  # not accounting for scr refresh
    #             BoredomBlackTriangle.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(BoredomBlackTriangle, 'tStopRefresh')  # time at next scr refresh
    #             BoredomBlackTriangle.setAutoDraw(False)

    #     # *BoredomAnchors* updates
    #     if BoredomAnchors.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         BoredomAnchors.frameNStart = frameN  # exact frame index
    #         BoredomAnchors.tStart = t  # local t and not account for scr refresh
    #         BoredomAnchors.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(BoredomAnchors, 'tStartRefresh')  # time at next scr refresh
    #         BoredomAnchors.setAutoDraw(True)
    #     if BoredomAnchors.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > BoredomAnchors.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             BoredomAnchors.tStop = t  # not accounting for scr refresh
    #             BoredomAnchors.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(BoredomAnchors, 'tStopRefresh')  # time at next scr refresh
    #             BoredomAnchors.setAutoDraw(False)
        
    #     # *BoredomPrompt* updates
    #     if BoredomPrompt.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         BoredomPrompt.frameNStart = frameN  # exact frame index
    #         BoredomPrompt.tStart = t  # local t and not account for scr refresh
    #         BoredomPrompt.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(BoredomPrompt, 'tStartRefresh')  # time at next scr refresh
    #         BoredomPrompt.setAutoDraw(True)
    #     if BoredomPrompt.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > BoredomPrompt.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             BoredomPrompt.tStop = t  # not accounting for scr refresh
    #             BoredomPrompt.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(BoredomPrompt, 'tStopRefresh')  # time at next scr refresh
    #             BoredomPrompt.setAutoDraw(False)
    #     # Autoresponder
    #     if t >= thisSimKey.rt and autorespond == 1:
    #         sliderValue = random.randint(-100,100)
    #         continueRoutine = False

    #     # check for quit (typically the Esc key)
    #     if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
    #         core.quit()
        
    #     # check if all components have finished
    #     if not continueRoutine:  # a component has requested a forced-end of Routine
    #         break
    #     continueRoutine = False  # will revert to True if at least one component still running
    #     for thisComponent in BoredomRatingComponents:
    #         if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
    #             continueRoutine = True
    #             break  # at least one component has not yet finished
        
    #     # refresh the screen
    #     if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
    #         win.flip()

    # # -------Ending Routine "BoredomRating"-------
    # print("CueOff Channel " + str(boredom_rating))
    # for thisComponent in BoredomRatingComponents:
    #     if hasattr(thisComponent, "setAutoDraw"):
    #         thisComponent.setAutoDraw(False)
    # # store data for thisExp (ExperimentHandler)
    # thisExp.addData('BoredomRating.response', sliderValue)
    # thisExp.addData('BoredomRating.rt', timeNow - BoredomRating.tStart)
    # thisExp.nextEntry()
    # thisExp.addData('BoredomRating.started', BoredomRating.tStart)
    # thisExp.addData('BoredomRating.stopped', BoredomRating.tStop)
    # medmap_bids.append(["Boredom Rating:", sliderValue])
    # # the Routine "BoredomRating" was not non-slip safe, so reset the non-slip timer
    # routineTimer.reset()


    medmap_bids.append(showBipolarScale("AlertnessRating", AlertnessText, ratingTime, biopacCode=alertness_rating))
    # ############ ASK Sleepy vs. Alert #######################################
    # # ------Prepare to start Routine "AlertnessRating"-------
    # continueRoutine = True
    # routineTimer.add(ratingTime)
    # # update component parameters for each repeat
    # # AlertnessRating.reset()
    # AlertnessMouse = event.Mouse(win=win, visible=False) # Re-initialize AlertnessMouse
    # AlertnessMouse.setPos((0,0))
    # timeAtLastInterval = 0
    # mouseX = 0
    # oldMouseX = 0

    # # keep track of which components have finished
    # AlertnessRatingComponents = [AlertnessMouse, AlertnessRating, AlertnessBlackTriangle, AlertnessAnchors, AlertnessPrompt]
    # for thisComponent in AlertnessRatingComponents:
    #     thisComponent.tStart = None
    #     thisComponent.tStop = None
    #     thisComponent.tStartRefresh = None
    #     thisComponent.tStopRefresh = None
    #     if hasattr(thisComponent, 'status'):
    #         thisComponent.status = NOT_STARTED
    # # reset timers
    # t = 0
    # _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    # AlertnessRatingClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    # frameN = -1

    # # -------Run Routine "AlertnessRating"-------
    # while continueRoutine:
    #     # get current time
    #     t = AlertnessRatingClock.getTime()
    #     tThisFlip = win.getFutureFlipTime(clock=AlertnessRatingClock)
    #     tThisFlipGlobal = win.getFutureFlipTime(clock=None)
    #     frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    #     # update/draw components on each frame

    #     timeNow = globalClock.getTime()
    #     if (timeNow - timeAtLastInterval) > TIME_INTERVAL:
    #         mouseRel=AlertnessMouse.getRel()
    #         mouseX=oldMouseX + mouseRel[0]
    #     AlertnessRating.pos = (mouseX/2,0)
    #     AlertnessRating.width = abs(mouseX)
    #     if mouseX > sliderMax:
    #         mouseX = sliderMax
    #     if mouseX < sliderMin:
    #         mouseX = sliderMin
    #     timeAtLastInterval = timeNow
    #     oldMouseX=mouseX
    #     sliderValue = ((mouseX - sliderMin) / (sliderMax - sliderMin) * 200)-100

    #     # *AlertnessMouse* updates
    #     if AlertnessMouse.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         AlertnessMouse.frameNStart = frameN  # exact frame index
    #         AlertnessMouse.tStart = t  # local t and not account for scr refresh
    #         AlertnessMouse.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(AlertnessMouse, 'tStartRefresh')  # time at next scr refresh
    #         AlertnessMouse.status = STARTED
    #         AlertnessMouse.mouseClock.reset()
    #         prevButtonState = AlertnessMouse.getPressed()  # if button is down already this ISN'T a new click
    #     if AlertnessMouse.status == STARTED:  # only update if started and not finished!
    #         if tThisFlipGlobal > AlertnessMouse.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             AlertnessMouse.tStop = t  # not accounting for scr refresh
    #             AlertnessMouse.frameNStop = frameN  # exact frame index
    #             AlertnessMouse.status = FINISHED
    #         buttons = AlertnessMouse.getPressed()
    #         if buttons != prevButtonState:  # button state changed?
    #             prevButtonState = buttons
    #             if sum(buttons) > 0:  # state changed to a new click
    #                 # abort routine on response
    #                 continueRoutine = False

    #     # *AlertnessRating* updates
    #     if AlertnessRating.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         AlertnessRating.frameNStart = frameN  # exact frame index
    #         AlertnessRating.tStart = t  # local t and not account for scr refresh
    #         AlertnessRating.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.callOnFlip(print, "Show Alertness Rating")
    #         if biopac_exists == 1:
    #             win.callOnFlip(biopac.setData, biopac, 0)
    #             win.callOnFlip(biopac.setData, biopac, alertness_rating)
    #         win.timeOnFlip(AlertnessRating, 'tStartRefresh')  # time at next scr refresh
    #         AlertnessRating.setAutoDraw(True)
    #     if AlertnessRating.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > AlertnessRating.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             AlertnessRating.tStop = t  # not accounting for scr refresh
    #             AlertnessRating.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(AlertnessRating, 'tStopRefresh')  # time at next scr refresh
    #             AlertnessRating.setAutoDraw(False)
        
    #     # *AlertnessBlackTriangle* updates
    #     if AlertnessBlackTriangle.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         AlertnessBlackTriangle.frameNStart = frameN  # exact frame index
    #         AlertnessBlackTriangle.tStart = t  # local t and not account for scr refresh
    #         AlertnessBlackTriangle.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(AlertnessBlackTriangle, 'tStartRefresh')  # time at next scr refresh
    #         AlertnessBlackTriangle.setAutoDraw(True)
    #     if AlertnessBlackTriangle.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > AlertnessBlackTriangle.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             AlertnessBlackTriangle.tStop = t  # not accounting for scr refresh
    #             AlertnessBlackTriangle.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(AlertnessBlackTriangle, 'tStopRefresh')  # time at next scr refresh
    #             AlertnessBlackTriangle.setAutoDraw(False)

    #     # *AlertnessAnchors* updates
    #     if AlertnessAnchors.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         AlertnessAnchors.frameNStart = frameN  # exact frame index
    #         AlertnessAnchors.tStart = t  # local t and not account for scr refresh
    #         AlertnessAnchors.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(AlertnessAnchors, 'tStartRefresh')  # time at next scr refresh
    #         AlertnessAnchors.setAutoDraw(True)
    #     if AlertnessAnchors.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > AlertnessAnchors.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             AlertnessAnchors.tStop = t  # not accounting for scr refresh
    #             AlertnessAnchors.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(AlertnessAnchors, 'tStopRefresh')  # time at next scr refresh
    #             AlertnessAnchors.setAutoDraw(False)
        
    #     # *AlertnessPrompt* updates
    #     if AlertnessPrompt.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         AlertnessPrompt.frameNStart = frameN  # exact frame index
    #         AlertnessPrompt.tStart = t  # local t and not account for scr refresh
    #         AlertnessPrompt.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(AlertnessPrompt, 'tStartRefresh')  # time at next scr refresh
    #         AlertnessPrompt.setAutoDraw(True)
    #     if AlertnessPrompt.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > AlertnessPrompt.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             AlertnessPrompt.tStop = t  # not accounting for scr refresh
    #             AlertnessPrompt.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(AlertnessPrompt, 'tStopRefresh')  # time at next scr refresh
    #             AlertnessPrompt.setAutoDraw(False)
    #     # Autoresponder
    #     if t >= thisSimKey.rt and autorespond == 1:
    #         sliderValue = random.randint(-100,100)
    #         continueRoutine = False

    #     # check for quit (typically the Esc key)
    #     if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
    #         core.quit()
        
    #     # check if all components have finished
    #     if not continueRoutine:  # a component has requested a forced-end of Routine
    #         break
    #     continueRoutine = False  # will revert to True if at least one component still running
    #     for thisComponent in AlertnessRatingComponents:
    #         if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
    #             continueRoutine = True
    #             break  # at least one component has not yet finished
        
    #     # refresh the screen
    #     if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
    #         win.flip()

    # # -------Ending Routine "AlertnessRating"-------
    # print("CueOff Channel " + str(alertness_rating))
    # for thisComponent in AlertnessRatingComponents:
    #     if hasattr(thisComponent, "setAutoDraw"):
    #         thisComponent.setAutoDraw(False)
    # # store data for thisExp (ExperimentHandler)
    # thisExp.addData('AlertnessRating.response', sliderValue)
    # thisExp.addData('AlertnessRating.rt', timeNow - AlertnessRating.tStart)
    # thisExp.nextEntry()
    # thisExp.addData('AlertnessRating.started', AlertnessRating.tStart)
    # thisExp.addData('AlertnessRating.stopped', AlertnessRating.tStop)
    # medmap_bids.append(["Alertness Rating:", sliderValue])
    # # the Routine "AlertnessRating" was not non-slip safe, so reset the non-slip timer
    # routineTimer.reset()


    medmap_bids.append(showBipolarScale("PosThxRating", PosThxText, ratingTime, biopacCode=posthx_rating))
    # ############ ASK thoughts were POSITIVE #######################################
    # # ------Prepare to start Routine "PosThxRating"-------
    # continueRoutine = True
    # routineTimer.add(ratingTime)
    # # update component parameters for each repeat
    # # PosThxRating.reset()
    # PosThxMouse = event.Mouse(win=win, visible=False) # Re-initialize PosThxMouse
    # PosThxMouse.setPos((0,0))
    # timeAtLastInterval = 0
    # mouseX = 0
    # oldMouseX = 0

    # # keep track of which components have finished
    # PosThxRatingComponents = [PosThxMouse, PosThxRating, PosThxBlackTriangle, PosThxAnchors, PosThxPrompt]
    # for thisComponent in PosThxRatingComponents:
    #     thisComponent.tStart = None
    #     thisComponent.tStop = None
    #     thisComponent.tStartRefresh = None
    #     thisComponent.tStopRefresh = None
    #     if hasattr(thisComponent, 'status'):
    #         thisComponent.status = NOT_STARTED
    # # reset timers
    # t = 0
    # _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    # PosThxRatingClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    # frameN = -1

    # # -------Run Routine "PosThxRating"-------
    # while continueRoutine:
    #     # get current time
    #     t = PosThxRatingClock.getTime()
    #     tThisFlip = win.getFutureFlipTime(clock=PosThxRatingClock)
    #     tThisFlipGlobal = win.getFutureFlipTime(clock=None)
    #     frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    #     # update/draw components on each frame

    #     timeNow = globalClock.getTime()
    #     if (timeNow - timeAtLastInterval) > TIME_INTERVAL:
    #         mouseRel=PosThxMouse.getRel()
    #         mouseX=oldMouseX + mouseRel[0]
    #     PosThxRating.pos = (mouseX/2,0)
    #     PosThxRating.width = abs(mouseX)
    #     if mouseX > sliderMax:
    #         mouseX = sliderMax
    #     if mouseX < sliderMin:
    #         mouseX = sliderMin
    #     timeAtLastInterval = timeNow
    #     oldMouseX=mouseX
    #     sliderValue = ((mouseX - sliderMin) / (sliderMax - sliderMin) * 200)-100

    #     # *PosThxMouse* updates
    #     if PosThxMouse.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         PosThxMouse.frameNStart = frameN  # exact frame index
    #         PosThxMouse.tStart = t  # local t and not account for scr refresh
    #         PosThxMouse.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(PosThxMouse, 'tStartRefresh')  # time at next scr refresh
    #         PosThxMouse.status = STARTED
    #         PosThxMouse.mouseClock.reset()
    #         prevButtonState = PosThxMouse.getPressed()  # if button is down already this ISN'T a new click
    #     if PosThxMouse.status == STARTED:  # only update if started and not finished!
    #         if tThisFlipGlobal > PosThxMouse.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             PosThxMouse.tStop = t  # not accounting for scr refresh
    #             PosThxMouse.frameNStop = frameN  # exact frame index
    #             PosThxMouse.status = FINISHED
    #         buttons = PosThxMouse.getPressed()
    #         if buttons != prevButtonState:  # button state changed?
    #             prevButtonState = buttons
    #             if sum(buttons) > 0:  # state changed to a new click
    #                 # abort routine on response
    #                 continueRoutine = False

    #     # *PosThxRating* updates
    #     if PosThxRating.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         PosThxRating.frameNStart = frameN  # exact frame index
    #         PosThxRating.tStart = t  # local t and not account for scr refresh
    #         PosThxRating.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.callOnFlip(print, "Show PosThx Rating")
    #         if biopac_exists == 1:
    #             win.callOnFlip(biopac.setData, biopac, 0)
    #             win.callOnFlip(biopac.setData, biopac, posthx_rating)
    #         win.timeOnFlip(PosThxRating, 'tStartRefresh')  # time at next scr refresh
    #         PosThxRating.setAutoDraw(True)
    #     if PosThxRating.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > PosThxRating.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             PosThxRating.tStop = t  # not accounting for scr refresh
    #             PosThxRating.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(PosThxRating, 'tStopRefresh')  # time at next scr refresh
    #             PosThxRating.setAutoDraw(False)
        
    #     # *PosThxBlackTriangle* updates
    #     if PosThxBlackTriangle.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         PosThxBlackTriangle.frameNStart = frameN  # exact frame index
    #         PosThxBlackTriangle.tStart = t  # local t and not account for scr refresh
    #         PosThxBlackTriangle.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(PosThxBlackTriangle, 'tStartRefresh')  # time at next scr refresh
    #         PosThxBlackTriangle.setAutoDraw(True)
    #     if PosThxBlackTriangle.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > PosThxBlackTriangle.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             PosThxBlackTriangle.tStop = t  # not accounting for scr refresh
    #             PosThxBlackTriangle.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(PosThxBlackTriangle, 'tStopRefresh')  # time at next scr refresh
    #             PosThxBlackTriangle.setAutoDraw(False)

    #     # *PosThxAnchors* updates
    #     if PosThxAnchors.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         PosThxAnchors.frameNStart = frameN  # exact frame index
    #         PosThxAnchors.tStart = t  # local t and not account for scr refresh
    #         PosThxAnchors.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(PosThxAnchors, 'tStartRefresh')  # time at next scr refresh
    #         PosThxAnchors.setAutoDraw(True)
    #     if PosThxAnchors.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > PosThxAnchors.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             PosThxAnchors.tStop = t  # not accounting for scr refresh
    #             PosThxAnchors.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(PosThxAnchors, 'tStopRefresh')  # time at next scr refresh
    #             PosThxAnchors.setAutoDraw(False)
        
    #     # *PosThxPrompt* updates
    #     if PosThxPrompt.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         PosThxPrompt.frameNStart = frameN  # exact frame index
    #         PosThxPrompt.tStart = t  # local t and not account for scr refresh
    #         PosThxPrompt.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(PosThxPrompt, 'tStartRefresh')  # time at next scr refresh
    #         PosThxPrompt.setAutoDraw(True)
    #     if PosThxPrompt.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > PosThxPrompt.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             PosThxPrompt.tStop = t  # not accounting for scr refresh
    #             PosThxPrompt.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(PosThxPrompt, 'tStopRefresh')  # time at next scr refresh
    #             PosThxPrompt.setAutoDraw(False)
    #     # Autoresponder
    #     if t >= thisSimKey.rt and autorespond == 1:
    #         sliderValue = random.randint(-100,100)
    #         continueRoutine = False

    #     # check for quit (typically the Esc key)
    #     if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
    #         core.quit()
        
    #     # check if all components have finished
    #     if not continueRoutine:  # a component has requested a forced-end of Routine
    #         break
    #     continueRoutine = False  # will revert to True if at least one component still running
    #     for thisComponent in PosThxRatingComponents:
    #         if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
    #             continueRoutine = True
    #             break  # at least one component has not yet finished
        
    #     # refresh the screen
    #     if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
    #         win.flip()

    # # -------Ending Routine "PosThxRating"-------
    # print("CueOff Channel " + str(posthx_rating))
    # for thisComponent in PosThxRatingComponents:
    #     if hasattr(thisComponent, "setAutoDraw"):
    #         thisComponent.setAutoDraw(False)
    # # store data for thisExp (ExperimentHandler)
    # thisExp.addData('PosThxRating.response', sliderValue)
    # thisExp.addData('PosThxRating.rt', timeNow - PosThxRating.tStart)
    # thisExp.nextEntry()
    # thisExp.addData('PosThxRating.started', PosThxRating.tStart)
    # thisExp.addData('PosThxRating.stopped', PosThxRating.tStop)
    # medmap_bids.append(["Positive Thoughts Rating:", sliderValue])
    # # the Routine "PosThxRating" was not non-slip safe, so reset the non-slip timer
    # routineTimer.reset()


    medmap_bids.append(showBipolarScale("NegThxRating", NegThxText, ratingTime, biopacCode=negthx_rating))  
    # ############ ASK thoughts were NEGATIVE #######################################
    # # ------Prepare to start Routine "NegThxRating"-------
    # continueRoutine = True
    # routineTimer.add(ratingTime)
    # # update component parameters for each repeat
    # # NegThxRating.reset()
    # NegThxMouse = event.Mouse(win=win, visible=False) # Re-initialize NegThxMouse
    # NegThxMouse.setPos((0,0))
    # timeAtLastInterval = 0
    # mouseX = 0
    # oldMouseX = 0


    # # keep track of which components have finished
    # NegThxRatingComponents = [NegThxMouse, NegThxRating, NegThxBlackTriangle, NegThxAnchors, NegThxPrompt]
    # for thisComponent in NegThxRatingComponents:
    #     thisComponent.tStart = None
    #     thisComponent.tStop = None
    #     thisComponent.tStartRefresh = None
    #     thisComponent.tStopRefresh = None
    #     if hasattr(thisComponent, 'status'):
    #         thisComponent.status = NOT_STARTED
    # # reset timers
    # t = 0
    # _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    # NegThxRatingClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    # frameN = -1

    # # -------Run Routine "NegThxRating"-------
    # while continueRoutine:
    #     # get current time
    #     t = NegThxRatingClock.getTime()
    #     tThisFlip = win.getFutureFlipTime(clock=NegThxRatingClock)
    #     tThisFlipGlobal = win.getFutureFlipTime(clock=None)
    #     frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    #     # update/draw components on each frame

    #     timeNow = globalClock.getTime()
    #     if (timeNow - timeAtLastInterval) > TIME_INTERVAL:
    #         mouseRel=NegThxMouse.getRel()
    #         mouseX=oldMouseX + mouseRel[0]
    #     NegThxRating.pos = (mouseX/2,0)
    #     NegThxRating.width = abs(mouseX)
    #     if mouseX > sliderMax:
    #         mouseX = sliderMax
    #     if mouseX < sliderMin:
    #         mouseX = sliderMin
    #     timeAtLastInterval = timeNow
    #     oldMouseX=mouseX
    #     sliderValue = ((mouseX - sliderMin) / (sliderMax - sliderMin) * 200)-100

    #     # *NegThxMouse* updates
    #     if NegThxMouse.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         NegThxMouse.frameNStart = frameN  # exact frame index
    #         NegThxMouse.tStart = t  # local t and not account for scr refresh
    #         NegThxMouse.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(NegThxMouse, 'tStartRefresh')  # time at next scr refresh
    #         NegThxMouse.status = STARTED
    #         NegThxMouse.mouseClock.reset()
    #         prevButtonState = NegThxMouse.getPressed()  # if button is down already this ISN'T a new click
    #     if NegThxMouse.status == STARTED:  # only update if started and not finished!
    #         if tThisFlipGlobal > NegThxMouse.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             NegThxMouse.tStop = t  # not accounting for scr refresh
    #             NegThxMouse.frameNStop = frameN  # exact frame index
    #             NegThxMouse.status = FINISHED
    #         buttons = NegThxMouse.getPressed()
    #         if buttons != prevButtonState:  # button state changed?
    #             prevButtonState = buttons
    #             if sum(buttons) > 0:  # state changed to a new click
    #                 # abort routine on response
    #                 continueRoutine = False

    #     # *NegThxRating* updates
    #     if NegThxRating.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         NegThxRating.frameNStart = frameN  # exact frame index
    #         NegThxRating.tStart = t  # local t and not account for scr refresh
    #         NegThxRating.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.callOnFlip(print, "Show NegThx Rating")
    #         if biopac_exists == 1:
    #             win.callOnFlip(biopac.setData, biopac, 0)
    #             win.callOnFlip(biopac.setData, biopac, negthx_rating)
    #         win.timeOnFlip(NegThxRating, 'tStartRefresh')  # time at next scr refresh
    #         NegThxRating.setAutoDraw(True)
    #     if NegThxRating.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > NegThxRating.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             NegThxRating.tStop = t  # not accounting for scr refresh
    #             NegThxRating.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(NegThxRating, 'tStopRefresh')  # time at next scr refresh
    #             NegThxRating.setAutoDraw(False)
        
    #     # *NegThxBlackTriangle* updates
    #     if NegThxBlackTriangle.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         NegThxBlackTriangle.frameNStart = frameN  # exact frame index
    #         NegThxBlackTriangle.tStart = t  # local t and not account for scr refresh
    #         NegThxBlackTriangle.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(NegThxBlackTriangle, 'tStartRefresh')  # time at next scr refresh
    #         NegThxBlackTriangle.setAutoDraw(True)
    #     if NegThxBlackTriangle.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > NegThxBlackTriangle.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             NegThxBlackTriangle.tStop = t  # not accounting for scr refresh
    #             NegThxBlackTriangle.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(NegThxBlackTriangle, 'tStopRefresh')  # time at next scr refresh
    #             NegThxBlackTriangle.setAutoDraw(False)

    #     # *NegThxAnchors* updates
    #     if NegThxAnchors.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         NegThxAnchors.frameNStart = frameN  # exact frame index
    #         NegThxAnchors.tStart = t  # local t and not account for scr refresh
    #         NegThxAnchors.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(NegThxAnchors, 'tStartRefresh')  # time at next scr refresh
    #         NegThxAnchors.setAutoDraw(True)
    #     if NegThxAnchors.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > NegThxAnchors.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             NegThxAnchors.tStop = t  # not accounting for scr refresh
    #             NegThxAnchors.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(NegThxAnchors, 'tStopRefresh')  # time at next scr refresh
    #             NegThxAnchors.setAutoDraw(False)
        
    #     # *NegThxPrompt* updates
    #     if NegThxPrompt.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         NegThxPrompt.frameNStart = frameN  # exact frame index
    #         NegThxPrompt.tStart = t  # local t and not account for scr refresh
    #         NegThxPrompt.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(NegThxPrompt, 'tStartRefresh')  # time at next scr refresh
    #         NegThxPrompt.setAutoDraw(True)
    #     if NegThxPrompt.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > NegThxPrompt.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             NegThxPrompt.tStop = t  # not accounting for scr refresh
    #             NegThxPrompt.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(NegThxPrompt, 'tStopRefresh')  # time at next scr refresh
    #             NegThxPrompt.setAutoDraw(False)
    #     # Autoresponder
    #     if t >= thisSimKey.rt and autorespond == 1:
    #         sliderValue = random.randint(-100,100)
    #         continueRoutine = False

    #     # check for quit (typically the Esc key)
    #     if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
    #         core.quit()
        
    #     # check if all components have finished
    #     if not continueRoutine:  # a component has requested a forced-end of Routine
    #         break
    #     continueRoutine = False  # will revert to True if at least one component still running
    #     for thisComponent in NegThxRatingComponents:
    #         if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
    #             continueRoutine = True
    #             break  # at least one component has not yet finished
        
    #     # refresh the screen
    #     if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
    #         win.flip()

    # # -------Ending Routine "NegThxRating"-------
    # print("CueOff Channel " + str(negthx_rating))
    # for thisComponent in NegThxRatingComponents:
    #     if hasattr(thisComponent, "setAutoDraw"):
    #         thisComponent.setAutoDraw(False)
    # # store data for thisExp (ExperimentHandler)
    # thisExp.addData('NegThxRating.response', sliderValue)
    # thisExp.addData('NegThxRating.rt', timeNow - NegThxRating.tStart)
    # thisExp.nextEntry()
    # thisExp.addData('NegThxRating.started', NegThxRating.tStart)
    # thisExp.addData('NegThxRating.stopped', NegThxRating.tStop)
    # medmap_bids.append(["Negative Thoughts Rating:", sliderValue])
    # # the Routine "NegThxRating" was not non-slip safe, so reset the non-slip timer
    # routineTimer.reset()

    medmap_bids.append(showBipolarScale("SelfRating", SelfText, ratingTime, biopacCode=self_rating))
    ############ ASK thoughts were SELF-ORIENTED #######################################
    # # ------Prepare to start Routine "SelfRating"-------
    # continueRoutine = True
    # routineTimer.add(ratingTime)
    # # update component parameters for each repeat
    # # SelfRating.reset()
    # SelfMouse = event.Mouse(win=win, visible=False) # Re-initialize SelfMouse
    # SelfMouse.setPos((0,0))
    # timeAtLastInterval = 0
    # mouseX = 0
    # oldMouseX = 0

    # # keep track of which components have finished
    # SelfRatingComponents = [SelfMouse, SelfRating, SelfBlackTriangle, SelfAnchors, SelfPrompt]
    # for thisComponent in SelfRatingComponents:
    #     thisComponent.tStart = None
    #     thisComponent.tStop = None
    #     thisComponent.tStartRefresh = None
    #     thisComponent.tStopRefresh = None
    #     if hasattr(thisComponent, 'status'):
    #         thisComponent.status = NOT_STARTED
    # # reset timers
    # t = 0
    # _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    # SelfRatingClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    # frameN = -1

    # # -------Run Routine "SelfRating"-------
    # while continueRoutine:
    #     # get current time
    #     t = SelfRatingClock.getTime()
    #     tThisFlip = win.getFutureFlipTime(clock=SelfRatingClock)
    #     tThisFlipGlobal = win.getFutureFlipTime(clock=None)
    #     frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    #     # update/draw components on each frame

    #     timeNow = globalClock.getTime()
    #     if (timeNow - timeAtLastInterval) > TIME_INTERVAL:
    #         mouseRel=SelfMouse.getRel()
    #         mouseX=oldMouseX + mouseRel[0]
    #     SelfRating.pos = (mouseX/2,0)
    #     SelfRating.width = abs(mouseX)
    #     if mouseX > sliderMax:
    #         mouseX = sliderMax
    #     if mouseX < sliderMin:
    #         mouseX = sliderMin
    #     timeAtLastInterval = timeNow
    #     oldMouseX=mouseX
    #     sliderValue = ((mouseX - sliderMin) / (sliderMax - sliderMin) * 200)-100

    #     # *SelfMouse* updates
    #     if SelfMouse.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         SelfMouse.frameNStart = frameN  # exact frame index
    #         SelfMouse.tStart = t  # local t and not account for scr refresh
    #         SelfMouse.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(SelfMouse, 'tStartRefresh')  # time at next scr refresh
    #         SelfMouse.status = STARTED
    #         SelfMouse.mouseClock.reset()
    #         prevButtonState = SelfMouse.getPressed()  # if button is down already this ISN'T a new click
    #     if SelfMouse.status == STARTED:  # only update if started and not finished!
    #         if tThisFlipGlobal > SelfMouse.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             SelfMouse.tStop = t  # not accounting for scr refresh
    #             SelfMouse.frameNStop = frameN  # exact frame index
    #             SelfMouse.status = FINISHED
    #         buttons = SelfMouse.getPressed()
    #         if buttons != prevButtonState:  # button state changed?
    #             prevButtonState = buttons
    #             if sum(buttons) > 0:  # state changed to a new click
    #                 # abort routine on response
    #                 continueRoutine = False

    #     # *SelfRating* updates
    #     if SelfRating.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         SelfRating.frameNStart = frameN  # exact frame index
    #         SelfRating.tStart = t  # local t and not account for scr refresh
    #         SelfRating.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.callOnFlip(print, "Show Self Rating")
    #         if biopac_exists == 1:
    #             win.callOnFlip(biopac.setData, biopac, 0)
    #             win.callOnFlip(biopac.setData, biopac, self_rating)
    #         win.timeOnFlip(SelfRating, 'tStartRefresh')  # time at next scr refresh
    #         SelfRating.setAutoDraw(True)
    #     if SelfRating.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > SelfRating.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             SelfRating.tStop = t  # not accounting for scr refresh
    #             SelfRating.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(SelfRating, 'tStopRefresh')  # time at next scr refresh
    #             SelfRating.setAutoDraw(False)
        
    #     # *SelfBlackTriangle* updates
    #     if SelfBlackTriangle.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         SelfBlackTriangle.frameNStart = frameN  # exact frame index
    #         SelfBlackTriangle.tStart = t  # local t and not account for scr refresh
    #         SelfBlackTriangle.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(SelfBlackTriangle, 'tStartRefresh')  # time at next scr refresh
    #         SelfBlackTriangle.setAutoDraw(True)
    #     if SelfBlackTriangle.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > SelfBlackTriangle.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             SelfBlackTriangle.tStop = t  # not accounting for scr refresh
    #             SelfBlackTriangle.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(SelfBlackTriangle, 'tStopRefresh')  # time at next scr refresh
    #             SelfBlackTriangle.setAutoDraw(False)

    #     # *SelfAnchors* updates
    #     if SelfAnchors.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         SelfAnchors.frameNStart = frameN  # exact frame index
    #         SelfAnchors.tStart = t  # local t and not account for scr refresh
    #         SelfAnchors.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(SelfAnchors, 'tStartRefresh')  # time at next scr refresh
    #         SelfAnchors.setAutoDraw(True)
    #     if SelfAnchors.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > SelfAnchors.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             SelfAnchors.tStop = t  # not accounting for scr refresh
    #             SelfAnchors.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(SelfAnchors, 'tStopRefresh')  # time at next scr refresh
    #             SelfAnchors.setAutoDraw(False)
        
    #     # *SelfPrompt* updates
    #     if SelfPrompt.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         SelfPrompt.frameNStart = frameN  # exact frame index
    #         SelfPrompt.tStart = t  # local t and not account for scr refresh
    #         SelfPrompt.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(SelfPrompt, 'tStartRefresh')  # time at next scr refresh
    #         SelfPrompt.setAutoDraw(True)
    #     if SelfPrompt.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > SelfPrompt.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             SelfPrompt.tStop = t  # not accounting for scr refresh
    #             SelfPrompt.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(SelfPrompt, 'tStopRefresh')  # time at next scr refresh
    #             SelfPrompt.setAutoDraw(False)
    #     # Autoresponder
    #     if t >= thisSimKey.rt and autorespond == 1:
    #         sliderValue = random.randint(-100,100)
    #         continueRoutine = False

    #     # check for quit (typically the Esc key)
    #     if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
    #         core.quit()
        
    #     # check if all components have finished
    #     if not continueRoutine:  # a component has requested a forced-end of Routine
    #         break
    #     continueRoutine = False  # will revert to True if at least one component still running
    #     for thisComponent in SelfRatingComponents:
    #         if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
    #             continueRoutine = True
    #             break  # at least one component has not yet finished
        
    #     # refresh the screen
    #     if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
    #         win.flip()

    # # -------Ending Routine "SelfRating"-------
    # print("CueOff Channel " + str(self_rating))
    # for thisComponent in SelfRatingComponents:
    #     if hasattr(thisComponent, "setAutoDraw"):
    #         thisComponent.setAutoDraw(False)
    # # store data for thisExp (ExperimentHandler)
    # thisExp.addData('SelfRating.response', sliderValue)
    # thisExp.addData('SelfRating.rt', timeNow - SelfRating.tStart)
    # thisExp.nextEntry()
    # thisExp.addData('SelfRating.started', SelfRating.tStart)
    # thisExp.addData('SelfRating.stopped', SelfRating.tStop)
    # medmap_bids.append(["Self-Thoughts Rating:", sliderValue])
    # # the Routine "SelfRating" was not non-slip safe, so reset the non-slip timer
    # routineTimer.reset()

    medmap_bids.append(showBipolarScale("OtherRating", OtherText, ratingTime, biopacCode=other_rating))
    ############ ASK thoughts were Other-Oriented #######################################
    # ------Prepare to start Routine "OtherRating"-------
    # continueRoutine = True
    # routineTimer.add(ratingTime)
    # # update component parameters for each repeat
    # # OtherRating.reset()
    # OtherMouse = event.Mouse(win=win, visible=False) # Re-initialize OtherMouse
    # OtherMouse.setPos((0,0))
    # timeAtLastInterval = 0
    # mouseX = 0
    # oldMouseX = 0

    # # keep track of which components have finished
    # OtherRatingComponents = [OtherMouse, OtherRating, OtherBlackTriangle, OtherAnchors, OtherPrompt]
    # for thisComponent in OtherRatingComponents:
    #     thisComponent.tStart = None
    #     thisComponent.tStop = None
    #     thisComponent.tStartRefresh = None
    #     thisComponent.tStopRefresh = None
    #     if hasattr(thisComponent, 'status'):
    #         thisComponent.status = NOT_STARTED
    # # reset timers
    # t = 0
    # _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    # OtherRatingClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    # frameN = -1

    # # -------Run Routine "OtherRating"-------
    # while continueRoutine:
    #     # get current time
    #     t = OtherRatingClock.getTime()
    #     tThisFlip = win.getFutureFlipTime(clock=OtherRatingClock)
    #     tThisFlipGlobal = win.getFutureFlipTime(clock=None)
    #     frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    #     # update/draw components on each frame

    #     timeNow = globalClock.getTime()
    #     if (timeNow - timeAtLastInterval) > TIME_INTERVAL:
    #         mouseRel=OtherMouse.getRel()
    #         mouseX=oldMouseX + mouseRel[0]
    #     OtherRating.pos = (mouseX/2,0)
    #     OtherRating.width = abs(mouseX)
    #     if mouseX > sliderMax:
    #         mouseX = sliderMax
    #     if mouseX < sliderMin:
    #         mouseX = sliderMin
    #     timeAtLastInterval = timeNow
    #     oldMouseX=mouseX
    #     sliderValue = ((mouseX - sliderMin) / (sliderMax - sliderMin) * 200)-100

    #     # *OtherMouse* updates
    #     if OtherMouse.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         OtherMouse.frameNStart = frameN  # exact frame index
    #         OtherMouse.tStart = t  # local t and not account for scr refresh
    #         OtherMouse.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(OtherMouse, 'tStartRefresh')  # time at next scr refresh
    #         OtherMouse.status = STARTED
    #         OtherMouse.mouseClock.reset()
    #         prevButtonState = OtherMouse.getPressed()  # if button is down already this ISN'T a new click
    #     if OtherMouse.status == STARTED:  # only update if started and not finished!
    #         if tThisFlipGlobal > OtherMouse.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             OtherMouse.tStop = t  # not accounting for scr refresh
    #             OtherMouse.frameNStop = frameN  # exact frame index
    #             OtherMouse.status = FINISHED
    #         buttons = OtherMouse.getPressed()
    #         if buttons != prevButtonState:  # button state changed?
    #             prevButtonState = buttons
    #             if sum(buttons) > 0:  # state changed to a new click
    #                 # abort routine on response
    #                 continueRoutine = False

    #     # *OtherRating* updates
    #     if OtherRating.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         OtherRating.frameNStart = frameN  # exact frame index
    #         OtherRating.tStart = t  # local t and not account for scr refresh
    #         OtherRating.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.callOnFlip(print, "Show Other Rating")
    #         if biopac_exists == 1:
    #             win.callOnFlip(biopac.setData, biopac, 0)
    #             win.callOnFlip(biopac.setData, biopac, other_rating)
    #         win.timeOnFlip(OtherRating, 'tStartRefresh')  # time at next scr refresh
    #         OtherRating.setAutoDraw(True)
    #     if OtherRating.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > OtherRating.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             OtherRating.tStop = t  # not accounting for scr refresh
    #             OtherRating.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(OtherRating, 'tStopRefresh')  # time at next scr refresh
    #             OtherRating.setAutoDraw(False)
        
    #     # *OtherBlackTriangle* updates
    #     if OtherBlackTriangle.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         OtherBlackTriangle.frameNStart = frameN  # exact frame index
    #         OtherBlackTriangle.tStart = t  # local t and not account for scr refresh
    #         OtherBlackTriangle.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(OtherBlackTriangle, 'tStartRefresh')  # time at next scr refresh
    #         OtherBlackTriangle.setAutoDraw(True)
    #     if OtherBlackTriangle.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > OtherBlackTriangle.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             OtherBlackTriangle.tStop = t  # not accounting for scr refresh
    #             OtherBlackTriangle.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(OtherBlackTriangle, 'tStopRefresh')  # time at next scr refresh
    #             OtherBlackTriangle.setAutoDraw(False)

    #     # *OtherAnchors* updates
    #     if OtherAnchors.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         OtherAnchors.frameNStart = frameN  # exact frame index
    #         OtherAnchors.tStart = t  # local t and not account for scr refresh
    #         OtherAnchors.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(OtherAnchors, 'tStartRefresh')  # time at next scr refresh
    #         OtherAnchors.setAutoDraw(True)
    #     if OtherAnchors.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > OtherAnchors.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             OtherAnchors.tStop = t  # not accounting for scr refresh
    #             OtherAnchors.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(OtherAnchors, 'tStopRefresh')  # time at next scr refresh
    #             OtherAnchors.setAutoDraw(False)
        
    #     # *OtherPrompt* updates
    #     if OtherPrompt.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         OtherPrompt.frameNStart = frameN  # exact frame index
    #         OtherPrompt.tStart = t  # local t and not account for scr refresh
    #         OtherPrompt.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(OtherPrompt, 'tStartRefresh')  # time at next scr refresh
    #         OtherPrompt.setAutoDraw(True)
    #     if OtherPrompt.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > OtherPrompt.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             OtherPrompt.tStop = t  # not accounting for scr refresh
    #             OtherPrompt.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(OtherPrompt, 'tStopRefresh')  # time at next scr refresh
    #             OtherPrompt.setAutoDraw(False)
    #     # Autoresponder
    #     if t >= thisSimKey.rt and autorespond == 1:
    #         sliderValue = random.randint(-100,100)
    #         continueRoutine = False

    #     # check for quit (typically the Esc key)
    #     if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
    #         core.quit()
        
    #     # check if all components have finished
    #     if not continueRoutine:  # a component has requested a forced-end of Routine
    #         break
    #     continueRoutine = False  # will revert to True if at least one component still running
    #     for thisComponent in OtherRatingComponents:
    #         if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
    #             continueRoutine = True
    #             break  # at least one component has not yet finished
        
    #     # refresh the screen
    #     if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
    #         win.flip()

    # # -------Ending Routine "OtherRating"-------
    # print("CueOff Channel " + str(other_rating))
    # for thisComponent in OtherRatingComponents:
    #     if hasattr(thisComponent, "setAutoDraw"):
    #         thisComponent.setAutoDraw(False)
    # # store data for thisExp (ExperimentHandler)
    # thisExp.addData('OtherRating.response', sliderValue)
    # thisExp.addData('OtherRating.rt', timeNow - OtherRating.tStart)
    # thisExp.nextEntry()
    # thisExp.addData('OtherRating.started', OtherRating.tStart)
    # thisExp.addData('OtherRating.stopped', OtherRating.tStop)
    # medmap_bids.append(["Other People Thoughts Rating:", sliderValue])
    # # the Routine "OtherRating" was not non-slip safe, so reset the non-slip timer
    # routineTimer.reset()

    medmap_bids.append(showBipolarScale("ImageryRating", ImageryText, ratingTime, biopacCode=posthx_rating))
    ############ ASK thoughts contained Clear and Vivid Mental Imagery #######################################
    # ------Prepare to start Routine "ImageryRating"-------
    # continueRoutine = True
    # routineTimer.add(ratingTime)
    # # update component parameters for each repeat
    # # ImageryRating.reset()
    # ImageryMouse = event.Mouse(win=win, visible=False) # Re-initialize ImageryMouse
    # ImageryMouse.setPos((0,0))
    # timeAtLastInterval = 0
    # mouseX = 0
    # oldMouseX = 0

    # # keep track of which components have finished
    # ImageryRatingComponents = [ImageryMouse, ImageryRating, ImageryBlackTriangle, ImageryAnchors, ImageryPrompt]
    # for thisComponent in ImageryRatingComponents:
    #     thisComponent.tStart = None
    #     thisComponent.tStop = None
    #     thisComponent.tStartRefresh = None
    #     thisComponent.tStopRefresh = None
    #     if hasattr(thisComponent, 'status'):
    #         thisComponent.status = NOT_STARTED
    # # reset timers
    # t = 0
    # _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    # ImageryRatingClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    # frameN = -1

    # # -------Run Routine "ImageryRating"-------
    # while continueRoutine:
    #     # get current time
    #     t = ImageryRatingClock.getTime()
    #     tThisFlip = win.getFutureFlipTime(clock=ImageryRatingClock)
    #     tThisFlipGlobal = win.getFutureFlipTime(clock=None)
    #     frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    #     # update/draw components on each frame

    #     timeNow = globalClock.getTime()
    #     if (timeNow - timeAtLastInterval) > TIME_INTERVAL:
    #         mouseRel=ImageryMouse.getRel()
    #         mouseX=oldMouseX + mouseRel[0]
    #     ImageryRating.pos = (mouseX/2,0)
    #     ImageryRating.width = abs(mouseX)
    #     if mouseX > sliderMax:
    #         mouseX = sliderMax
    #     if mouseX < sliderMin:
    #         mouseX = sliderMin
    #     timeAtLastInterval = timeNow
    #     oldMouseX=mouseX
    #     sliderValue = ((mouseX - sliderMin) / (sliderMax - sliderMin) * 200)-100

    #     # *ImageryMouse* updates
    #     if ImageryMouse.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         ImageryMouse.frameNStart = frameN  # exact frame index
    #         ImageryMouse.tStart = t  # local t and not account for scr refresh
    #         ImageryMouse.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(ImageryMouse, 'tStartRefresh')  # time at next scr refresh
    #         ImageryMouse.status = STARTED
    #         ImageryMouse.mouseClock.reset()
    #         prevButtonState = ImageryMouse.getPressed()  # if button is down already this ISN'T a new click
    #     if ImageryMouse.status == STARTED:  # only update if started and not finished!
    #         if tThisFlipGlobal > ImageryMouse.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             ImageryMouse.tStop = t  # not accounting for scr refresh
    #             ImageryMouse.frameNStop = frameN  # exact frame index
    #             ImageryMouse.status = FINISHED
    #         buttons = ImageryMouse.getPressed()
    #         if buttons != prevButtonState:  # button state changed?
    #             prevButtonState = buttons
    #             if sum(buttons) > 0:  # state changed to a new click
    #                 # abort routine on response
    #                 continueRoutine = False

    #     # *ImageryRating* updates
    #     if ImageryRating.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         ImageryRating.frameNStart = frameN  # exact frame index
    #         ImageryRating.tStart = t  # local t and not account for scr refresh
    #         ImageryRating.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.callOnFlip(print, "Show Imagery Rating")
    #         if biopac_exists == 1:
    #             win.callOnFlip(biopac.setData, biopac, 0)
    #             win.callOnFlip(biopac.setData, biopac, imagery_rating)
    #         win.timeOnFlip(ImageryRating, 'tStartRefresh')  # time at next scr refresh
    #         ImageryRating.setAutoDraw(True)
    #     if ImageryRating.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > ImageryRating.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             ImageryRating.tStop = t  # not accounting for scr refresh
    #             ImageryRating.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(ImageryRating, 'tStopRefresh')  # time at next scr refresh
    #             ImageryRating.setAutoDraw(False)
        
    #     # *ImageryBlackTriangle* updates
    #     if ImageryBlackTriangle.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         ImageryBlackTriangle.frameNStart = frameN  # exact frame index
    #         ImageryBlackTriangle.tStart = t  # local t and not account for scr refresh
    #         ImageryBlackTriangle.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(ImageryBlackTriangle, 'tStartRefresh')  # time at next scr refresh
    #         ImageryBlackTriangle.setAutoDraw(True)
    #     if ImageryBlackTriangle.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > ImageryBlackTriangle.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             ImageryBlackTriangle.tStop = t  # not accounting for scr refresh
    #             ImageryBlackTriangle.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(ImageryBlackTriangle, 'tStopRefresh')  # time at next scr refresh
    #             ImageryBlackTriangle.setAutoDraw(False)

    #     # *ImageryAnchors* updates
    #     if ImageryAnchors.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         ImageryAnchors.frameNStart = frameN  # exact frame index
    #         ImageryAnchors.tStart = t  # local t and not account for scr refresh
    #         ImageryAnchors.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(ImageryAnchors, 'tStartRefresh')  # time at next scr refresh
    #         ImageryAnchors.setAutoDraw(True)
    #     if ImageryAnchors.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > ImageryAnchors.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             ImageryAnchors.tStop = t  # not accounting for scr refresh
    #             ImageryAnchors.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(ImageryAnchors, 'tStopRefresh')  # time at next scr refresh
    #             ImageryAnchors.setAutoDraw(False)
        
    #     # *ImageryPrompt* updates
    #     if ImageryPrompt.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         ImageryPrompt.frameNStart = frameN  # exact frame index
    #         ImageryPrompt.tStart = t  # local t and not account for scr refresh
    #         ImageryPrompt.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(ImageryPrompt, 'tStartRefresh')  # time at next scr refresh
    #         ImageryPrompt.setAutoDraw(True)
    #     if ImageryPrompt.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > ImageryPrompt.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             ImageryPrompt.tStop = t  # not accounting for scr refresh
    #             ImageryPrompt.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(ImageryPrompt, 'tStopRefresh')  # time at next scr refresh
    #             ImageryPrompt.setAutoDraw(False)
    #     # Autoresponder
    #     if t >= thisSimKey.rt and autorespond == 1:
    #         sliderValue = random.randint(-100,100)
    #         continueRoutine = False

    #     # check for quit (typically the Esc key)
    #     if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
    #         core.quit()
        
    #     # check if all components have finished
    #     if not continueRoutine:  # a component has requested a forced-end of Routine
    #         break
    #     continueRoutine = False  # will revert to True if at least one component still running
    #     for thisComponent in ImageryRatingComponents:
    #         if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
    #             continueRoutine = True
    #             break  # at least one component has not yet finished
        
    #     # refresh the screen
    #     if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
    #         win.flip()

    # # -------Ending Routine "ImageryRating"-------
    # print("CueOff Channel " + str(imagery_rating))
    # for thisComponent in ImageryRatingComponents:
    #     if hasattr(thisComponent, "setAutoDraw"):
    #         thisComponent.setAutoDraw(False)
    # # store data for thisExp (ExperimentHandler)
    # thisExp.addData('ImageryRating.response', sliderValue)
    # thisExp.addData('ImageryRating.rt', timeNow - ImageryRating.tStart)
    # thisExp.nextEntry()
    # thisExp.addData('ImageryRating.started', ImageryRating.tStart)
    # thisExp.addData('ImageryRating.stopped', ImageryRating.tStop)
    # medmap_bids.append(["Clear and Vivid Imagery Rating:", sliderValue])
    # # the Routine "ImageryRating" was not non-slip safe, so reset the non-slip timer
    # routineTimer.reset()

    medmap_bids.append(showBipolarScale("PresentRating", PresentText, ratingTime, biopacCode=present_rating))
    ############ ASK thoughts pertained to the immediate PRESENT #######################################
    # ------Prepare to start Routine "PresentRating"-------
    # continueRoutine = True
    # routineTimer.add(ratingTime)
    # # update component parameters for each repeat
    # # PresentRating.reset()
    # PresentMouse = event.Mouse(win=win, visible=False) # Re-initialize PresentMouse
    # PresentMouse.setPos((0,0))
    # timeAtLastInterval = 0
    # mouseX = 0
    # oldMouseX = 0

    # # keep track of which components have finished
    # PresentRatingComponents = [PresentMouse, PresentRating, PresentBlackTriangle, PresentAnchors, PresentPrompt]
    # for thisComponent in PresentRatingComponents:
    #     thisComponent.tStart = None
    #     thisComponent.tStop = None
    #     thisComponent.tStartRefresh = None
    #     thisComponent.tStopRefresh = None
    #     if hasattr(thisComponent, 'status'):
    #         thisComponent.status = NOT_STARTED
    # # reset timers
    # t = 0
    # _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    # PresentRatingClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    # frameN = -1

    # # -------Run Routine "PresentRating"-------
    # while continueRoutine:
    #     # get current time
    #     t = PresentRatingClock.getTime()
    #     tThisFlip = win.getFutureFlipTime(clock=PresentRatingClock)
    #     tThisFlipGlobal = win.getFutureFlipTime(clock=None)
    #     frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    #     # update/draw components on each frame

    #     timeNow = globalClock.getTime()
    #     if (timeNow - timeAtLastInterval) > TIME_INTERVAL:
    #         mouseRel=PresentMouse.getRel()
    #         mouseX=oldMouseX + mouseRel[0]
    #     PresentRating.pos = (mouseX/2,0)
    #     PresentRating.width = abs(mouseX)
    #     if mouseX > sliderMax:
    #         mouseX = sliderMax
    #     if mouseX < sliderMin:
    #         mouseX = sliderMin
    #     timeAtLastInterval = timeNow
    #     oldMouseX=mouseX
    #     sliderValue = ((mouseX - sliderMin) / (sliderMax - sliderMin) * 200)-100

    #     # *PresentMouse* updates
    #     if PresentMouse.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         PresentMouse.frameNStart = frameN  # exact frame index
    #         PresentMouse.tStart = t  # local t and not account for scr refresh
    #         PresentMouse.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(PresentMouse, 'tStartRefresh')  # time at next scr refresh
    #         PresentMouse.status = STARTED
    #         PresentMouse.mouseClock.reset()
    #         prevButtonState = PresentMouse.getPressed()  # if button is down already this ISN'T a new click
    #     if PresentMouse.status == STARTED:  # only update if started and not finished!
    #         if tThisFlipGlobal > PresentMouse.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             PresentMouse.tStop = t  # not accounting for scr refresh
    #             PresentMouse.frameNStop = frameN  # exact frame index
    #             PresentMouse.status = FINISHED
    #         buttons = PresentMouse.getPressed()
    #         if buttons != prevButtonState:  # button state changed?
    #             prevButtonState = buttons
    #             if sum(buttons) > 0:  # state changed to a new click
    #                 # abort routine on response
    #                 continueRoutine = False

    #     # *PresentRating* updates
    #     if PresentRating.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         PresentRating.frameNStart = frameN  # exact frame index
    #         PresentRating.tStart = t  # local t and not account for scr refresh
    #         PresentRating.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.callOnFlip(print, "Show Present Rating")
    #         if biopac_exists == 1:
    #             win.callOnFlip(biopac.setData, biopac, 0)
    #             win.callOnFlip(biopac.setData, biopac, present_rating)
    #         win.timeOnFlip(PresentRating, 'tStartRefresh')  # time at next scr refresh
    #         PresentRating.setAutoDraw(True)
    #     if PresentRating.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > PresentRating.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             PresentRating.tStop = t  # not accounting for scr refresh
    #             PresentRating.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(PresentRating, 'tStopRefresh')  # time at next scr refresh
    #             PresentRating.setAutoDraw(False)
        
    #     # *PresentBlackTriangle* updates
    #     if PresentBlackTriangle.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         PresentBlackTriangle.frameNStart = frameN  # exact frame index
    #         PresentBlackTriangle.tStart = t  # local t and not account for scr refresh
    #         PresentBlackTriangle.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(PresentBlackTriangle, 'tStartRefresh')  # time at next scr refresh
    #         PresentBlackTriangle.setAutoDraw(True)
    #     if PresentBlackTriangle.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > PresentBlackTriangle.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             PresentBlackTriangle.tStop = t  # not accounting for scr refresh
    #             PresentBlackTriangle.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(PresentBlackTriangle, 'tStopRefresh')  # time at next scr refresh
    #             PresentBlackTriangle.setAutoDraw(False)

    #     # *PresentAnchors* updates
    #     if PresentAnchors.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         PresentAnchors.frameNStart = frameN  # exact frame index
    #         PresentAnchors.tStart = t  # local t and not account for scr refresh
    #         PresentAnchors.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(PresentAnchors, 'tStartRefresh')  # time at next scr refresh
    #         PresentAnchors.setAutoDraw(True)
    #     if PresentAnchors.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > PresentAnchors.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             PresentAnchors.tStop = t  # not accounting for scr refresh
    #             PresentAnchors.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(PresentAnchors, 'tStopRefresh')  # time at next scr refresh
    #             PresentAnchors.setAutoDraw(False)
        
    #     # *PresentPrompt* updates
    #     if PresentPrompt.status == NOT_STARTED and t >= 0.0-frameTolerance:
    #         # keep track of start time/frame for later
    #         PresentPrompt.frameNStart = frameN  # exact frame index
    #         PresentPrompt.tStart = t  # local t and not account for scr refresh
    #         PresentPrompt.tStartRefresh = tThisFlipGlobal  # on global time
    #         win.timeOnFlip(PresentPrompt, 'tStartRefresh')  # time at next scr refresh
    #         PresentPrompt.setAutoDraw(True)
    #     if PresentPrompt.status == STARTED:
    #         # is it time to stop? (based on global clock, using actual start)
    #         if tThisFlipGlobal > PresentPrompt.tStartRefresh + ratingTime-frameTolerance:
    #             # keep track of stop time/frame for later
    #             PresentPrompt.tStop = t  # not accounting for scr refresh
    #             PresentPrompt.frameNStop = frameN  # exact frame index
    #             win.timeOnFlip(PresentPrompt, 'tStopRefresh')  # time at next scr refresh
    #             PresentPrompt.setAutoDraw(False)
    #     # Autoresponder
    #     if t >= thisSimKey.rt and autorespond == 1:
    #         sliderValue = random.randint(-100,100)
    #         continueRoutine = False

    #     # check for quit (typically the Esc key)
    #     if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
    #         core.quit()
        
    #     # check if all components have finished
    #     if not continueRoutine:  # a component has requested a forced-end of Routine
    #         break
    #     continueRoutine = False  # will revert to True if at least one component still running
    #     for thisComponent in PresentRatingComponents:
    #         if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
    #             continueRoutine = True
    #             break  # at least one component has not yet finished
        
    #     # refresh the screen
    #     if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
    #         win.flip()

    # # -------Ending Routine "PresentRating"-------
    # print("CueOff Channel " + str(present_rating))
    # for thisComponent in PresentRatingComponents:
    #     if hasattr(thisComponent, "setAutoDraw"):
    #         thisComponent.setAutoDraw(False)
    # # store data for thisExp (ExperimentHandler)
    # thisExp.addData('PresentRating.response', sliderValue)
    # thisExp.addData('PresentRating.rt', timeNow - PresentRating.tStart)
    # thisExp.nextEntry()
    # thisExp.addData('PresentRating.started', PresentRating.tStart)
    # thisExp.addData('PresentRating.stopped', PresentRating.tStop)
    # medmap_bids.append(["Presentness Thoughts Rating:", sliderValue])
    # # the Routine "PresentRating" was not non-slip safe, so reset the non-slip timer
    # routineTimer.reset()

    rating_sound.stop() # Stop the sound so it can be played again.
    ########################## END SELF REPORT RUNS #######################################################

    # After the last Placebo Run, run the Hyperalignment and PinelLocalizer Scans 
    if runs==6: 
        if biopac_exists:
            WASABI_hyperalignment.run(movielist, biopac, biopac_info)
            WASABI_pinelLocalizer.run(biopac, biopac_info)
        else:
            WASABI_hyperalignment.run(movielist)
            WASABI_pinelLocalizer.run()

    """
    17. Save data into .TSV formats and Tying up Loose Ends
    """ 
    medmap_bids_data = pd.DataFrame(medmap_bids, columns = ['onset', 'duration', 'intensity', 'bodySite', 'temperature', 'condition', 'pretrial-jitter'])
    medmap_bids_filename = sub_dir + os.sep + u'sub-SID%06d_ses-%02d_task-%s_acq-%s_run-%s_events.tsv' % (int(expInfo['DBIC Number']), int(expInfo['session']), expName, bodySites[runs].replace(" ", "").lower(), str(runs+1))
    medmap_bids_data.to_csv(medmap_bids_filename, sep="\t")

    """
    18. End of Run, Wait for Experimenter instructions to begin next run
    """   
    message = visual.TextStim(win, text=in_between_run_msg, height=0.05, units='height')
    message.draw()
    win.callOnFlip(print, "Awaiting Experimenter to start next run...\nPress [e] to continue")
    if biopac_exists:
        win.callOnFlip(biopac.setData, biopac,0)
        win.callOnFlip(biopac.setData, biopac,between_run_msg)
    win.flip()
    # Autoresponder
    if autorespond != 1:
        # event.waitKeys(keyList = 'e')
        continueRoutine = True
        event.clearEvents()
        while continueRoutine == True:
            if 'e' in event.getKeys(keyList = 'e'):
                continueRoutine = False

"""
19. Wrap up
"""
if biopac_exists:
    biopac.setData(biopac,0)
    biopac.setData(biopac,end_task)
win.flip()

# these shouldn't be strictly necessary (should auto-save)
thisExp.saveAsWideText(psypy_filename+'.csv', delim='auto')
thisExp.saveAsPickle(psypy_filename)
logging.flush()
# make sure everything is closed down
message = visual.TextStim(win, text=end_msg, height=0.05, units='height')
message.draw()
if biopac_exists == 1:
    biopac.close()  # Close the labjack U3 device to end communication with the Biopac MP150
thisExp.abort()  # or data files will save again on exit
win.close()  # close the window
core.quit()

"""
End of Experiment
"""