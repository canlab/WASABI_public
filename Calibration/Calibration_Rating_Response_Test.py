#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This experiment was created in part using PsychoPy3 Experiment Builder (v2020.2.5),
    on November 10, 2020, at 10:26
If you publish work using this script the most relevant publication is:

    Peirce J, Gray JR, Simpson S, MacAskill M, Höchenberger R, Sogo H, Kastman E, Lindeløv JK. (2019) 
        PsychoPy2: Experiments in behavior made easy Behav Res 51: 195. 
        https://doi.org/10.3758/s13428-018-01193-y

This python script was extensively modified in order to work in the CANLab Behavioral Testing Environment, which includes a
Biopac MP160 Physiological data acquisition device acquired via DB25 parallel port.

Some measures have been taken to minimize experimental latency. PTB/Psychopy code
style is used to initialize all objects prior to screen flipping as much as possible.

Data is written in the default PsychoPy format. 

Trial-by-Trial data is also written in BIDS 1.4.1 format, as separate tab-separated-value (.tsv) files for each subject, (UTF-8 encoding). 
Following this format:
all data headers are in lower snake_case.
missing values are coded None or -99.

1x of these files of name:
sub-XX_task-Calibration_beh.tsv

32x trials per file with the following headers:
onset   duration    body_site   stim_temp   hot_temp    valence_rating  intensity_rating

Averaged data will also be written in pseudo BIDS 1.4.1 format to be fed into the fMRI paradigm (WASABI_Main_fMRI.py) and later to be concatenated with all other participant files into a participants.tsv:
1x file of the name:
sub-XX_task-Calibration_participants.tsv

1x row per file with the following headers (st: stimulation threshold, ht: heat threshold):
participant_id  age sex handedness  leftarm_st rightarm_st  leftleg_st  rightleg_st  leftface_st  rightface_st chest_st    abdomen_st   leftarm_ht rightarm_ht  leftleg_ht  rightleg_ht  leftface_ht  rightface_ht chest_ht    abdomen_ht 

0a. Import Libraries
"""
from __future__ import absolute_import, division, print_function
from builtins import range

from psychopy import locale_setup, prefs, logging, clock  # Psychopy's __init__.py auto-generated commands for Windows are buggy. Quotations and slashes are not well formatted going from Unix-style to Windows. Check this.
from psychopy import sound # Note: You may have to delete 'sounddevice' from the Psychopy audio library in your preferences to avoid a sound-related error message
# from psychopy import event
from psychopy import data
from psychopy import core
from psychopy import visual  # ensure python image library "pillow" is installed, or reinstall it. pip uninstall pillow pip install pillow
from psychopy import event
from psychopy import gui     # ensure PyQt5 is installed. pip install pyqt5

from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)
from psychopy.hardware import keyboard

import numpy as np  # whole numpy lib is available, prepend 'np.'
from numpy import (sin, cos, tan, log, log10, pi, average,
                   sqrt, std, deg2rad, rad2deg, linspace, asarray)
from numpy.random import random, randint, normal, shuffle

import pandas as pd

import os  # handy system and path functions
import sys  # to get file system encoding

from psychopy import parallel

import time as heatTimer
import math
import random

__author__ = "Michael Sun"
__version__ = "1.0.0"
__email__ = "msun@dartmouth.edu"
__status__ = "Production"

""" 
0b. Beta-Testing Togglers
Set to 1 during development, 0 during production
"""
debug = 1
autorespond = 0
biopac_exists = 0
thermode_exists = 0
waitSetting = 0

"""
0c. Prepare Devices: Biopac Psychophysiological Acquisition and Medoc Thermode
"""
# Biopac parameters _________________________________________________
# Relevant Biopac commands: 
#     To send a Biopac marker code to Acqknowledge, replace the FIO number with a value between 0-255(dec), or an 8-bit word(bin) 
#     For instance, the following code would send a value of 15 by setting the first 4 bits to “1": biopac.setData(15)

# biopac channels EDIT
# The channel codes are assigned to mirror the fmri bodymapping sessions
task_ID=255
task_start=7
task_end=8
run_start=9
run_end=10
run_middle=11
trial_start=12
trial_end=13
calibration_intro=14
cue_experimenter=15
leftface_heat=17
rightface_heat=18
leftarm_heat=19
rightarm_heat=20
leftleg_heat=21
rightleg_heat=22
chest_heat=23
abdomen_heat=24
leftface_calib=25
rightface_calib=26
leftarm_calib=27
rightarm_calib=28
leftleg_calib=29
rightleg_calib=30
chest_calib=31
abdomen_calib=32
stim_threshold=33
heat_threshold=34
jitter=41
valence_rating=42
intensity_rating=43
end=46




bodysite_word2calibcode = {"Left Face": leftface_heat, 
                        "Right Face": rightface_heat, 
                        "Left Arm": leftarm_heat, 
                        "Right Arm": rightarm_heat, 
                        "Left Leg": leftleg_heat, 
                        "Right Leg": rightleg_heat, 
                        "Chest": chest_heat,
                        "Abdomen": abdomen_heat 
                        }

bodysite_word2heatcode = {"Left Face": leftface_heat, 
                        "Right Face": rightface_heat, 
                        "Left Arm": leftarm_heat, 
                        "Right Arm": rightarm_heat, 
                        "Left Leg": leftleg_heat, 
                        "Right Leg": rightleg_heat, 
                        "Chest": chest_heat,
                        "Abdomen": abdomen_heat 
                        }

# Biopac MP160 parameters ______________________________________________
# Test if we have a parallel port to toggle Biopac Channels
# This is for the CANLAB Testing Room Setup that uses a DB25 parallel port to interface with the Biopac MP160 and STP100C
try:
    biopac = parallel.ParallelPort(address=0x2FF8) # address for Testing Room C Participant Computer
    biopac.setData(0)  # sets all pins low
    ## Relevant commands:
        # pinNumber = 2  # choose a pin to write to (2-9).
        # parallel.setPin(2, 1)  # sets just this pin to be high
        # biopac.readPin(2)
        # biopac.setPin(2, 1)
        # biopac.setData(byte)
        # biopac.setData(int("8_bit_code", 2))
except TypeError:
    pass
# Medoc TSA2 parameters ______________________________________________
# Initialize the Medoc TSA2 thermal stimulation delivery device
    # Medoc Troubleshooting:
    # To find the computer IP address, check with MMS Arbel's External Control (or Windows ipconfig alternatively)
    # Communication port is always 20121
    # Relevant Medoc commands:
    #     Prepare a program: sendCommand('select_tp', config.START_CALIBRATION)
    #     Trigger a prepared program: sendCommand('trigger')
    #     Pause a program: sendCommand('pause')
    #     Stop a program: sendCommand('stop')

# Import medocControl library, python library custom written for Medoc.
# This will create a ThermodeConfig object called config 
# Make sure medocControl.py is in the same directory 
from medocControl import *
if thermode_exists == 1:
    ip = '192.168.0.114' # Control Center C Room
    # ip = '10.230.133.189' # Home
    # ip = '129.170.31.22' # Wetlab Office
    port = 20121
    config.address = ip
    config.port = port
"""
0d. Custom Classes and Methods
"""
            

class simKeys:
    '''
    an object to simulate key presses
    
    keyList: a list of keys to watch
    name: randomly selected from keyList
    rtRange: [min RT, max RT] where min and max RT are sepecified in ms
        
    '''
    def __init__(self, keyList, rtRange):
        self.name=np.random.choice(keyList)
        self.rt = np.random.choice(np.linspace(rtRange[0], rtRange[1])/1000)

# pick an RT for autoresponding
thisRT=randint(0,5)
thisSimKey=simKeys(keyList=['space'], 
    rtRange=[200,1000])
"""
1. Experimental Parameters
Clocks, paths, etc.
"""
# Create some handy timers
globalClock = core.Clock()  # to track the time since experiment started
routineTimer = core.CountdownTimer()  # to track time remaining of each (non-slip) routine 
# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)

main_dir = _thisDir
stimuli_dir = main_dir + os.sep + "stimuli"
"""
2. Start Experimental Dialog Boxes
"""
# Store info about the experiment session
psychopyVersion = '2020.2.5'
expName = 'Calibration'  # from the Builder filename that created this script
if debug:
    expInfo = {'participant': '99','dob (mm/dd/yyyy)':'06/20/1988', 'gender': 'M', 'handedness': 'r', 'experimenter': 'MS'}
else:
    expInfo = {'participant': '','dob (mm/dd/yyyy)':'', 'gender': '', 'handedness': '', 'experimenter': ''}

dlg = gui.DlgFromDict(dictionary=expInfo, sortKeys=False, title="WASABI Calibration Protocol") # sort_keys flag needs to be changed to sortKeys
if dlg.OK == False:
    core.quit()  # user pressed cancel
expInfo['date'] = data.getDateStr()  # add a simple timestamp
expInfo['expName'] = expName
expInfo['psychopyVersion'] = psychopyVersion

""" 
3. Setup the Window
The CANLab Testing Rooms use a 1920x1080 (16:9) IPS panel with a 250hz refresh rate.
Configure a black window with a 16:9 aspect ratio during development (1280x720) and production (1920x1080)
fullscr = False for testing, True for running participants
"""
if debug == 1: 
    win = visual.Window(
            size=[1280, 720], fullscr=False, screen=1, 
            winType='pyglet', allowGUI=True, allowStencil=False,
            monitor='testMonitor', color=[0,0,0], colorSpace='rgb',
            blendMode='avg', useFBO=True, 
            units='height')
else:
    win = visual.Window(
            size=[1920, 1080], fullscr=True, screen=0, 
            winType='pyglet', allowGUI=True, allowStencil=False,
            monitor='testMonitor', color=[0,0,0], colorSpace='rgb',
            blendMode='avg', useFBO=True, 
            units='height')

# store frame rate of monitor if we can measure it
expInfo['frameRate'] = win.getActualFrameRate()
if expInfo['frameRate'] != None:
    frameDur = 1.0 / round(expInfo['frameRate'])
else:
    frameDur = 1.0 / 60.0  # could not measure, so guess
# Fill expInfo dictionary with None if any field is left blank
expInfo = {k: None if not v else v for k, v in expInfo.items() }

"""
3. Prepare experimental dictionaries for Body-Site Cues and Medoc Tmperature Programs
"""
## Check gender for Chest cue
Chest_imgPath = os.sep.join([stimuli_dir,"cue","ChestF.png"])
if expInfo['gender'] in {"M", "m", "Male", "male"}:
    Chest_imgPath = os.sep.join([stimuli_dir,"cue","ChestM.png"])
elif expInfo['gender'] in {"F", "f", "Female", "female"}:
    Chest_imgPath = os.sep.join([stimuli_dir,"cue","ChestF.png"])

bodysite_word_to_image = {"Left Face": visual.ImageStim(win, image = os.sep.join([stimuli_dir,"cue","LeftFace.png"]), opacity=1, size = (300,300), units="pix"), 
                          "Right Face": visual.ImageStim(win, image = os.sep.join([stimuli_dir,"cue","RightFace.png"]), opacity=1, size = (300,300), units="pix"), 
                          "Left Arm": visual.ImageStim(win, image = os.sep.join([stimuli_dir,"cue","LeftArm.png"]), opacity=1, size = (300,300), units="pix"), 
                          "Right Arm": visual.ImageStim(win, image = os.sep.join([stimuli_dir,"cue","RightArm.png"]), opacity=1, size = (300,300), units="pix"), 
                          "Left Leg": visual.ImageStim(win, image = os.sep.join([stimuli_dir,"cue","LeftLeg.png"]), opacity=1, size = (300,300), units="pix"), 
                          "Right Leg": visual.ImageStim(win, image = os.sep.join([stimuli_dir,"cue","RightLeg.png"]), opacity=1, size = (300,300), units="pix"), 
                          "Chest": visual.ImageStim(win, image = Chest_imgPath, size = (300,300), opacity=1, units="pix"), 
                          "Abdomen": visual.ImageStim(win, image = os.sep.join([stimuli_dir,"cue","Abdomen.png"]), opacity=1, size = (300,300), units="pix") 
                        }
time_to_program = { 0: config.calib_RH_32,
                    1: config.calib_RH_32_5,
                    2: config.calib_RH_33,
                    3: config.calib_RH_33_5,
                    4: config.calib_RH_34,
                    5: config.calib_RH_34_5,
                    6: config.calib_RH_35,
                    7: config.calib_RH_35_5,
                    8: config.calib_RH_36,
                    9: config.calib_RH_36_5,
                    10: config.calib_RH_37,
                    11: config.calib_RH_37_5,
                    12: config.calib_RH_38,
                    13: config.calib_RH_38_5,
                    14: config.calib_RH_39,
                    15: config.calib_RH_39_5,
                    16: config.calib_RH_40,
                    17: config.calib_RH_40_5,
                    18: config.calib_RH_41,
                    19: config.calib_RH_41_5,
                    20: config.calib_RH_42,
                    21: config.calib_RH_42_5,
                    22: config.calib_RH_43,
                    23: config.calib_RH_43_5,
                    24: config.calib_RH_44,
                    25: config.calib_RH_44_5,
                    26: config.calib_RH_45,
                    27: config.calib_RH_45_5,
                    28: config.calib_RH_46,
                    29: config.calib_RH_46_5,
                    30: config.calib_RH_47,
                    31: config.calib_RH_47_5,
                    32: config.calib_RH_48,
                    33: config.calib_RH_48_5,
                    34: config.calib_RH_49
                    }
"""
5. Prepare files to write
"""
sub_dir = os.path.join(_thisDir, 'data', 'sub-%05d' % (int(expInfo['participant'])))
if not os.path.exists(sub_dir):
    os.makedirs(sub_dir)

# Data file name stem = absolute path + name later add .psyexp, .csv, .log, etc
filename = sub_dir + os.sep + u'%05d_%s_%s' % (int(expInfo['participant']), expName, expInfo['date'])
bids_filename = sub_dir + os.sep + u'sub-%05d_task-%s_beh.tsv' % (int(expInfo['participant']), expName)
averaged_filename = sub_dir + os.sep + u'sub-%05d_task-%s_participants.tsv' % (int(expInfo['participant']), expName)

# An ExperimentHandler isn't essential but helps with data saving
thisExp = data.ExperimentHandler(name=expName, version='',
    extraInfo=expInfo, runtimeInfo=None,
    savePickle=True, saveWideText=True,
    dataFileName=filename)
# save a log file for detail verbose info
logFile = logging.LogFile(filename+'.log', level=logging.ERROR)
logging.console.setLevel(logging.WARNING)  # this outputs to the screen, not a file
endExpNow = False  # flag for 'escape' or other condition => quit the exp
frameTolerance = 0.001  # how close to onset before 'same' frame

bids_data = []
averaged_data = []
calibrationOrder = []

"""
6. Initialize Trial-level Components
"""
# create a default keyboard (e.g. to check for escape)
defaultKeyboard = keyboard.Keyboard()
# Initialize components for Routine "Introduction"
IntroductionClock = core.Clock()
Logo = visual.ImageStim(
    win=win, 
    name='Logo', 
    image = os.sep.join([stimuli_dir,"logo.png"]), 
    pos=(0, 0),
    units="pix")
WhiteBack1 = visual.Rect(
    win=win, name='WhiteBack1',
    width=(2, 2)[0], height=(2, 2)[1],
    ori=0, pos=(0, 0),
    lineWidth=1, lineColor=[1,1,1], lineColorSpace='rgb',
    fillColor=[1,1,1], fillColorSpace='rgb',
    opacity=1, depth=0.0, interpolate=True)

# I like the TextBox2 object because you can dynamically add html <b> bold and <i> italics tags.
Welcome = visual.TextBox2(win=win, name='Welcome',
    text='Thermal Sensitivity Calibration\n    Press <b>[Space]</b> to begin.',  # But something is wrong with pyglet, Text alignment doesn't work in Psychopy
    font='Lucida Sans', units='height', letterHeight=0.04,
    pos=(.2, -.4), alignment="center", anchor='center',
    color='black', colorSpace='rgb', opacity=1)
WelcomeConfirm = keyboard.Keyboard()

# Initialize components for Routine "CueExperimenter"
CueExperimenterClock = core.Clock()
WhiteBack2 = visual.Rect(
    win=win, name='WhiteBack2',
    width=(2, 2)[0], height=(2, 2)[1],
    ori=0, pos=(0, 0),
    lineWidth=1, lineColor=[1,1,1], lineColorSpace='rgb',
    fillColor=[1,1,1], fillColorSpace='rgb',
    opacity=1, depth=0.0, interpolate=True)


BodyCueInstructionsText = visual.TextBox2(win=win, name='BodyCueInstructionsText',
    text='     Place the thermode on the indicated body-site and wait\n for the Experimenter to press <b>[Space]</b> when secured.',
    font='Lucida Sans', units='height', letterHeight=0.03,
    pos=(.1, -.3), alignment="center", anchor='center',
    color='black', colorSpace='rgb', opacity=1
    )

ExperimenterConfirm = keyboard.Keyboard()

# Initialize components for Routine "CueParticipant"
CueParticipantClock = core.Clock()
WhiteBack3 = visual.Rect(
    win=win, name='WhiteBack3',
    width=(2, 2)[0], height=(2, 2)[1],
    ori=0, pos=(0, 0),
    lineWidth=1, lineColor=[1,1,1], lineColorSpace='rgb',
    fillColor=[1,1,1], fillColorSpace='rgb',
    opacity=1, depth=0.0, interpolate=True)

PrepareParticipantText = visual.TextBox2(win=win, name='PrepareParticipantText',
    text='Participant: Please press <b>[Space]</b> when you are ready to begin',
    font='Lucida Sans', units='height', letterHeight=0.03,
    pos=(0.05, -.3), alignment="center", anchor='center',
    color='black', colorSpace='rgb', opacity=1)
ParticipantConfirmStart = keyboard.Keyboard()

# Initialize components for Routine "CueStimulationThreshold"
CueStimulationThresholdClock = core.Clock()
WhiteBack4 = visual.Rect(
    win=win, name='WhiteBack4',
    width=(2, 2)[0], height=(2, 2)[1],
    ori=0, pos=(0, 0),
    lineWidth=1, lineColor=[1,1,1], lineColorSpace='rgb',
    fillColor=[1,1,1], fillColorSpace='rgb',
    opacity=1, depth=0.0, interpolate=True)

StimThresholdText = visual.TextBox2(win=win, name='StimThresholdText',
    text='Press <b>[Space]</b> when you begin to feel some sensation in the indicated body-site.',
    font='Lucida Sans', units='height', letterHeight=0.03,
    pos=(0.05, -.3), alignment="center", anchor='center',
    color='black', colorSpace='rgb', opacity=1)
ThresholdSet = keyboard.Keyboard()

# Initialize components for Routine "CueHeatThreshold"
CueHeatThresholdClock = core.Clock()
OKcue1 = visual.TextStim(win=win, name='OKcue1',
    text='OK',
    font='Lucida Sans',
    pos=(0, 0), 
    color=(0,1,0), colorSpace='rgb', opacity=1)
WhiteBack5 = visual.Rect(
    win=win, name='WhiteBack5',
    width=(2, 2)[0], height=(2, 2)[1],
    ori=0, pos=(0, 0),
    lineWidth=1, lineColor=[1,1,1], lineColorSpace='rgb',
    fillColor=[1,1,1], fillColorSpace='rgb',
    opacity=1, depth=0.0, interpolate=True)

HeatSettingText = visual.TextBox2(win=win, name='HeatSettingText',
    text='      Please wait until the heat reaches\nthe highest temperature you can tolerate.\n   Then press <b>[Space]</b> to stop the heat.',
    font='Lucida Sans', units='height', letterHeight=0.03,
    pos=(0.2, -.3), 
    color='black', colorSpace='rgb', opacity=1)
HeatSet = keyboard.Keyboard()

# Initialize components for Routine "CueHeat"
CueHeatClock = core.Clock()

OKcue2 = visual.TextStim(win=win, name='OKcue2',
    text='OK',
    font='Lucida Sans',
    pos=(0, 0), 
    color=(0,1,0), colorSpace='rgb', opacity=1)
WhiteBack6 = visual.Rect(
    win=win, name='WhiteBack6',
    width=(2, 2)[0], height=(2, 2)[1],
    ori=0, pos=(0, 0),
    lineWidth=1, lineColor=[1,1,1], lineColorSpace='rgb',
    fillColor=[1,1,1], fillColorSpace='rgb',
    opacity=1, depth=0.0, interpolate=True)
CalibrationText = visual.TextStim(win=win, name='CalibrationText',
    text='Calibrating…',
    font='Lucida Sans', units='height', height=0.03,
    pos=(0, -0.3), 
    color='black', colorSpace='rgb', opacity=1)

# Initialize components for Routine "ValenceRating"
ValenceRatingClock = core.Clock()

WhiteBack7 = visual.Rect(
    win=win, name='WhiteBack7',
    width=(2, 2)[0], height=(2, 2)[1],
    ori=0, pos=(0, 0),
    lineWidth=1, lineColor=[1,1,1], lineColorSpace='rgb',
    fillColor=[1,1,1], fillColorSpace='rgb',
    opacity=1, depth=0.0, interpolate=True)
ValenceScale = visual.ImageStim(
    win=win, 
    name='ValenceScale', 
    image = os.sep.join([stimuli_dir,"ratingscale","valenceScale.png"]), 
    pos=(0, 0),
    size=((1.45,.42))
    )
ValenceRatingScale = visual.RatingScale(
    win=win, 
    name='ValenceRatingScale', 
    marker='triangle', 
    size=1.0, 
    pos=[0, -0.19], 
    low=-100, 
    high=100, 
    labels=[''], 
    scale='\n\n\n\n\n\nHow pleasant was that stimulation?',
    acceptPreText="Click the line",
    showValue=True,
    textColor='black',
    lineColor='black',
    precision=1,
    stretch=2,
    tickHeight=0,
    markerStart=0,
    leftKeys='1',
    rightKeys='2',
    acceptKeys='space')

# Initialize the text for current valence rating
# Initialize the text for current valence rating
currentValenceRatingText = visual.TextStim(win=win, name='currentValenceRatingText',
                                           text='Current rating: 0',
                                           font='Arial',
                                           pos=(0, -0.4), height=0.05, wrapWidth=None, ori=0,
                                           color='white', colorSpace='rgb', opacity=1,
                                           languageStyle='LTR',
                                           depth=-4.0)


# Initialize components for Routine "IntensityRating"
IntensityRatingClock = core.Clock()

WhiteBack8 = visual.Rect(
    win=win, name='WhiteBack8',
    width=(2, 2)[0], height=(2, 2)[1],
    ori=0, pos=(0, 0),
    lineWidth=1, lineColor=[1,1,1], lineColorSpace='rgb',
    fillColor=[1,1,1], fillColorSpace='rgb',
    opacity=1, depth=0.0, interpolate=True)
IntensityScale = visual.ImageStim(
    win=win, 
    name='IntensityScale', 
    image = os.sep.join([stimuli_dir,"ratingscale","intensityScale.png"]), 
    pos=(0, 0),
    size=((1.35,.35))
    )
IntensityRatingScale = visual.RatingScale(
    win=win, 
    name='IntensityRatingScale', 
    marker='triangle', 
    pos=(0, -0.19),
    size=1.0,
    low=0, 
    high=100, 
    labels=[''], 
    scale='\n\n\n\n\n\nHow intense was that stimulation?',
    acceptPreText="Click the line",
    showValue=True,
    textColor='black',
    lineColor='black',
    precision=1,
    stretch=2,
    tickHeight=0,
    markerStart=0,
    leftKeys='1',
    rightKeys='2',
    acceptKeys='space')

# Initialize the text for current valence rating
currentIntensityRatingText = visual.TextStim(win=win, name='currentIntensityRatingText',
                                           text='Current rating: 0',
                                           font='Arial',
                                           pos=(0, -0.4), height=0.05, wrapWidth=None, ori=0,
                                           color='white', colorSpace='rgb', opacity=1,
                                           languageStyle='LTR',
                                           depth=-4.0)

# Initialize components for Routine "End"
EndClock = core.Clock()
WhiteBack9 = visual.Rect(
    win=win, name='WhiteBack9',
    width=(2, 2)[0], height=(2, 2)[1],
    ori=0, pos=(0, 0),
    lineWidth=1, lineColor=[1,1,1], lineColorSpace='rgb',
    fillColor=[1,1,1], fillColorSpace='rgb',
    opacity=1, depth=0.0, interpolate=True)
EndingImage = visual.ImageStim(
    win=win,
    name='EndingImage', 
    image='stimuli/logo.png', mask=None,
    ori=0, pos=(0, 0), size=(0.5, 0.5),
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=512, interpolate=True, depth=-1.0)
EndingText = visual.TextBox2(win=win, name='EndingText',
    text='            Calibration complete. \n    Thank you for your patience. \nPlease press <b>[Space]</b> to end the task.',
    font='Lucida Sans', units='height', letterHeight=0.03,
    pos=(0.25, -0.4), 
    color='black', colorSpace='rgb', opacity=1)
ConfirmEnd = keyboard.Keyboard()

"""
7. Start Experimental Loops: 
"""
# ------Prepare to start Routine "Introduction"-------
continueRoutine = True
# update component parameters for each repeat
WelcomeConfirm.keys = []
WelcomeConfirm.rt = []
_WelcomeConfirm_allKeys = []

# keep track of which components have finished
IntroductionComponents = [WhiteBack1, Logo, Welcome, WelcomeConfirm]
for thisComponent in IntroductionComponents:
    thisComponent.tStart = None
    thisComponent.tStop = None
    thisComponent.tStartRefresh = None
    thisComponent.tStopRefresh = None
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED
# reset timers
t = 0
_timeToFirstFrame = win.getFutureFlipTime(clock="now")
IntroductionClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
frameN = -1
"""
8a. Calibration Introduction
"""
# -------Run Routine "Introduction"-------
while continueRoutine:
    # get current time
    t = IntroductionClock.getTime()
    tThisFlip = win.getFutureFlipTime(clock=IntroductionClock)
    tThisFlipGlobal = win.getFutureFlipTime(clock=None)
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame

    # *WhiteBack1* updates
    if WhiteBack1.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        # keep track of start time/frame for later
        WhiteBack1.frameNStart = frameN  # exact frame index
        WhiteBack1.tStart = t  # local t and not account for scr refresh
        WhiteBack1.tStartRefresh = tThisFlipGlobal  # on global time
        win.timeOnFlip(WhiteBack1, 'tStartRefresh')  # time at next scr refresh
        WhiteBack1.setAutoDraw(True)
        
        # Cue biopac on
        win.callOnFlip(print, "Cue biopac channel " + str(calibration_intro))
        if biopac_exists == 1:
            win.callOnFlip(biopac.setData, 0)
            win.callOnFlip(biopac.setData, calibration_intro)

    # *Logo* updates
    if Logo.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        # keep track of start time/frame for later
        Logo.frameNStart = frameN  # exact frame index
        Logo.tStart = t  # local t and not account for scr refresh
        Logo.tStartRefresh = tThisFlipGlobal  # on global time
        win.timeOnFlip(WhiteBack1, 'tStartRefresh')  # time at next scr refresh
        Logo.setAutoDraw(True)
    
    # *Welcome* updates
    if Welcome.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        # keep track of start time/frame for later
        Welcome.frameNStart = frameN  # exact frame index
        Welcome.tStart = t  # local t and not account for scr refresh
        Welcome.tStartRefresh = tThisFlipGlobal  # on global time
        win.timeOnFlip(Welcome, 'tStartRefresh')  # time at next scr refresh
        Welcome.setAutoDraw(True)
    
    # *WelcomeConfirm* updates
    waitOnFlip = False
    if WelcomeConfirm.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        # keep track of start time/frame for later
        WelcomeConfirm.frameNStart = frameN  # exact frame index
        WelcomeConfirm.tStart = t  # local t and not account for scr refresh
        WelcomeConfirm.tStartRefresh = tThisFlipGlobal  # on global time
        win.timeOnFlip(WelcomeConfirm, 'tStartRefresh')  # time at next scr refresh
        WelcomeConfirm.status = STARTED
        # keyboard checking is just starting
        waitOnFlip = True
        ## Thermode Commands: Prepare the START_CALIBRATION PROGRAM
        # if thermode_exists == 1:
        #     # At this point, ensure that the Medoc Machine is in External Control mode, waiting for a test program.
        #     win.callOnFlip(poll_for_change, 'IDLE')
        #     win.callOnFlip(sendCommand, 'select_tp', config.START_CALIBRATION)
        win.callOnFlip(WelcomeConfirm.clock.reset)  # t=0 on next screen flip
        win.callOnFlip(WelcomeConfirm.clearEvents, eventType='keyboard')  # clear events on next screen flip
    if WelcomeConfirm.status == STARTED and not waitOnFlip:
        theseKeys = WelcomeConfirm.getKeys(keyList=['space'], waitRelease=False)
        _WelcomeConfirm_allKeys.extend(theseKeys)
        if len(_WelcomeConfirm_allKeys):
            WelcomeConfirm.keys = _WelcomeConfirm_allKeys[-1].name  # just the last key pressed
            WelcomeConfirm.rt = _WelcomeConfirm_allKeys[-1].rt
            # a response ends the routine
            continueRoutine = False
            
    # Autoresponder
    if t >= thisSimKey.rt and autorespond == 1:
        _WelcomeConfirm_allKeys.extend([thisSimKey])    

    # check for quit (typically the Esc key)
    if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
        core.quit()
    
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in IntroductionComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

# -------Ending Routine "Introduction"-------
if biopac_exists == 1:
    biopac.setData(biopac, 0)
for thisComponent in IntroductionComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)
thisExp.addData('WhiteBack1.started', WhiteBack1.tStartRefresh)
thisExp.addData('Logo.started', WhiteBack1.tStartRefresh)
thisExp.addData('Welcome.started', Welcome.tStartRefresh)
# check responses
if WelcomeConfirm.keys in ['', [], None]:  # No response was made
    WelcomeConfirm.keys = None
thisExp.addData('WelcomeConfirm.keys',WelcomeConfirm.keys)
if WelcomeConfirm.keys != None:  # we had a response
    thisExp.addData('WelcomeConfirm.rt', WelcomeConfirm.rt)
thisExp.addData('WelcomeConfirm.started', WelcomeConfirm.tStartRefresh)
thisExp.nextEntry()
# the Routine "Introduction" was not non-slip safe, so reset the non-slip timer
routineTimer.reset()

"""
8b. Main Loop
"""
# set up handler to look after randomisation of conditions etc
trials = data.TrialHandler(nReps=4, method='random', 
    extraInfo=expInfo, originPath=-1,
    trialList=data.importConditions('bodySites.csv'),
    seed=None, name='trials')
thisExp.addLoop(trials)  # add the loop to the experiment
thisTrial = trials.trialList[0]  # so we can initialise stimuli with some values
# abbreviate parameter names if possible (e.g. rgb = thisTrial.rgb)
if thisTrial != None:
    for paramName in thisTrial:
        exec('{} = thisTrial[paramName]'.format(paramName))

for thisTrial in trials:    
    """
    8g. Self-Report Ratings
    """   
    # ------Prepare to start Routine "ValenceRating"-------
    continueRoutine = True
    # update component parameters for each repeat
    ValenceRatingScale.reset()
    # keep track of which components have finished
    ValenceRatingComponents = [WhiteBack7, ValenceScale, ValenceRatingScale, currentValenceRatingText]
    for thisComponent in ValenceRatingComponents:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    ValenceRatingClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    frameN = -1
    
    # -------Run Routine "ValenceRating"-------
    while continueRoutine:
        # get current time
        t = ValenceRatingClock.getTime()
        tThisFlip = win.getFutureFlipTime(clock=ValenceRatingClock)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *WhiteBack7* updates
        if WhiteBack7.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            WhiteBack7.frameNStart = frameN  # exact frame index
            WhiteBack7.tStart = t  # local t and not account for scr refresh
            WhiteBack7.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(WhiteBack7, 'tStartRefresh')  # time at next scr refresh
            WhiteBack7.setAutoDraw(True)

            # Cue biopac on
            win.callOnFlip(print, "Cue biopac channel " + str(valence_rating))
            if biopac_exists == 1:
                win.callOnFlip(biopac.setData, 0)
                win.callOnFlip(biopac.setData, valence_rating)
        
        # *ValenceScale* updates
        if ValenceScale.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            ValenceScale.frameNStart = frameN  # exact frame index
            ValenceScale.tStart = t  # local t and not account for scr refresh
            ValenceScale.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(ValenceScale, 'tStartRefresh')  # time at next scr refresh
            ValenceScale.setAutoDraw(True)
        
        # *ValenceRatingScale* updates
        if ValenceRatingScale.status == NOT_STARTED and t >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            ValenceRatingScale.frameNStart = frameN  # exact frame index
            ValenceRatingScale.tStart = t  # local t and not account for scr refresh
            ValenceRatingScale.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(ValenceRatingScale, 'tStartRefresh')  # time at next scr refresh
            ValenceRatingScale.setAutoDraw(True)
        continueRoutine &= ValenceRatingScale.noResponse  # a response ends the trial
        
        
        # Autoresponder
        if t >= thisSimKey.rt and autorespond == 1:
            if waitSetting:
                core.wait(randint(3,4))
            ValenceRatingScale.noResponse = False

        # check for quit (typically the Esc key)
        if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
            core.quit()
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in ValenceRatingComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # -------Ending Routine "ValenceRating"-------
    if biopac_exists == 1:
        biopac.setData(biopac, 0)
    for thisComponent in ValenceRatingComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    trials.addData('WhiteBack7.started', WhiteBack7.tStartRefresh)
    trials.addData('WhiteBack7.stopped', WhiteBack7.tStopRefresh)
    trials.addData('ValenceScale.started', ValenceScale.tStartRefresh)
    trials.addData('ValenceScale.stopped', ValenceScale.tStopRefresh)
    # store data for trials (TrialHandler)
    trials.addData('ValenceRatingScale.response', ValenceRatingScale.getRating())
    trials.addData('ValenceRatingScale.rt', ValenceRatingScale.getRT())
    trials.addData('ValenceRatingScale.started', ValenceRatingScale.tStart)
    trials.addData('ValenceRatingScale.stopped', ValenceRatingScale.tStop)
    # bids_df.loc[trials.thisN, 'valence_rating'] = ValenceRatingScale.getRating()
    # bids_trialData.append(ValenceRatingScale.getRating())
    # the Routine "ValenceRating" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()

    
    # ------Prepare to start Routine "IntensityRating"-------
    continueRoutine = True
    # update component parameters for each repeat
    IntensityRatingScale.reset()
    # keep track of which components have finished
    IntensityRatingComponents = [WhiteBack8, IntensityScale, IntensityRatingScale, currentIntensityRatingText]
    for thisComponent in IntensityRatingComponents:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    IntensityRatingClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    frameN = -1
    
    # -------Run Routine "IntensityRating"-------
    while continueRoutine:
        # get current time
        t = IntensityRatingClock.getTime()
        tThisFlip = win.getFutureFlipTime(clock=IntensityRatingClock)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *WhiteBack8* updates
        if WhiteBack8.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            WhiteBack8.frameNStart = frameN  # exact frame index
            WhiteBack8.tStart = t  # local t and not account for scr refresh
            WhiteBack8.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(WhiteBack8, 'tStartRefresh')  # time at next scr refresh
            WhiteBack8.setAutoDraw(True)
            # Cue biopac on
            win.callOnFlip(print, "Cue biopac channel " + str(intensity_rating))
            if biopac_exists == 1:
                win.callOnFlip(biopac.setData, 0)
                win.callOnFlip(biopac.setData, intensity_rating)
        # *IntensityScale* updates
        if IntensityScale.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            IntensityScale.frameNStart = frameN  # exact frame index
            IntensityScale.tStart = t  # local t and not account for scr refresh
            IntensityScale.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(IntensityScale, 'tStartRefresh')  # time at next scr refresh
            IntensityScale.setAutoDraw(True)
        # *IntensityRatingScale* updates
        if IntensityRatingScale.status == NOT_STARTED and t >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            IntensityRatingScale.frameNStart = frameN  # exact frame index
            IntensityRatingScale.tStart = t  # local t and not account for scr refresh
            IntensityRatingScale.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(IntensityRatingScale, 'tStartRefresh')  # time at next scr refresh
            IntensityRatingScale.setAutoDraw(True)
        continueRoutine &= IntensityRatingScale.noResponse  # a response ends the trial

        # Autoresponder
        if t >= thisSimKey.rt and autorespond == 1:
            if waitSetting:
                core.wait(randint(3,4))
            IntensityRatingScale.noResponse = False   
        
        # check for quit (typically the Esc key)
        if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
            core.quit()
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in IntensityRatingComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # -------Ending Routine "IntensityRating"-------
    if biopac_exists == 1:
        biopac.setData(biopac, 0)
    for thisComponent in IntensityRatingComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    trials.addData('WhiteBack8.started', WhiteBack8.tStartRefresh)
    trials.addData('WhiteBack8.stopped', WhiteBack8.tStopRefresh)
    trials.addData('IntensityScale.started', IntensityScale.tStartRefresh)
    trials.addData('IntensityScale.stopped', IntensityScale.tStopRefresh)
    # store data for trials (TrialHandler)
    trials.addData('IntensityRatingScale.response', IntensityRatingScale.getRating())
    trials.addData('IntensityRatingScale.rt', IntensityRatingScale.getRT())
    trials.addData('IntensityRatingScale.started', IntensityRatingScale.tStart)
    trials.addData('IntensityRatingScale.stopped', IntensityRatingScale.tStop)
    # bids_df.loc[trials.thisN, 'intensity_rating'] =  IntensityRatingScale.getRating()
    # bids_trialData.append(IntensityRatingScale.getRating())
    # bids_data.append(bids_trialData)

    # the Routine "IntensityRating" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()
    thisExp.nextEntry()
    
# completed 4 repeats of 'trials'
"""
9. Save data into Excel and .CSV formats
""" 
# get names of stimulus parameters
if trials.trialList in ([], [None], None):
    params = []
else:
    params = trials.trialList[0].keys()
# save data for this loop
trials.saveAsExcel(filename + '.xlsx', sheetName='trials',
    stimOut=params,
    dataOut=['n','all_mean','all_std', 'all_raw'])
trials.saveAsText(filename + 'trials.csv', delim=',',
    stimOut=params,
    dataOut=['n','all_mean','all_std', 'all_raw'])
"""
10. Thanking the Participant
""" 
# ------Prepare to start Routine "End"-------
continueRoutine = True
# update component parameters for each repeat
ConfirmEnd.keys = []
ConfirmEnd.rt = []
_ConfirmEnd_allKeys = []
# keep track of which components have finished
EndComponents = [WhiteBack9, EndingImage, EndingText, ConfirmEnd]
for thisComponent in EndComponents:
    thisComponent.tStart = None
    thisComponent.tStop = None
    thisComponent.tStartRefresh = None
    thisComponent.tStopRefresh = None
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED
# reset timers
t = 0
_timeToFirstFrame = win.getFutureFlipTime(clock="now")
EndClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
frameN = -1

# -------Run Routine "End"-------
while continueRoutine:
    # get current time
    t = EndClock.getTime()
    tThisFlip = win.getFutureFlipTime(clock=EndClock)
    tThisFlipGlobal = win.getFutureFlipTime(clock=None)
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame
    
    # *WhiteBack9* updates
    if WhiteBack9.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        # keep track of start time/frame for later
        WhiteBack9.frameNStart = frameN  # exact frame index
        WhiteBack9.tStart = t  # local t and not account for scr refresh
        WhiteBack9.tStartRefresh = tThisFlipGlobal  # on global time
        win.timeOnFlip(WhiteBack9, 'tStartRefresh')  # time at next scr refresh
        WhiteBack9.setAutoDraw(True)
        # Cue biopac on
        win.callOnFlip(print, "Cue biopac channel " + str(end))
        if biopac_exists == 1:
            win.callOnFlip(biopac.setData, 0)
            win.callOnFlip(biopac.setData, end)
            win.callOnFlip(biopac.setData, 0)
    # *EndingImage* updates
    if EndingImage.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        # keep track of start time/frame for later
        EndingImage.frameNStart = frameN  # exact frame index
        EndingImage.tStart = t  # local t and not account for scr refresh
        EndingImage.tStartRefresh = tThisFlipGlobal  # on global time
        win.timeOnFlip(EndingImage, 'tStartRefresh')  # time at next scr refresh
        EndingImage.setAutoDraw(True)
    
    # *EndingText* updates
    if EndingText.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        # keep track of start time/frame for later
        EndingText.frameNStart = frameN  # exact frame index
        EndingText.tStart = t  # local t and not account for scr refresh
        EndingText.tStartRefresh = tThisFlipGlobal  # on global time
        win.timeOnFlip(EndingText, 'tStartRefresh')  # time at next scr refresh
        EndingText.setAutoDraw(True)
    
    # *ConfirmEnd* updates
    waitOnFlip = False
    if ConfirmEnd.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        # keep track of start time/frame for later
        ConfirmEnd.frameNStart = frameN  # exact frame index
        ConfirmEnd.tStart = t  # local t and not account for scr refresh
        ConfirmEnd.tStartRefresh = tThisFlipGlobal  # on global time
        win.timeOnFlip(ConfirmEnd, 'tStartRefresh')  # time at next scr refresh
        ConfirmEnd.status = STARTED
        # keyboard checking is just starting
        waitOnFlip = True
        win.callOnFlip(ConfirmEnd.clock.reset)  # t=0 on next screen flip
        win.callOnFlip(ConfirmEnd.clearEvents, eventType='keyboard')  # clear events on next screen flip
    if ConfirmEnd.status == STARTED and not waitOnFlip:
        theseKeys = ConfirmEnd.getKeys(keyList=['space'], waitRelease=False)
        _ConfirmEnd_allKeys.extend(theseKeys)
        if len(_ConfirmEnd_allKeys):
            ConfirmEnd.keys = _ConfirmEnd_allKeys[-1].name  # just the last key pressed
            ConfirmEnd.rt = _ConfirmEnd_allKeys[-1].rt
            # a response ends the routine
            continueRoutine = False
    
    # check for quit (typically the Esc key)
    if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
        core.quit()
    
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in EndComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

# -------Ending Routine "End"-------
if biopac_exists == 1:
    biopac.setData(biopac, 0)
for thisComponent in EndComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)
thisExp.addData('WhiteBack9.started', WhiteBack9.tStartRefresh)
thisExp.addData('EndingImage.started', EndingImage.tStartRefresh)
thisExp.addData('EndingText.started', EndingText.tStartRefresh)
# check responses
if ConfirmEnd.keys in ['', [], None]:  # No response was made
    ConfirmEnd.keys = None
thisExp.addData('ConfirmEnd.keys',ConfirmEnd.keys)
if ConfirmEnd.keys != None:  # we had a response
    thisExp.addData('ConfirmEnd.rt', ConfirmEnd.rt)
thisExp.addData('ConfirmEnd.started', ConfirmEnd.tStartRefresh)
thisExp.nextEntry()
# the Routine "End" was not non-slip safe, so reset the non-slip timer
routineTimer.reset()

# Flip one final time so any remaining win.callOnFlip() 
# and win.timeOnFlip() tasks get executed before quitting
win.flip()

"""
12. Tying up Loose Ends
""" 

logging.flush()
# make sure everything is closed down
thisExp.abort()  # or data files will save again on exit
win.close()
core.quit()