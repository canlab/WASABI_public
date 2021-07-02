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
e
Some measures have been taken to minimize experimental latency. PTB/Psychopy style is used to initialize all objects prior to screen flipping as much as possible.
    
Data is written in BIDS 1.4.1 format, as separate tab-separated-value (.tsv) files for each run per subject, (UTF-8 encoding). 
Following this format:
all data headers are in lower snake_case.

The paradigm will generate 8x of these files of name:
sub-XXXX_task-Nback_run-X_events.tsv

42x trials per file with the following
headers:
onset   duration    trial_type  body_site

Troubleshooting Tips:
If you get window-related errors, make sure to downgrade pyglet to 1.4.1:
pip uninstall pyglet
pip install pyglet==1.4.1

0a. Import Libraries
"""

from __future__ import absolute_import, division

from psychopy import locale_setup
from psychopy import prefs
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

__author__ = "Michael Sun"
__version__ = "1.0.0"
__email__ = "msun@dartmouth.edu"
__status__ = "Production"

""" 
0b. Beta-Testing Togglers
Set to 1 during development, 0 during production
"""
debug = 0
autorespond = 0
# Device togglers
biopac_exists = 1

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

# pick an RT
thisRT=randint(0,5)
thisSimKey=simKeys(keyList=['space'], 
    rtRange=[200,1000])
"""
0c. Prepare Devices: Biopac Psychophysiological Acquisition
"""  
# Biopac parameters _________________________________________________
# Relevant Biopac commands: 
#     To send a Biopac marker code to Acqknowledge, replace the FIO number with a value between 0-255(dec), or an 8-bit word(bin) 
#     For instance, the following code would send a value of 15 by setting the first 4 bits to “1": biopac.getFeedback(u3.PortStateWrite(State = [15, 0, 0]))
#     Toggling each of the FIO 8 channels directly: biopac.setFIOState(fioNum = 0:7, state=1)
#     Another command that may work: biopac.setData(byte)

# biopac channels EDIT
task_ID=3
intro=46
rest_t1=47
nback_instructions=48
nback_fixation=49
nback_trial_start=50
second_run=51
nback_hit=52
nback_comiss=53
end_task = 54

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
"""
1. Experimental Parameters
Clocks, paths, etc.
"""
# Clocks
globalClock = core.Clock()  # to track the time since experiment started
routineTimer = core.CountdownTimer()  # to track time remaining of each (non-slip) routine 
# Paths
# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)
main_dir = _thisDir

calibration_dir = os.path.join(os.path.dirname(os.path.abspath(__file__), os.path.pardir, 'Calibration')
"""
2. Start Experimental Dialog Boxes
"""
# Upload participant file: Browse for file
# Store info about the experiment session
psychopyVersion = '2020.2.10'
expName = 'WASABI distractmap'  # from the Builder filename that created this script
if debug == 1:
    expInfo = {
    'subject number': '99', 
    'gender': 'm',
    'session': '99',
    'handedness': 'r', 
    'scanner': 'MS'
    }
else:
    expInfo = {
    'subject number': '', 
    'gender': '',
    'session': '',
    'handedness': '', 
    'scanner': '' 
    }

## Limit the entries of this to hot temperatures (32-49 degrees in half-degree-steps)
participant_settingsHeat = {
    'Left Face': [32,32.5,33,33.5,34,34.5,35,35.5,36,36.5,37,37.5,38,38.5,39,39.5,40,40.5,41,41.5,42,42.5,43,43.5,44,44.5,45,45.5,46,46.5,47,47.5,48,48.5,49],    # Calibrated Temp for left face
    'Right Face': [32,32.5,33,33.5,34,34.5,35,35.5,36,36.5,37,37.5,38,38.5,39,39.5,40,40.5,41,41.5,42,42.5,43,43.5,44,44.5,45,45.5,46,46.5,47,47.5,48,48.5,49],   # Calibrated Temp for right face
    'Left Arm': [32,32.5,33,33.5,34,34.5,35,35.5,36,36.5,37,37.5,38,38.5,39,39.5,40,40.5,41,41.5,42,42.5,43,43.5,44,44.5,45,45.5,46,46.5,47,47.5,48,48.5,49],     # Calibrated Temp for left arm
    'Right Arm': [32,32.5,33,33.5,34,34.5,35,35.5,36,36.5,37,37.5,38,38.5,39,39.5,40,40.5,41,41.5,42,42.5,43,43.5,44,44.5,45,45.5,46,46.5,47,47.5,48,48.5,49],    # Calibrated Temp for right arm
    'Left Leg': [32,32.5,33,33.5,34,34.5,35,35.5,36,36.5,37,37.5,38,38.5,39,39.5,40,40.5,41,41.5,42,42.5,43,43.5,44,44.5,45,45.5,46,46.5,47,47.5,48,48.5,49],     # Calibrated Temp for left leg
    'Right Leg': [32,32.5,33,33.5,34,34.5,35,35.5,36,36.5,37,37.5,38,38.5,39,39.5,40,40.5,41,41.5,42,42.5,43,43.5,44,44.5,45,45.5,46,46.5,47,47.5,48,48.5,49],    # Calibrated Temp for right leg
    'Chest': [32,32.5,33,33.5,34,34.5,35,35.5,36,36.5,37,37.5,38,38.5,39,39.5,40,40.5,41,41.5,42,42.5,43,43.5,44,44.5,45,45.5,46,46.5,47,47.5,48,48.5,49],        # Calibrated Temp for chest
    'Abdomen': [32,32.5,33,33.5,34,34.5,35,35.5,36,36.5,37,37.5,38,38.5,39,39.5,40,40.5,41,41.5,42,42.5,43,43.5,44,44.5,45,45.5,46,46.5,47,47.5,48,48.5,49]       # Calibrated Temp for abdomen
    }
## Limit the entries of this to hot temperatures (32-49 degrees in half-degree-steps)
participant_settingsWarm = {
    'Left Face': [32,32.5,33,33.5,34,34.5,35,35.5,36,36.5,37,37.5,38,38.5,39,39.5,40,40.5,41,41.5,42,42.5,43,43.5,44,44.5,45,45.5,46,46.5,47,47.5,48,48.5,49],     # Calibrated Temp for left face
    'Right Face': [32,32.5,33,33.5,34,34.5,35,35.5,36,36.5,37,37.5,38,38.5,39,39.5,40,40.5,41,41.5,42,42.5,43,43.5,44,44.5,45,45.5,46,46.5,47,47.5,48,48.5,49],    # Calibrated Temp for right face
    'Left Arm': [32,32.5,33,33.5,34,34.5,35,35.5,36,36.5,37,37.5,38,38.5,39,39.5,40,40.5,41,41.5,42,42.5,43,43.5,44,44.5,45,45.5,46,46.5,47,47.5,48,48.5,49],      # Calibrated Temp for left arm
    'Right Arm': [32,32.5,33,33.5,34,34.5,35,35.5,36,36.5,37,37.5,38,38.5,39,39.5,40,40.5,41,41.5,42,42.5,43,43.5,44,44.5,45,45.5,46,46.5,47,47.5,48,48.5,49],     # Calibrated Temp for right arm
    'Left Leg': [32,32.5,33,33.5,34,34.5,35,35.5,36,36.5,37,37.5,38,38.5,39,39.5,40,40.5,41,41.5,42,42.5,43,43.5,44,44.5,45,45.5,46,46.5,47,47.5,48,48.5,49],      # Calibrated Temp for left leg
    'Right Leg': [32,32.5,33,33.5,34,34.5,35,35.5,36,36.5,37,37.5,38,38.5,39,39.5,40,40.5,41,41.5,42,42.5,43,43.5,44,44.5,45,45.5,46,46.5,47,47.5,48,48.5,49],     # Calibrated Temp for right leg
    'Chest': [32,32.5,33,33.5,34,34.5,35,35.5,36,36.5,37,37.5,38,38.5,39,39.5,40,40.5,41,41.5,42,42.5,43,43.5,44,44.5,45,45.5,46,46.5,47,47.5,48,48.5,49],         # Calibrated Temp for chest
    'Abdomen': [32,32.5,33,33.5,34,34.5,35,35.5,36,36.5,37,37.5,38,38.5,39,39.5,40,40.5,41,41.5,42,42.5,43,43.5,44,44.5,45,45.5,46,46.5,47,47.5,48,48.5,49]       # Calibrated Temp for abdomen
    }

# Load the subject's calibration file and ensure that it is valid
if debug==1:
    expInfo = {
        'subject number': '999', 
        'gender': 'm',
        'bodymap first- or second-half (1 or 2)': '2',
        'session': '99',
        'handedness': 'r', 
        'scanner': 'TEST'
    }
    participant_settingsHeat = {
        'Left Face': 46,
        'Right Face': 46,
        'Left Arm': 46,
        'Right Arm': 46,
        'Left Leg': 46,
        'Right Leg': 46,
        'Chest': 46,
        'Abdomen': 46
    }
    participant_settingsWarm = {
        'Left Face': 40,
        'Right Face': 40,
        'Left Arm': 40,
        'Right Arm': 40,
        'Left Leg': 40,
        'Right Leg': 40,
        'Chest': 40,
        'Abdomen': 40
    }
else:
    dlg1 = gui.fileOpenDlg(tryFilePath=calibration_dir, tryFileName="", prompt="Select participant calibration file (*_task-Calibration_participants.tsv)", allowed="Calibration files (*.tsv)")
    if dlg1!=None:
        if "_task-Calibration_participants.tsv" in dlg1[0]:
            # Read in participant info csv and convert to a python dictionary
            a = pd.read_csv(dlg1[0], delimiter='\t', index_col=0, header=0, squeeze=True)
            if a.shape == (1,39):
                participant_settingsHeat = {}
                participant_settingsWarm = {}
                p_info = [dict(zip(a.iloc[i].index.values, a.iloc[i].values)) for i in range(len(a))][0]
                expInfo['subject number'] = p_info['participant_id']
                expInfo['gender'] = p_info['gender']
                expInfo['handedness'] = p_info['handedness']
                bodySites = p_info['calibration_order']
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
                'scanner': ''
                }
                dlg2 = gui.DlgFromDict(title="WASABI Distraction Map Scan", dictionary=expInfo2, sortKeys=False) 
                expInfo['session'] = expInfo2['session']
                expInfo['scanner'] = expInfo2['scanner']
                if dlg2.OK == False:
                    core.quit()  # user pressed cancel
            else:
                errorDlg1 = gui.Dlg(title="Error - invalid file")
                errorDlg1.addText("Selected file is not a valid calibration file. Data is incorrectly formatted. (Wrong dimensions)")
                errorDlg1.show()
                dlg1=None
        else:
            errorDlg2 = gui.Dlg(title="Error - invalid file")
            errorDlg2.addText("Selected file is not a valid calibration file. Name is not formatted sub-XXX_task-Calibration_participant.tsv")
            errorDlg2.show()
            dlg1=None
    if dlg1==None:
        dlg2 = gui.DlgFromDict(title="WASABI Body-Site Scan", dictionary=expInfo, sortKeys=False)
        if dlg2.OK == False:
            core.quit()  # user pressed cancel
        pphDlg = gui.DlgFromDict(participant_settingsHeat, 
                                title='Participant Heat Parameters')
        if pphDlg.OK == False:
            core.quit()
        ppwDlg = gui.DlgFromDict(participant_settingsWarm, 
                                title='Participant Warmth Parameters')
        if ppwDlg.OK == False:
            core.quit()

expInfo['date'] = data.getDateStr()  # add a simple timestamp
expInfo['expName'] = expName
expInfo['psychopyVersion'] = psychopyVersion

""" 
3. Setup the Window
fullscr = False for testing, True for running participants
"""
if debug == 1: 
    win = visual.Window(
            size=[1280, 720], fullscr=False, 
            screen=0,   # Change this to the appropriate display 
            winType='pyglet', allowGUI=True, allowStencil=False,
            monitor='testMonitor', color=[-1.000,-1.000,-1.000], colorSpace='rgb',
            blendMode='avg', useFBO=True, 
            units='height')
else: 
    win = visual.Window(
            size=[1920, 1080], fullscr=True, 
            screen=-1,   # Change this to the appropriate fMRI projector 
            winType='pyglet', allowGUI=True, allowStencil=False,
            monitor='testMonitor', color=[-1.000,-1.000,-1.000], colorSpace='rgb',
            blendMode='avg', useFBO=True, 
            units='height')
# store frame rate of monitor if we can measure it
expInfo['frameRate'] = win.getActualFrameRate()
if expInfo['frameRate'] != None:
    frameDur = 1.0 / round(expInfo['frameRate'])
else:
    frameDur = 1.0 / 60.0  # could not measure, so guess

win.mouseVisible = False # Make the mouse invisible for the remainder of the experiment

"""
4. Prepare files to write
"""
sub_dir = os.path.join(_thisDir, 'data', 'sub-%05d' % (int(expInfo['subject number'])), 'ses-%02d' % (int(expInfo['session'])))
if not os.path.exists(sub_dir):
    os.makedirs(sub_dir)

psypy_filename = os.path.join(sub_dir, '%05d_%s_%s' % (int(expInfo['subject number']), expName, expInfo['date']))

# An ExperimentHandler isn't essential but helps with data saving
thisExp = data.ExperimentHandler(name=expName, version='',
    extraInfo=expInfo, runtimeInfo=None,
    # originPath='C:\\Users\\Michael\\Downloads\\counterbalance-multiple-tasks-demo.py',
    savePickle=True, saveWideText=True,
    dataFileName=psypy_filename)
# save a log file for detail verbose info
logFile = logging.LogFile(psypy_filename+'.log', level=logging.EXP)
logging.console.setLevel(logging.WARNING)  # this outputs to the screen, not a file

endExpNow = False  # flag for 'escape' or other condition => quit the exp
frameTolerance = 0.001  # how close to onset before 'same' frame

# Create python lists to later concatenate or convert into pandas dataframes
nback_bids_trial = []
nback_bids = []
"""
5. Initialize Trial-level Components
"""
# General Instructional Text
start_msg = 'Please wait. \nThe scan will begin shortly. \n Experimenter press [s] to continue.'
in_between_run_msg = 'Thank you.\n Please wait for the next scan to start \n Experimenter press [e] to continue.'
end_msg = 'Please wait for instructions from the experimenter'

# create a default keyboard (e.g. to check for escape)
defaultKeyboard = keyboard.Keyboard()

######################
# N-Back Task Components
######################
# Initialize components for Routine "NbackInstructions"
NbackInstructionsClock = core.Clock()
NbackInstructions = visual.TextStim(win=win, name='Nbackinstructions',
    text='Welcome to the n-back task \nPlease read the following instructions \nvery carefully.\n\n\n\nExperimenter press [Space] to continue.',
    font='Arial',
    pos=(0, 0), units='height', height=0.05, 
    color='white', colorSpace='rgb', opacity=1)
NbackInstructionImg = visual.ImageStim(
    win=win,
    name='NbackInstructionImg', 
    image= 'instruction_stim/1.png', mask=None,
    ori=0, pos=(0, 0), size=(0.3, 0.3),
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=0.0)

NbackInstructionWideImg = visual.ImageStim(
    win=win,
    name='NbackInstructionWideImg', 
    image= 'instruction_stim/3.png', mask=None,
    ori=0, pos=(0, 0), size=(1, 0.3),
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=0.0)

ClickPrompt = visual.TextStim(win=win, name='Nbackinstructions',
    text='Welcome to the n-back task \nPlease read the following instructions \nvery carefully.\n\n\n\nExperimenter press [Space] to continue.',
    font='Arial',
    pos=(0, 0), units='height', height=0.05, 
    color='white', colorSpace='rgb', opacity=1)

NbackStart = keyboard.Keyboard()

# Initialize components for Routine "ButtonTest"
ButtonTestText = "Button/key 1 \nindicates \"YES\", a match.\n\n\n\nButton/key 2\n indicates \"NO\", a mismatch."
box1 = visual.Rect(
    win=win, name='box1',
    width=(0.05, 0.05)[0], height=(0.05, 0.05)[1],
    ori=0, pos=(0, 0.1),
    lineWidth=1,     colorSpace='rgb',  lineColor=[1,1,1], fillColor=[1,1,1],
    opacity=1, depth=0.0, interpolate=True)
box2 = visual.Rect(
    win=win, name='box2',
    width=(0.05, 0.05)[0], height=(0.05, 0.05)[1],
    ori=0, pos=(0, 0),
    lineWidth=1,     colorSpace='rgb',  lineColor=[1,1,1], fillColor=[1,1,1],
    opacity=1, depth=-1.0, interpolate=True)
mouse = event.Mouse(win=win)
x, y = [None, None]
mouse.mouseClock = core.Clock()

FeedBack = visual.TextStim(win=win, name='Feedback',
    text=incorrect_text,
    font='Arial',
    pos=(0, 0), units='height', height=0.05, 
    color='white', colorSpace='rgb', opacity=1)

incorrect_text = "Incorrect!"
noresponse_text = "No Response!"
correct_text = "Correct!"

TryAgainText = "Let's try that again...\n\n\n\n\n\n\n\nExperimenter press [Space] to continue."
PleaseWaitText = "Please wait for the experimenter ..."
PassedText = "Great! Let's move on.\n\n\n\n\n\n\n\nExperimenter press [Space] to continue."

NbackInstructionText8 = "2-back\n\n\nDuring 2-back you will have to indicate whether the current position matches the position matches the position that was presented two trials ago, by either pressing the \"yes\" button (left click) or the \"no\" button (right click).\n\n\nExperimenter press [Space] to see an example."
NbackInstructionText9 = "In this 2-back example you should make a \"yes\" response (left click) on trial 3, since the position is the same as the position on trial 1, while the other trials require a \"no\" (right click) response. "
NbackInstructionText10 = "Now, we will practice some trials so that you can get used to the procedure.\n\n\nAfter each response you'll see whether your response was correct, incorrect, or whether you forgot to respond.\n\n\n\n\n\nGood Luck!"

NbackInstructionText11 = "Now we will start some real trials.\n\n\nDuring the task it is very important that you respond as fast and as accurately as possible.\n\n\nYou should try to respond during the square being presented shortly after. This might be difficult, so it is important that you concentrate!\n\n\n\nDo not forget to respond during every trial."

# Initialize components for Routine "Fixation"
FixationClock = core.Clock()
fixation_2 = visual.TextStim(win=win, name='fixation_2',
    text='+',
    font='Arial',
    pos=(0, 0), height=0.05, wrapWidth=None, ori=0, 
    color='white', colorSpace='rgb', opacity=1, 
    languageStyle='LTR',
    depth=-2.0)

# Initialize components for Routine "N_back_1_trial"
N_back_1_trialsClock = core.Clock()
grid_lines_1 = visual.ImageStim(
    win=win,
    name='grid_lines_1', 
    image='grid.png', mask=None,
    ori=0, pos=(0, 0), size=(0.6, 0.6),
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=0.0)
target_square_1 = visual.Rect(
    win=win, name='target_square_1',
    width=(0.15, 0.15)[0], height=(0.15, 0.15)[1],
    ori=0, pos=[0,0],
    lineWidth=1, lineColor=None, lineColorSpace='rgb',
    fillColor=[1.000,1.000,1.000], fillColorSpace='rgb',
    opacity=1, depth=-1.0, interpolate=True)
fixation_1 = visual.TextStim(win=win, name='fixation_1',
    text='+',
    font='Arial',
    pos=(0, 0), height=0.05, wrapWidth=None, ori=0, 
    color='white', colorSpace='rgb', opacity=1, 
    languageStyle='LTR',
    depth=-2.0)
response_1 = event.Mouse(win=win)
response_1.mouseClock = core.Clock()

# Initialize components for Routine "N_back_2_trials"
N_back_2_trialsClock = core.Clock()
grid_lines_2 = visual.ImageStim(
    win=win,
    name='grid_lines_2', 
    image='grid.png', mask=None,
    ori=0, pos=(0, 0), size=(0.6, 0.6),
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=0.0)
target_square_2 = visual.Rect(
    win=win, name='target_square_2',
    width=(0.15, 0.15)[0], height=(0.15, 0.15)[1],
    ori=0, pos=[0,0],
    lineWidth=1, lineColor=None, lineColorSpace='rgb',
    fillColor=[1.000,1.000,1.000], fillColorSpace='rgb',
    opacity=1, depth=-1.0, interpolate=True)
fixation_3 = visual.TextStim(win=win, name='fixation_3',
    text='+',
    font='Arial',
    pos=(0, 0), height=0.05, wrapWidth=None, ori=0, 
    color='white', colorSpace='rgb', opacity=1, 
    languageStyle='LTR',
    depth=-2.0)
# response_2 = keyboard.Keyboard()
response_2 = event.Mouse(win=win)
response_2.mouseClock = core.Clock()

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
NbackInstructionText1 = "Welcome to the n-back task \nPlease read the following instructions \nvery carefully.\n\n\n\nExperimenter press [Space] to continue."
NbackInstructionText2 = "During the task you will be presented a white square in one of nine positions on a grid. \n\n\n\nDepending on the instruction, your task is to indicate whether the \ncurrent position is the same as either:\nthe position on the last trial\nor the position two trials ago\n\n\nExperimenter press [Space] to continue."
NbackInstructionText3 = "Between each trial, a fixation cross will appear in the middle of the grid. \n\n\n\nYou do not need to respond during this time. \nSimply wait for the next trial.\n\n\nExperimenter press [Space] to continue."
NbackInstructionText4 = "1-back\n\n\nDuring 1-back you will have to indicate whether the current position matches the position that was presented in the last trial, by either pressing the \"yes\" button (left click) or the \"no\" button (right click).\n\n\nExperimenter press [Space] to see an example."

NbackInstructions.setText(NbackInstructionText1)
NbackInstructions.draw()
win.flip()
event.waitKeys(keyList = 'space')
NbackInstructions.setText(NbackInstructionText2)
NbackInstructions.draw()
NbackInstructionImg.setImage('1.png')
win.flip()
event.waitKeys(keyList = 'space')
NbackInstructions.setText(NbackInstructionText3)
NbackInstructions.draw()
NbackInstructionImg.setImage('2.png')
win.flip()
event.waitKeys(keyList = 'space')
NbackInstructionImg.setAutoDraw(False)
NbackInstructions.setText(NbackInstructionText4)
NbackInstructions.draw()
win.flip()
event.waitKeys(keyList = 'space')

"""
6. Button Test
"""
# ------Prepare to start Routine "trial"-------
continueRoutine = True
# update component parameters for each repeat
checkboxes = [box1, box2]
clicked = []
mouseDown = False
for box in checkboxes:
    box.color = "white"
    
# setup some python lists for storing info about the mouse
mouse.x = []
mouse.y = []
mouse.leftButton = []
mouse.midButton = []
mouse.rightButton = []
mouse.time = []
mouse.clicked_name = []
gotValidClick = False  # until a click is received
slider.reset()
# keep track of which components have finished
trialComponents = [box1, box2, mouse]
for thisComponent in trialComponents:
    thisComponent.tStart = None
    thisComponent.tStop = None
    thisComponent.tStartRefresh = None
    thisComponent.tStopRefresh = None
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED
# reset timers
t = 0
_timeToFirstFrame = win.getFutureFlipTime(clock="now")
trialClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
frameN = -1

# -------Run Routine "trial"-------
while continueRoutine:
    # *box1* updates
    if box1.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        box1.setAutoDraw(True)
    
    # *box2* updates
    if box2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        box2.setAutoDraw(True)
    
    if mouse.getPressed()[0] == 0:
        mouseDown = False
        
    if mouse.getPressed()[0]==1 and box.name not in clicked and not mouseDown:
        box.color = "black"
        clicked.append(box1.name)
        mouseDown = True  
    elif mouse.getPressed()[0]==2 and box.name in clicked and not mouseDown:
        box.color = "white"
        clicked.append(box2.name)
        mouseDown = True

    # *mouse* updates
    if mouse.status == NOT_STARTED and t >= 0.0-frameTolerance:
        # keep track of start time/frame for later
        mouse.frameNStart = frameN  # exact frame index
        mouse.tStart = t  # local t and not account for scr refresh
        mouse.tStartRefresh = tThisFlipGlobal  # on global time
        win.timeOnFlip(mouse, 'tStartRefresh')  # time at next scr refresh
        mouse.status = STARTED
        mouse.mouseClock.reset()
        prevButtonState = mouse.getPressed()  # if button is down already this ISN'T a new click
    if mouse.status == STARTED:  # only update if started and not finished!
        buttons = mouse.getPressed()
        if buttons != prevButtonState:  # button state changed?
            prevButtonState = buttons
            if sum(buttons) > 0:  # state changed to a new click
                x, y = mouse.getPos()
                mouse.x.append(x)
                mouse.y.append(y)
                buttons = mouse.getPressed()
                mouse.leftButton.append(buttons[0])
                mouse.midButton.append(buttons[1])
                mouse.rightButton.append(buttons[2])
                mouse.time.append(mouse.mouseClock.getTime())
    
    # check for quit (typically the Esc key)
    if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
        core.quit()
    
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in trialComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

# -------Ending Routine "trial"-------
for thisComponent in trialComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)
routineTimer.reset()

"""
6. Start Practice
"""

NbackInstructionText5 = "In the above 1-back example you should make a \"yes\" response (left click) on trial 3, since the position is the same as the position on trial 2, while the other trials require a \"no\" (right click) response."
ClickToContinueText = "Click to continue"
# Picture Loop 3-16.png
NbackInstructionText6 = "First, we will practice some trials so that you can get used to the procedure.\n\n\nAfter each response you'll see whether your response was correct, incorrect, or whether you forgot to respond.\n\n\n\n\n\nGood Luck!"
ClickToStartText = "Click to start practice"
NbackInstructionText7 = "1-back\n\n\nDuring 1-back you will have to indicate whether the current position matches the position that was presented in the last trial, by either pressing the \"yes\" button (left click) or the \"no\" button (right click).\n\n\nExperimenter press [Space] to see an example."


continueRoutine = True
InstructionImageArray = ['3.png', '4.png', '5.png', '6.png', '7.png', '8.png', '9.png', '10.png', '11.png', '12.png', '13.png', '14.png', '15.png', '16.png']
iteration = 0
NbackInstructions.setText(NbackInstructionText5)
NbackInstructions.draw()
ClickPrompt.setText(ClickToContinueText)
mouse = event.Mouse()
prevButtonState = mouse.getPressed()  # if button is down already this ISN'T a new click
while continueRoutine == True:
    for i in range(InstructionImageArray.len()):
        NbackInstructionWideImg.setImage(InstructionImageArray[i])
        core.wait(1)
        NbackInstructionWideImg.draw()
        win.flip()
        if i == InstructionImageArray.len():
            iteration = 1
        if iteration == 1:
            ClickPrompt.draw()
            buttons = mouse.getPressed()
            if buttons != prevButtonState:  # button state changed?
                prevButtonState = buttons
                if sum(buttons) > 0:
                    continueRoutine = False
NbackInstructions.setText(NbackInstructionText6)
NbackInstructions.draw()
win.flip()
core.wait(2)
mouse = event.Mouse()
while(mouse.getPressed()[0] != 1):
    ClickPrompt.setText(ClickToStartText)
    ClickPrompt.draw()
    win.flip()

# NbackInstructions.setText(NbackInstructionText5)

# NbackInstructions.draw()
# win.flip()
# event.waitKeys(keyList = 'space')
# NbackInstructions.setText(NbackInstructionText2)
# NbackInstructions.draw()
# ClickPrompt.draw()
# win.flip()
# event.waitKeys(keyList = 'space')
# NbackInstructions.setText(NbackInstructionText3)
# NbackInstructions.draw()
# NbackInstructionImg.setImage('2.png')
# win.flip()
# event.waitKeys(keyList = 'space')
# NbackInstructionImg.setAutoDraw(True)
# NbackInstructions.setText(NbackInstructionText4)
# NbackInstructions.draw()
# win.flip()
# event.waitKeys(keyList = 'space')


""" 
7. 1-Back Practice
"""
# set up handler to look after randomisation of conditions etc
TaskT1Loop = data.TrialHandler(nReps=TaskT1, method='random', 
    extraInfo=expInfo, originPath=-1,
    trialList=[None],
    seed=None, name='TaskT1Loop')
thisExp.addLoop(TaskT1Loop)  # add the loop to the experiment
thisTaskT1Loop = TaskT1Loop.trialList[0]  # so we can initialise stimuli with some values
# abbreviate parameter names if possible (e.g. rgb = thisTaskT1Loop.rgb)
if thisTaskT1Loop != None:
    for paramName in thisTaskT1Loop:
        exec('{} = thisTaskT1Loop[paramName]'.format(paramName))

for thisTaskT1Loop in TaskT1Loop:
    currentLoop = TaskT1Loop
    # abbreviate parameter names if possible (e.g. rgb = thisTaskT1Loop.rgb)
    if thisTaskT1Loop != None:
        for paramName in thisTaskT1Loop:
            exec('{} = thisTaskT1Loop[paramName]'.format(paramName))
    

    # while passed == False, keep redoing the instructions 3 times.

    """ 
    7i. 1-back Practice Instruction
    """
    # ------Prepare to start Routine "NbackInstructions"-------
    continueRoutine = True
    # update component parameters for each repeat
    NbackStart.keys = []
    NbackStart.rt = []
    _NbackStart_allKeys = []
    # keep track of which components have finished
    NbackInstructionsComponents = [NbackInstructions, NbackStart]
    for thisComponent in NbackInstructionsComponents:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    NbackInstructionsClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    frameN = -1

    # -------Run Routine "NbackInstructions"-------
    while continueRoutine:
        # get current time
        t = NbackInstructionsClock.getTime()
        tThisFlip = win.getFutureFlipTime(clock=NbackInstructionsClock)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *NbackInstructions* updates
        if NbackInstructions.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            NbackInstructions.frameNStart = frameN  # exact frame index
            NbackInstructions.tStart = t  # local t and not account for scr refresh
            NbackInstructions.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(NbackInstructions, 'tStartRefresh')  # time at next scr refresh
            if biopac_exists:
                win.callOnFlip(biopac.setData, biopac, 0)
                win.callOnFlip(biopac.setData, biopac, nback_instructions)
            NbackInstructions.setAutoDraw(True)
        
        # *NbackStart* updates
        waitOnFlip = False
        if NbackStart.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            NbackStart.frameNStart = frameN  # exact frame index
            NbackStart.tStart = t  # local t and not account for scr refresh
            NbackStart.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(NbackStart, 'tStartRefresh')  # time at next scr refresh
            NbackStart.status = STARTED
            # keyboard checking is just starting
            waitOnFlip = True
            win.callOnFlip(NbackStart.clock.reset)  # t=0 on next screen flip
            win.callOnFlip(NbackStart.clearEvents, eventType='keyboard')  # clear events on next screen flip
        if NbackStart.status == STARTED and not waitOnFlip:
            theseKeys = NbackStart.getKeys(keyList=['space'], waitRelease=False)
            _NbackStart_allKeys.extend(theseKeys)
            if len(_NbackStart_allKeys):
                NbackStart.keys = _NbackStart_allKeys[-1].name  # just the last key pressed
                NbackStart.rt = _NbackStart_allKeys[-1].rt
                # a response ends the routine
                continueRoutine = False
        
        # Autoresponder
        if t >= thisSimKey.rt and autorespond == 1:
            _NbackStart_allKeys.extend([thisSimKey])

        # check for quit (typically the Esc key)
        if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
            core.quit()
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in NbackInstructionsComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()

    # -------Ending Routine "NbackInstructions"-------
    if biopac_exists:
        biopac.setData(biopac, 0)
    for thisComponent in NbackInstructionsComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    thisExp.addData('NbackInstructions.started', NbackInstructions.tStartRefresh)
    thisExp.addData('NbackInstructions.stopped', NbackInstructions.tStopRefresh)
    # check responses
    if NbackStart.keys in ['', [], None]:  # No response was made
        NbackStart.keys = None
    thisExp.addData('NbackStart.keys',NbackStart.keys)
    if NbackStart.keys != None:  # we had a response
        thisExp.addData('NbackStart.rt', NbackStart.rt)
    thisExp.addData('NbackStart.started', NbackStart.tStartRefresh)
    thisExp.addData('NbackStart.stopped', NbackStart.tStopRefresh)
    thisExp.nextEntry()
    # the Routine "NbackInstructions" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()

"""
Start Scanner
"""

start = visual.TextStim(win, text=start_msg, height=.05, color=win.rgb + 0.5)
start.draw()  # Automatically draw every frame
win.flip()
if autorespond != 1:
    # Trigger
    event.waitKeys(keyList = 's') # experimenter start key - safe key before fMRI trigger
    event.waitKeys(keyList='5')   # fMRI trigger
    TR = 0.46
    core.wait(TR*6)         # Wait 6 TRs, Dummy Scans

""" 
7ii. Pre-1-Back Task Fixation Cross
"""
# ------Prepare to start Routine "Fixation"-------
continueRoutine = True
routineTimer.add(1.000000)
# update component parameters for each repeat
# keep track of which components have finished
FixationComponents = [fixation_1]
for thisComponent in FixationComponents:
    thisComponent.tStart = None
    thisComponent.tStop = None
    thisComponent.tStartRefresh = None
    thisComponent.tStopRefresh = None
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED
# reset timers
t = 0
_timeToFirstFrame = win.getFutureFlipTime(clock="now")
FixationClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
frameN = -1

# -------Run Routine "Fixation"-------
while continueRoutine and routineTimer.getTime() > 0:
    # get current time
    t = FixationClock.getTime()
    tThisFlip = win.getFutureFlipTime(clock=FixationClock)
    tThisFlipGlobal = win.getFutureFlipTime(clock=None)
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame
    
    # *fixation_1* updates
    if fixation_1.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        # keep track of start time/frame for later
        fixation_1.frameNStart = frameN  # exact frame index
        fixation_1.tStart = t  # local t and not account for scr refresh
        fixation_1.tStartRefresh = tThisFlipGlobal  # on global time
        win.timeOnFlip(fixation_1, 'tStartRefresh')  # time at next scr refresh
        fixation_1.setAutoDraw(True)
    if fixation_1.status == STARTED:
        # is it time to stop? (based on global clock, using actual start)
        if tThisFlipGlobal > fixation_1.tStartRefresh + 1.0-frameTolerance:
            # keep track of stop time/frame for later
            fixation_1.tStop = t  # not accounting for scr refresh
            fixation_1.frameNStop = frameN  # exact frame index
            win.timeOnFlip(fixation_1, 'tStopRefresh')  # time at next scr refresh
            fixation_1.setAutoDraw(False)
    
    # check for quit (typically the Esc key)
    if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
        core.quit()
    
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in FixationComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

# -------Ending Routine "Fixation"-------
for thisComponent in FixationComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)
thisExp.addData('fixation_1.started', fixation_1.tStartRefresh)
thisExp.addData('fixation_1.stopped', fixation_1.tStopRefresh)


####
# 1-back Start
####


# set up handler to look after randomisation of conditions etc
trials = data.TrialHandler(nReps=1, method='sequential', 
    extraInfo=expInfo, originPath=-1,
    trialList=data.importConditions('Practice_N-back-1.xlsx'),
    seed=None, name='trials')
thisExp.addLoop(trials)  # add the loop to the experiment
thisTrial = trials.trialList[0]  # so we can initialise stimuli with some values
# abbreviate parameter names if possible (e.g. rgb = thisTrial.rgb)
if thisTrial != None:
    for paramName in thisTrial:
        exec('{} = thisTrial[paramName]'.format(paramName))

for thisTrial in trials:
    currentLoop = trials
    # abbreviate parameter names if possible (e.g. rgb = thisTrial.rgb)
    if thisTrial != None:
        for paramName in thisTrial:
            exec('{} = thisTrial[paramName]'.format(paramName))
    
    # ------Prepare to start Routine "N_back_1_Trial"-------
    continueRoutine = True
    routineTimer.add(2.000000)
    # update component parameters for each repeat
    target_square.setPos(location)
    response.keys = []
    response.rt = []
    _response_allKeys = []

    incorrect_text = "Incorrect!"
    noresponse_text = "No Response!"
    correct_text = "Correct!"

    # keep track of which components have finished
    N_back_1_TrialComponents = [grid_lines, target_square, fixation_2, response, feedback]
    for thisComponent in N_back_1_TrialComponents:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    N_back_1_TrialClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    frameN = -1
    
    # -------Run Routine "N_back_1_Trial"-------
    while continueRoutine and routineTimer.getTime() > 0:
        # get current time
        t = N_back_1_TrialClock.getTime()
        tThisFlip = win.getFutureFlipTime(clock=N_back_1_TrialClock)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *grid_lines* updates
        if grid_lines.status == NOT_STARTED and tThisFlip >= 0-frameTolerance:
            # keep track of start time/frame for later
            grid_lines.frameNStart = frameN  # exact frame index
            grid_lines.tStart = t  # local t and not account for scr refresh
            grid_lines.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(grid_lines, 'tStartRefresh')  # time at next scr refresh
            grid_lines.setAutoDraw(True)
        if grid_lines.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > grid_lines.tStartRefresh + 2-frameTolerance:
                # keep track of stop time/frame for later
                grid_lines.tStop = t  # not accounting for scr refresh
                grid_lines.frameNStop = frameN  # exact frame index
                win.timeOnFlip(grid_lines, 'tStopRefresh')  # time at next scr refresh
                grid_lines.setAutoDraw(False)
        
        # *target_square* updates
        if target_square.status == NOT_STARTED and tThisFlip >= 0-frameTolerance:
            # keep track of start time/frame for later
            target_square.frameNStart = frameN  # exact frame index
            target_square.tStart = t  # local t and not account for scr refresh
            target_square.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(target_square, 'tStartRefresh')  # time at next scr refresh
            target_square.setAutoDraw(True)
        if target_square.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > target_square.tStartRefresh + 1-frameTolerance:
                # keep track of stop time/frame for later
                target_square.tStop = t  # not accounting for scr refresh
                target_square.frameNStop = frameN  # exact frame index
                win.timeOnFlip(target_square, 'tStopRefresh')  # time at next scr refresh
                target_square.setAutoDraw(False)
        
        # *fixation_2* updates
        if fixation_2.status == NOT_STARTED and tThisFlip >= 1-frameTolerance:
            # keep track of start time/frame for later
            fixation_2.frameNStart = frameN  # exact frame index
            fixation_2.tStart = t  # local t and not account for scr refresh
            fixation_2.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(fixation_2, 'tStartRefresh')  # time at next scr refresh
            fixation_2.setAutoDraw(True)
        if fixation_2.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > fixation_2.tStartRefresh + 1.0-frameTolerance:
                # keep track of stop time/frame for later
                fixation_2.tStop = t  # not accounting for scr refresh
                fixation_2.frameNStop = frameN  # exact frame index
                win.timeOnFlip(fixation_2, 'tStopRefresh')  # time at next scr refresh
                fixation_2.setAutoDraw(False)
        
        # *response* updates
        waitOnFlip = False
        if response.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            response.frameNStart = frameN  # exact frame index
            response.tStart = t  # local t and not account for scr refresh
            response.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(response, 'tStartRefresh')  # time at next scr refresh
            response.status = STARTED
            # keyboard checking is just starting
            waitOnFlip = True
            win.callOnFlip(response.mouseClock.reset) # t=0 on next screen flip
            win.callOnFlip(response.clickReset) # t=0 on next screen flip
            prevButtonState = response.getPressed()[0]  # if button is down already this ISN'T a new click
        if response.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > response.tStartRefresh + 2-frameTolerance:
                # keep track of stop time/frame for later
                response.tStop = t  # not accounting for scr refresh
                response.frameNStop = frameN  # exact frame index
                win.timeOnFlip(response, 'tStopRefresh')  # time at next scr refresh
                response.status = FINISHED
        if response.status == STARTED and not waitOnFlip:
            response.click, response.rt = response_2.getPressed(getTime = True)
            response.click = response.click[0]
            response.rt = response.rt[0]
            if response.click != prevButtonState:  # button state changed?
                prevButtonState = response.click
            if response.click == 1 and gotValidClick == False:
                print(str(response.click), str(response.rt))
                if corrAns != None:
                    response.corr = 1
                    if biopac_exists:
                        biopac.setData(biopac, 0)
                        biopac.setData(biopac, nback_hit)
                        Feedback.setText(correct_text)
                else:
                    response.corr = 0;  # failed to respond (incorrectly)
                    if biopac_exists:
                        biopac.setData(biopac, 0)
                        biopac.setData(biopac, nback_comiss) # mark comission error
                        Feedback.setText(incorrect_text)
                gotValidClick = True

        # check responses
        if response.keys in ['', [], None]:  # No response was made
            response.keys = None
            # was no response the correct answer?!
            if str(corrAns).lower() == 'none':
                response.corr = 1;  # correct non-response
                Feedback.setText(correct_text)
            else:
                response.corr = 0;  # failed to respond (incorrectly)
                Feedback.setText(noresponse_text)

        # *Feedback* updates
        waitOnFlip = False
        if Feedback.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            Feedback.frameNStart = frameN  # exact frame index
            Feedback.tStart = t  # local t and not account for scr refresh
            Feedback.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(Feedback, 'tStartRefresh')  # time at next scr refresh
            Feedback.status = STARTED
            # keyboard checking is just starting
            waitOnFlip = True
            win.callOnFlip(Feedback.clock.reset)  # t=0 on next screen flip
            win.callOnFlip(Feedback.clearEvents, eventType='keyboard')  # clear events on next screen flip

        if Feedback.status == STARTED and not waitOnFlip:
            theseKeys = Feedback.getKeys(keyList=['space'], waitRelease=False)
            _Feedback_allKeys.extend(theseKeys)
            if len(_Feedback_allKeys):
                Feedback.keys = _Feedback_allKeys[-1].name  # just the last key pressed
                Feedback.rt = _Feedback_allKeys[-1].rt
                # a response ends the routine
                continueRoutine = False

        # check for quit (typically the Esc key)
        if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
            core.quit()
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in N_back_1_TrialComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # -------Ending Routine "N_back_1_Trial"-------
    if biopac_exists:
        biopac.setData(biopac, 0)
    for thisComponent in N_back_1_TrialComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    trials.addData('grid_lines.started', grid_lines.tStartRefresh)
    trials.addData('grid_lines.stopped', grid_lines.tStopRefresh)
    trials.addData('target_square.started', target_square.tStartRefresh)
    trials.addData('target_square.stopped', target_square.tStopRefresh)
    trials.addData('fixation_2.started', fixation_2.tStartRefresh)
    trials.addData('fixation_2.stopped', fixation_2.tStopRefresh)
    # store data for trials (TrialHandler)
    trials.addData('response.keys',response.keys)
    trials.addData('response.corr', response.corr)
    
    trials.addData('response.x', x)
    trials.addData('response.y', y)
    trials.addData('response.leftButton', response.click)

    if response.keys != None:  # we had a response
        trials.addData('response.rt', response.rt)
    trials.addData('response.click',response.click)
    trials.addData('response.corr', response.corr)
    trials.addData('response.started', response.tStartRefresh)
    trials.addData('response.stopped', response.tStopRefresh)
    thisExp.nextEntry()

    score = result/100
    
    # completed 1 repeats of 'trials'

####
# Score Report
####

# ------Prepare to start Routine "ScoreReport"-------
continueRoutine = True
# update component parameters for each repeat
NbackStart.keys = []
NbackStart.rt = []
_NbackStart_allKeys = []
# keep track of which components have finished
NbackInstructionsComponents = [NbackInstructions, NbackStart]
for thisComponent in NbackInstructionsComponents:
    thisComponent.tStart = None
    thisComponent.tStop = None
    thisComponent.tStartRefresh = None
    thisComponent.tStopRefresh = None
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED
# reset timers
t = 0
_timeToFirstFrame = win.getFutureFlipTime(clock="now")
NbackInstructionsClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
frameN = -1

TryAgainText = "Let's try that again...\n\n\n\n\n\n\n\nExperimenter press [Space] to continue."
PleaseWaitText = "Please wait for the experimenter ..."
PassedText = "Okay! Let's move on.\n\n\n\n\n\n\n\nExperimenter press [Space] to continue."
PerfectText = "Perfect! Let's move on.\n\n\n\n\n\n\n\nExperimenter press [Space] to continue."


# -------Run Routine "ScoreReport"-------
while continueRoutine:
    # get current time
    t = NbackInstructionsClock.getTime()
    tThisFlip = win.getFutureFlipTime(clock=NbackInstructionsClock)
    tThisFlipGlobal = win.getFutureFlipTime(clock=None)
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame
    
    # *NbackInstructions* updates
    if NbackInstructions.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        if (turns == 3 and score < 70):
            NbackInstructions(PleaseWaitText)
            action = 1
        if (score < 70):
            NbackInstructions(TryAgainText)
            action = 2
        if (score > 70):
            NbackInstructions(PassedText)
            action = 3
        if (score == 100):
            NbackInstructions(PerfectText)
            action = 3

        # keep track of start time/frame for later
        NbackInstructions.frameNStart = frameN  # exact frame index
        NbackInstructions.tStart = t  # local t and not account for scr refresh
        NbackInstructions.tStartRefresh = tThisFlipGlobal  # on global time
        win.timeOnFlip(NbackInstructions, 'tStartRefresh')  # time at next scr refresh
        if biopac_exists:
            win.callOnFlip(biopac.setData, biopac, 0)
            win.callOnFlip(biopac.setData, biopac, nback_instructions)
        NbackInstructions.setAutoDraw(True)
    
    # *NbackStart* updates
    waitOnFlip = False
    if NbackStart.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        # keep track of start time/frame for later
        NbackStart.frameNStart = frameN  # exact frame index
        NbackStart.tStart = t  # local t and not account for scr refresh
        NbackStart.tStartRefresh = tThisFlipGlobal  # on global time
        win.timeOnFlip(NbackStart, 'tStartRefresh')  # time at next scr refresh
        NbackStart.status = STARTED
        # keyboard checking is just starting
        waitOnFlip = True
        win.callOnFlip(NbackStart.clock.reset)  # t=0 on next screen flip
        win.callOnFlip(NbackStart.clearEvents, eventType='keyboard')  # clear events on next screen flip
    if NbackStart.status == STARTED and not waitOnFlip:
        theseKeys = NbackStart.getKeys(keyList=['space'], waitRelease=False)
        _NbackStart_allKeys.extend(theseKeys)
        if len(_NbackStart_allKeys):
            NbackStart.keys = _NbackStart_allKeys[-1].name  # just the last key pressed
            NbackStart.rt = _NbackStart_allKeys[-1].rt
            # a response ends the routine
            continueRoutine = False
    
    # Autoresponder
    if t >= thisSimKey.rt and autorespond == 1:
        _NbackStart_allKeys.extend([thisSimKey])

    # check for quit (typically the Esc key)
    if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
        core.quit()
    
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in NbackInstructionsComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

# -------Ending Routine "ScoreReport"-------
if biopac_exists:
    biopac.setData(biopac, 0)
for thisComponent in NbackInstructionsComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)
thisExp.addData('NbackInstructions.started', NbackInstructions.tStartRefresh)
thisExp.addData('NbackInstructions.stopped', NbackInstructions.tStopRefresh)
# check responses
if NbackStart.keys in ['', [], None]:  # No response was made
    NbackStart.keys = None
thisExp.addData('NbackStart.keys',NbackStart.keys)
if NbackStart.keys != None:  # we had a response
    thisExp.addData('NbackStart.rt', NbackStart.rt)
thisExp.addData('NbackStart.started', NbackStart.tStartRefresh)
thisExp.addData('NbackStart.stopped', NbackStart.tStopRefresh)
thisExp.nextEntry()
# the Routine "NbackInstructions" was not non-slip safe, so reset the non-slip timer
routineTimer.reset()






# if passed == FALSE
TryAgainText = "Let's try that again...\n\n\n\n\n\n\n\nExperimenter press [Space] to continue."

# if passed == FALSE counter > 3:
PleaseWaitText = "Please wait for the experimenter ..."
# Probably will have to talk to participant about disqualifying their participation

# if passed == TRUE:
PassedText = "Great! Let's move on.\n\n\n\n\n\n\n\nExperimenter press [Space] to continue."


""" 
7. 2-Back Practice
"""


""" 
7. 2-Back Practice Instruction
"""

    # while passed == False, keep redoing the instructions 3 times.


# ------Prepare to start Routine "Instructions_2"-------

NbackInstructionText8 = "2-back\n\n\nDuring 2-back you will have to indicate whether the current position matches the position matches the position that was presented two trials ago, by either pressing the \"yes\" button (left click) or the \"no\" button (right click).\n\n\nExperimenter press [Space] to see an example."
ClickToContinueText = "Click to continue"

NbackInstructionText9 = "In this 2-back example you should make a \"yes\" response (left click) on trial 3, since the position is the same as the position on trial 1, while the other trials require a \"no\" (right click) response. "
# Picture Loop 17-30.png

NbackInstructionText10 = "Now, we will practice some trials so that you can get used to the procedure.\n\n\nAfter each response you'll see whether your response was correct, incorrect, or whether you forgot to respond.\n\n\n\n\n\nGood Luck!"
ClickToStart = "Click to start practice"

###########################################################

continueRoutine = True
# update component parameters for each repeat
key_resp_2.keys = []
key_resp_2.rt = []
_key_resp_2_allKeys = []
# keep track of which components have finished
Instructions_2Components = [instructions_2, key_resp_2]
for thisComponent in Instructions_2Components:
    thisComponent.tStart = None
    thisComponent.tStop = None
    thisComponent.tStartRefresh = None
    thisComponent.tStopRefresh = None
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED
# reset timers
t = 0
_timeToFirstFrame = win.getFutureFlipTime(clock="now")
Instructions_2Clock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
frameN = -1

# -------Run Routine "Instructions_2"-------
while continueRoutine:
    # get current time
    t = Instructions_2Clock.getTime()
    tThisFlip = win.getFutureFlipTime(clock=Instructions_2Clock)
    tThisFlipGlobal = win.getFutureFlipTime(clock=None)
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame
    
    # *instructions_2* updates
    if instructions_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        # keep track of start time/frame for later
        instructions_2.frameNStart = frameN  # exact frame index
        instructions_2.tStart = t  # local t and not account for scr refresh
        instructions_2.tStartRefresh = tThisFlipGlobal  # on global time
        win.timeOnFlip(instructions_2, 'tStartRefresh')  # time at next scr refresh
        instructions_2.setAutoDraw(True)
    
    # *key_resp_2* updates
    waitOnFlip = False
    if key_resp_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        # keep track of start time/frame for later
        key_resp_2.frameNStart = frameN  # exact frame index
        key_resp_2.tStart = t  # local t and not account for scr refresh
        key_resp_2.tStartRefresh = tThisFlipGlobal  # on global time
        win.timeOnFlip(key_resp_2, 'tStartRefresh')  # time at next scr refresh
        key_resp_2.status = STARTED
        # keyboard checking is just starting
        waitOnFlip = True
        win.callOnFlip(key_resp_2.clock.reset)  # t=0 on next screen flip
        win.callOnFlip(key_resp_2.clearEvents, eventType='keyboard')  # clear events on next screen flip
    if key_resp_2.status == STARTED and not waitOnFlip:
        theseKeys = key_resp_2.getKeys(keyList=['space'], waitRelease=False)
        _key_resp_2_allKeys.extend(theseKeys)
        if len(_key_resp_2_allKeys):
            key_resp_2.keys = _key_resp_2_allKeys[-1].name  # just the last key pressed
            key_resp_2.rt = _key_resp_2_allKeys[-1].rt
            # a response ends the routine
            continueRoutine = False
    
    # check for quit (typically the Esc key)
    if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
        core.quit()
    
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in Instructions_2Components:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

# -------Ending Routine "Instructions_2"-------
for thisComponent in Instructions_2Components:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)
thisExp.addData('instructions_2.started', instructions_2.tStartRefresh)
thisExp.addData('instructions_2.stopped', instructions_2.tStopRefresh)
# check responses
if key_resp_2.keys in ['', [], None]:  # No response was made
    key_resp_2.keys = None
thisExp.addData('key_resp_2.keys',key_resp_2.keys)
if key_resp_2.keys != None:  # we had a response
    thisExp.addData('key_resp_2.rt', key_resp_2.rt)
thisExp.addData('key_resp_2.started', key_resp_2.tStartRefresh)
thisExp.addData('key_resp_2.stopped', key_resp_2.tStopRefresh)
thisExp.nextEntry()
# the Routine "Instructions_2" was not non-slip safe, so reset the non-slip timer
routineTimer.reset()


"""
Start Scanner
"""

start = visual.TextStim(win, text=start_msg, height=.05, color=win.rgb + 0.5)
start.draw()  # Automatically draw every frame
win.flip()
if autorespond != 1:
    # Trigger
    event.waitKeys(keyList = 's') # experimenter start key - safe key before fMRI trigger
    event.waitKeys(keyList='5')   # fMRI trigger
    TR = 0.46
    core.wait(TR*6)         # Wait 6 TRs, Dummy Scans

# ------Prepare to start Routine "Fixation"-------
continueRoutine = True
routineTimer.add(1.000000)
# update component parameters for each repeat
# keep track of which components have finished
FixationComponents = [fixation_1]
for thisComponent in FixationComponents:
    thisComponent.tStart = None
    thisComponent.tStop = None
    thisComponent.tStartRefresh = None
    thisComponent.tStopRefresh = None
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED
# reset timers
t = 0
_timeToFirstFrame = win.getFutureFlipTime(clock="now")
FixationClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
frameN = -1

# -------Run Routine "Fixation"-------
while continueRoutine and routineTimer.getTime() > 0:
    # get current time
    t = FixationClock.getTime()
    tThisFlip = win.getFutureFlipTime(clock=FixationClock)
    tThisFlipGlobal = win.getFutureFlipTime(clock=None)
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame
    
    # *fixation_1* updates
    if fixation_1.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        # keep track of start time/frame for later
        fixation_1.frameNStart = frameN  # exact frame index
        fixation_1.tStart = t  # local t and not account for scr refresh
        fixation_1.tStartRefresh = tThisFlipGlobal  # on global time
        win.timeOnFlip(fixation_1, 'tStartRefresh')  # time at next scr refresh
        fixation_1.setAutoDraw(True)
    if fixation_1.status == STARTED:
        # is it time to stop? (based on global clock, using actual start)
        if tThisFlipGlobal > fixation_1.tStartRefresh + 1.0-frameTolerance:
            # keep track of stop time/frame for later
            fixation_1.tStop = t  # not accounting for scr refresh
            fixation_1.frameNStop = frameN  # exact frame index
            win.timeOnFlip(fixation_1, 'tStopRefresh')  # time at next scr refresh
            fixation_1.setAutoDraw(False)
    
    # check for quit (typically the Esc key)
    if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
        core.quit()
    
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in FixationComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

# -------Ending Routine "Fixation"-------
for thisComponent in FixationComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)
thisExp.addData('fixation_1.started', fixation_1.tStartRefresh)
thisExp.addData('fixation_1.stopped', fixation_1.tStopRefresh)


# set up handler to look after randomisation of conditions etc
Nback2 = os.sep.join([_thisDir,"Practice_N-back-2.xlsx"])
trials_2 = data.TrialHandler(nReps=1, method='sequential', 
    extraInfo=expInfo, originPath=-1,
    trialList=data.importConditions(Nback2),
    seed=None, name='trials_2')
thisExp.addLoop(trials_2)  # add the loop to the experiment
thisTrial_2 = trials_2.trialList[0]  # so we can initialise stimuli with some values
# abbreviate parameter names if possible (e.g. rgb = thisTrial_2.rgb)
if thisTrial_2 != None:
    for paramName in thisTrial_2:
        exec('{} = thisTrial_2[paramName]'.format(paramName))    
""" 
7iii. Working Memory 2-Back Main Loop
"""
for thisTrial_2 in trials_2:
    currentLoop = trials_2
    # abbreviate parameter names if possible (e.g. rgb = thisTrial_2.rgb)
    if thisTrial_2 != None:
        for paramName in thisTrial_2:
            exec('{} = thisTrial_2[paramName]'.format(paramName))
    
    # ------Prepare to start Routine "N_back_2_trials"-------
    continueRoutine = True
    routineTimer.add(2.000000)
    # update component parameters for each repeat
    target_square_2.setPos(location)
    response_2 = event.Mouse(win=win, visible=False) # Re-initialize
    response_2.click = []
    response_2.rt = []
    response_2.corr = []
    x, y = [None, None]
    gotValidClick = False  # until a click is received
    
    # keep track of which components have finished
    N_back_2_trialsComponents = [grid_lines_2, target_square_2, fixation_3, response_2]
    for thisComponent in N_back_2_trialsComponents:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    N_back_2_trialsClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    frameN = -1
    
    # -------Run Routine "N_back_2_trials"-------
    while continueRoutine and routineTimer.getTime() > 0:
        # get current time
        t = N_back_2_trialsClock.getTime()
        tThisFlip = win.getFutureFlipTime(clock=N_back_2_trialsClock)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame

        # *response_2* updates
        waitOnFlip = False
        if response_2.status == NOT_STARTED and t >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            response_2.frameNStart = frameN  # exact frame index
            response_2.tStart = t  # local t and not account for scr refresh
            response_2.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(response_2, 'tStartRefresh')  # time at next scr refresh
            response_2.status = STARTED
            waitOnFlip = True
            win.callOnFlip(response_2.mouseClock.reset) # t=0 on next screen flip
            win.callOnFlip(response_2.clickReset) # t=0 on next screen flip
            prevButtonState = response_2.getPressed()[0]  # if button is down already this ISN'T a new click
        if response_2.status == STARTED:  # only update if started and not finished!
            if tThisFlipGlobal > response_2.tStartRefresh + 2-frameTolerance:
                # keep track of stop time/frame for later
                response_2.tStop = t  # not accounting for scr refresh
                response_2.frameNStop = frameN  # exact frame index
                win.timeOnFlip(response_2, 'tStopRefresh')  # time at next scr refresh
                response_2.status = FINISHED
        if response_2.status == STARTED and not waitOnFlip:
            response_2.click, response_2.rt = response_2.getPressed(getTime = True)
            response_2.click = response_2.click[0]
            response_2.rt = response_2.rt[0]
            if response_2.click != prevButtonState:  # button state changed?
                prevButtonState = response_2.click
            if response_2.click == 1 and gotValidClick == False:
                print(str(response_2.click), str(response_2.rt))
                if corrAns != None:
                    response_2.corr = 1
                    if biopac_exists:
                        biopac.setData(biopac, 0)
                        biopac.setData(biopac, nback_hit)
                else:
                    response_2.corr = 0;  # failed to respond (incorrectly)
                    if biopac_exists:
                        biopac.setData(biopac, 0)
                        biopac.setData(biopac, nback_comiss) # mark comission error
                gotValidClick = True
        
        # *grid_lines_2* updates
        if grid_lines_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            grid_lines_2.frameNStart = frameN  # exact frame index
            grid_lines_2.tStart = t  # local t and not account for scr refresh
            grid_lines_2.tStartRefresh = tThisFlipGlobal  # on global time
            if biopac_exists:
                win.callOnFlip(biopac.setData, biopac, 0)
                win.callOnFlip(biopac.setData, biopac, nback_trial_start)
            win.timeOnFlip(grid_lines_2, 'tStartRefresh')  # time at next scr refresh
            grid_lines_2.setAutoDraw(True)
        if grid_lines_2.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > grid_lines_2.tStartRefresh + 2-frameTolerance:
                # keep track of stop time/frame for later
                grid_lines_2.tStop = t  # not accounting for scr refresh
                grid_lines_2.frameNStop = frameN  # exact frame index
                win.timeOnFlip(grid_lines_2, 'tStopRefresh')  # time at next scr refresh
                grid_lines_2.setAutoDraw(False)
        
        # *target_square_2* updates
        if target_square_2.status == NOT_STARTED and tThisFlip >= 0-frameTolerance:
            # keep track of start time/frame for later
            target_square_2.frameNStart = frameN  # exact frame index
            target_square_2.tStart = t  # local t and not account for scr refresh
            target_square_2.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(target_square_2, 'tStartRefresh')  # time at next scr refresh
            target_square_2.setAutoDraw(True)
        if target_square_2.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > target_square_2.tStartRefresh + 1.0-frameTolerance:
                # keep track of stop time/frame for later
                target_square_2.tStop = t  # not accounting for scr refresh
                target_square_2.frameNStop = frameN  # exact frame index
                win.timeOnFlip(target_square_2, 'tStopRefresh')  # time at next scr refresh
                target_square_2.setAutoDraw(False)
        
        # *fixation_3* updates
        if fixation_3.status == NOT_STARTED and tThisFlip >= 1-frameTolerance:
            # keep track of start time/frame for later
            fixation_3.frameNStart = frameN  # exact frame index
            fixation_3.tStart = t  # local t and not account for scr refresh
            fixation_3.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(fixation_3, 'tStartRefresh')  # time at next scr refresh
            fixation_3.setAutoDraw(True)
        if fixation_3.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > fixation_3.tStartRefresh + 1-frameTolerance:
                # keep track of stop time/frame for later
                fixation_3.tStop = t  # not accounting for scr refresh
                fixation_3.frameNStop = frameN  # exact frame index
                win.timeOnFlip(fixation_3, 'tStopRefresh')  # time at next scr refresh
                fixation_3.setAutoDraw(False)

        # # Autoresponder
        # if t >= thisSimKey.rt and autorespond == 1:
        #     _response_2_allKeys.extend([thisSimKey])

        # check for quit (typically the Esc key)
        if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
            core.quit()
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in N_back_2_trialsComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # -------Ending Routine "N_back_2_trials"-------
    if biopac_exists:
        biopac.setData(biopac, 0)
    for thisComponent in N_back_2_trialsComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)

    # Check non-response
    if response_2.click == 0 and gotValidClick == False:
        response_2.rt = None
        if str(corrAns).lower() == 'none':
            response_2.corr = 1;  # correct non-response
        else:
            response_2.corr = 0;  # failed to respond (incorrectly)

    # x, y = response_2.getPos()
    # response_2.click, response_2.rt = response_2.getPressed(getTime = True)
    # response_2.click = response_2.click[0]
    # response_2.rt = response_2.rt[0]
    trials_2.addData('response_2.x', x)
    trials_2.addData('response_2.y', y)
    trials_2.addData('response_2.leftButton', response_2.click)
    trials_2.addData('grid_lines_2.started', grid_lines_2.tStartRefresh)
    trials_2.addData('grid_lines_2.stopped', grid_lines_2.tStopRefresh)
    trials_2.addData('target_square_2.started', target_square_2.tStartRefresh)
    trials_2.addData('target_square_2.stopped', target_square_2.tStopRefresh)
    trials_2.addData('fixation_3.started', fixation_3.tStartRefresh)
    trials_2.addData('fixation_3.stopped', fixation_3.tStopRefresh)
    # # check responses
    # if response_2.keys in ['', [], None]:  # No response was made
    #     response_2.keys = None
    #     # was no response the correct answer?!
    #     if str(corrAns).lower() == 'none':
    #         response_2.corr = 1;  # correct non-response
    #     else:
    #         response_2.corr = 0;  # failed to respond (incorrectly)
    if response_2.click == 1:  # we had a response
        trials_2.addData('response_2.rt', response_2.rt)

    # store data for trials_2 (TrialHandler)
    trials_2.addData('response_2.click',response_2.click)
    trials_2.addData('response_2.corr', response_2.corr)
    trials_2.addData('response_2.started', response_2.tStartRefresh)
    trials_2.addData('response_2.stopped', response_2.tStopRefresh)
    nback_bids_trial = []
    nback_bids_trial.extend((order_no, grid_lines_2.tStartRefresh, t, response_2.rt, response_2.corr))
    nback_bids.append(nback_bids_trial)

    thisExp.nextEntry()
        
    # completed 1 repeats of 'trials_2' 

        ####
        # Make sure to add a feedback component for each trial after 3rd, or prior to that if comission error was produced.
        ####

    ####
    # Score Report
    ####

    # ------Prepare to start Routine "ScoreReport"-------
    # -------Run Routine "ScoreReport"-------
    # -------Ending Routine "ScoreReport"-------

    # if passed == FALSE
    TryAgainText = "Let's try that again...\n\n\n\n\n\n\n\nExperimenter press [Space] to continue."

    # if passed == FALSE counter > 3:
    PleaseWaitText = "Please wait for the experimenter ..."
    # Probably will have to talk to participant about disqualifying their participation

    # if passed == TRUE:
    PassedText = "Great! Let's move on.\n\n\n\n\n\n\n\nExperimenter press [Space] to continue."


#######
# Real Trials Start
#######

NbackInstructionText11 = "Now we will start some real trials.\n\n\nWe will add some difficulty by periodically sending painful thermal stimulations to a designated body-site. \nDuring the task it is very important that you respond as fast and as accurately as possible.\n\n\nYou should try to respond during the square being presented shortly after. This might be difficult, so it is important that you concentrate!\n\n\n\nDo not forget to respond during every trial."


# Start a loop:
"""
Body-Site Instructions
"""

# Please attach a thermode to the designated body-site:
"""
8c. Instruct the Experimenter on the Body Sites to attach thermodes to at the beginning of each run
"""
for thisrunLoop in runLoop:                     # Loop through each run.
    currentLoop = runLoop
    # abbreviate parameter names if possible (e.g. rgb = thisrunLoop.rgb)
    if thisrunLoop != None:
        for paramName in thisrunLoop:
            exec('{} = thisrunLoop[paramName]'.format(paramName))

    # ------Prepare to start Routine "BodySiteInstruction"-------
    continueRoutine = True
    # update component parameters for each repeat
    BodySiteInstructionRead.keys = []
    BodySiteInstructionRead.rt = []
    _BodySiteInstructionRead_allKeys = []
    ## Update instructions and cues based on current run's body-sites:
    BodySiteInstructionText.text="Experimenter: \nPlease place the thermode on the: \n" + bodySites[runLoop.thisTrialN].lower()
    # keep track of which components have finished
    BodySiteInstructionComponents = [BodySiteInstructionText, BodySiteImg, BodySiteInstructionRead]

    for thisComponent in BodySiteInstructionComponents:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    BodySiteInstructionClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    frameN = -1
    
    # -------Run Routine "BodySiteInstruction"-------
    while continueRoutine:
        # get current time
        t = BodySiteInstructionClock.getTime()
        tThisFlip = win.getFutureFlipTime(clock=BodySiteInstructionClock)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *BodySiteInstructionText* updates
        if BodySiteInstructionText.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            BodySiteInstructionText.frameNStart = frameN  # exact frame index
            BodySiteInstructionText.tStart = t  # local t and not account for scr refresh
            BodySiteInstructionText.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(BodySiteInstructionText, 'tStartRefresh')  # time at next scr refresh
            BodySiteInstructionText.setAutoDraw(True)

        # *BodySiteImg* updates
        if BodySiteImg.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            BodySiteImg.image = bodysite_word2img[bodySites[runLoop.thisTrialN]]
            BodySiteImg.pos = (0, .2)
            # keep track of start time/frame for later
            BodySiteImg.frameNStart = frameN  # exact frame index
            BodySiteImg.tStart = t  # local t and not account for scr refresh
            BodySiteImg.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(BodySiteImg, 'tStartRefresh')  # time at next scr refresh
            BodySiteImg.setAutoDraw(True)
        
        # *BodySiteInstructionRead* updates
        waitOnFlip = False
        if BodySiteInstructionRead.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            BodySiteInstructionRead.frameNStart = frameN  # exact frame index
            BodySiteInstructionRead.tStart = t  # local t and not account for scr refresh
            BodySiteInstructionRead.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(BodySiteInstructionRead, 'tStartRefresh')  # time at next scr refresh
            BodySiteInstructionRead.status = STARTED
            # keyboard checking is just starting
            waitOnFlip = True
            win.callOnFlip(print, "Cueing Off All Biopac Channels")            
            win.callOnFlip(print, "Showing BodySite Instructions")
            win.callOnFlip(print, "Cueing Biopac Channel: " + str(bodymapping_instruction))
            if biopac_exists == 1:
                win.callOnFlip(biopac.setData, biopac, 0)
                win.callOnFlip(biopac.setData, biopac, bodymapping_instruction)
            win.callOnFlip(BodySiteInstructionRead.clock.reset)  # t=0 on next screen flip
            win.callOnFlip(BodySiteInstructionRead.clearEvents, eventType='keyboard')  # clear events on next screen flip
        if BodySiteInstructionRead.status == STARTED and not waitOnFlip:
            theseKeys = BodySiteInstructionRead.getKeys(keyList=['space'], waitRelease=False)
            _BodySiteInstructionRead_allKeys.extend(theseKeys)
            if len(_BodySiteInstructionRead_allKeys):
                BodySiteInstructionRead.keys = _BodySiteInstructionRead_allKeys[-1].name  # just the last key pressed
                BodySiteInstructionRead.rt = _BodySiteInstructionRead_allKeys[-1].rt
                # a response ends the routine
                continueRoutine = False
        
        # Autoresponder
        if t >= thisSimKey.rt and autorespond == 1:
            _BodySiteInstructionRead_allKeys.extend([thisSimKey]) 

        # check for quit (typically the Esc key)
        if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
            core.quit()
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in BodySiteInstructionComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()

    # -------Ending Routine "BodySiteInstruction"-------
    print("CueOff Channel: " + str(bodymapping_instruction))
    if biopac_exists == 1:
        biopac.setData(biopac, 0)
    for thisComponent in BodySiteInstructionComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    runLoop.addData('BodySiteInstructionText.started', BodySiteInstructionText.tStartRefresh)
    runLoop.addData('BodySiteImg.started', BodySiteImg.tStartRefresh)
    runLoop.addData('BodySiteImg.stopped', BodySiteImg.tStopRefresh)
    # check responses
    if BodySiteInstructionRead.keys in ['', [], None]:  # No response was made
        BodySiteInstructionRead.keys = None
    runLoop.addData('BodySiteInstructionRead.keys',BodySiteInstructionRead.keys)
    if BodySiteInstructionRead.keys != None:  # we had a response
        runLoop.addData('BodySiteInstructionRead.rt', BodySiteInstructionRead.rt)
    runLoop.addData('BodySiteInstructionRead.started', BodySiteInstructionRead.tStartRefresh)
    runLoop.addData('BodySiteInstructionRead.stopped', BodySiteInstructionRead.tStopRefresh)
    # Start a new BIDS data collection array for each run
    bodymap_bids_data = []
    # the Routine "BodySiteInstruction" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()

    """
    Start Scanner
    """
    start = visual.TextStim(win, text=start_msg, height=.05, color=win.rgb + 0.5)
    start.draw()  # Automatically draw every frame
    win.flip()
    if autorespond != 1:
        # Trigger
        event.waitKeys(keyList = 's') # experimenter start key - safe key before fMRI trigger
        event.waitKeys(keyList='5')   # fMRI trigger
        TR = 0.46
        core.wait(TR*6)         # Wait 6 TRs, Dummy Scans

    hot = thermode1_temp2program[participant_settingsHeat[bodySites[runLoop.thisTrialN]]]
    
    """ 
    7. 1-Back Real
    """
    """ 
    7ii. Pre-1-Back Task Fixation Cross
    """
    # ------Prepare to start Routine "Fixation"-------
    continueRoutine = True
    routineTimer.add(1.000000)
    # update component parameters for each repeat
    # keep track of which components have finished
    FixationComponents = [fixation_1]
    for thisComponent in FixationComponents:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    FixationClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    frameN = -1

    # -------Run Routine "Fixation"-------
    while continueRoutine and routineTimer.getTime() > 0:
        # get current time
        t = FixationClock.getTime()
        tThisFlip = win.getFutureFlipTime(clock=FixationClock)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *fixation_1* updates
        if fixation_1.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            fixation_1.frameNStart = frameN  # exact frame index
            fixation_1.tStart = t  # local t and not account for scr refresh
            fixation_1.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(fixation_1, 'tStartRefresh')  # time at next scr refresh
            fixation_1.setAutoDraw(True)
        if fixation_1.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > fixation_1.tStartRefresh + 1.0-frameTolerance:
                # keep track of stop time/frame for later
                fixation_1.tStop = t  # not accounting for scr refresh
                fixation_1.frameNStop = frameN  # exact frame index
                win.timeOnFlip(fixation_1, 'tStopRefresh')  # time at next scr refresh
                fixation_1.setAutoDraw(False)
        
        # check for quit (typically the Esc key)
        if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
            core.quit()
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in FixationComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()

    # -------Ending Routine "Fixation"-------
    for thisComponent in FixationComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    thisExp.addData('fixation_1.started', fixation_1.tStartRefresh)
    thisExp.addData('fixation_1.stopped', fixation_1.tStopRefresh)

    """
    Start 1-back Trials
    4x Trials
    """
    # set up handler to look after randomisation of conditions etc
    trials = data.TrialHandler(nReps=1, method='sequential', 
        extraInfo=expInfo, originPath=-1,
        trialList=data.importConditions('N-back-1.xlsx'),
        seed=None, name='trials')
    thisExp.addLoop(trials)  # add the loop to the experiment
    thisTrial = trials.trialList[0]  # so we can initialise stimuli with some values
    # abbreviate parameter names if possible (e.g. rgb = thisTrial.rgb)
    if thisTrial != None:
        for paramName in thisTrial:
            exec('{} = thisTrial[paramName]'.format(paramName))

    for thisTrial in trials:
        currentLoop = trials
        # abbreviate parameter names if possible (e.g. rgb = thisTrial.rgb)
        if thisTrial != None:
            for paramName in thisTrial:
                exec('{} = thisTrial[paramName]'.format(paramName))
        
        # ------Prepare to start Routine "N_back_1_Trial"-------
        continueRoutine = True
        routineTimer.add(2.000000)
        # update component parameters for each repeat
        target_square.setPos(location)
        response.keys = []
        response.rt = []
        _response_allKeys = []

        # keep track of which components have finished
        N_back_1_TrialComponents = [grid_lines, target_square, fixation_2, response]
        for thisComponent in N_back_1_TrialComponents:
            thisComponent.tStart = None
            thisComponent.tStop = None
            thisComponent.tStartRefresh = None
            thisComponent.tStopRefresh = None
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        # reset timers
        t = 0
        _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        N_back_1_TrialClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
        frameN = -1
        
        # -------Run Routine "N_back_1_Trial"-------
        while continueRoutine and routineTimer.getTime() > 0:
            # get current time
            t = N_back_1_TrialClock.getTime()
            tThisFlip = win.getFutureFlipTime(clock=N_back_1_TrialClock)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame
            
            # *grid_lines* updates
            if grid_lines.status == NOT_STARTED and tThisFlip >= 0-frameTolerance:
                # keep track of start time/frame for later
                grid_lines.frameNStart = frameN  # exact frame index
                grid_lines.tStart = t  # local t and not account for scr refresh
                grid_lines.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(grid_lines, 'tStartRefresh')  # time at next scr refresh
                grid_lines.setAutoDraw(True)
            if grid_lines.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > grid_lines.tStartRefresh + 2-frameTolerance:
                    # keep track of stop time/frame for later
                    grid_lines.tStop = t  # not accounting for scr refresh
                    grid_lines.frameNStop = frameN  # exact frame index
                    win.timeOnFlip(grid_lines, 'tStopRefresh')  # time at next scr refresh
                    grid_lines.setAutoDraw(False)
            
            # *target_square* updates
            if target_square.status == NOT_STARTED and tThisFlip >= 0-frameTolerance:
                # keep track of start time/frame for later
                target_square.frameNStart = frameN  # exact frame index
                target_square.tStart = t  # local t and not account for scr refresh
                target_square.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(target_square, 'tStartRefresh')  # time at next scr refresh
                target_square.setAutoDraw(True)
            if target_square.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > target_square.tStartRefresh + 1-frameTolerance:
                    # keep track of stop time/frame for later
                    target_square.tStop = t  # not accounting for scr refresh
                    target_square.frameNStop = frameN  # exact frame index
                    win.timeOnFlip(target_square, 'tStopRefresh')  # time at next scr refresh
                    target_square.setAutoDraw(False)
            
            # *fixation_2* updates
            if fixation_2.status == NOT_STARTED and tThisFlip >= 1-frameTolerance:
                # keep track of start time/frame for later
                fixation_2.frameNStart = frameN  # exact frame index
                fixation_2.tStart = t  # local t and not account for scr refresh
                fixation_2.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(fixation_2, 'tStartRefresh')  # time at next scr refresh
                fixation_2.setAutoDraw(True)
            if fixation_2.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > fixation_2.tStartRefresh + 1.0-frameTolerance:
                    # keep track of stop time/frame for later
                    fixation_2.tStop = t  # not accounting for scr refresh
                    fixation_2.frameNStop = frameN  # exact frame index
                    win.timeOnFlip(fixation_2, 'tStopRefresh')  # time at next scr refresh
                    fixation_2.setAutoDraw(False)
            
            # *response* updates
            waitOnFlip = False
            if response.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                response.frameNStart = frameN  # exact frame index
                response.tStart = t  # local t and not account for scr refresh
                response.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(response, 'tStartRefresh')  # time at next scr refresh
                response.status = STARTED
                # keyboard checking is just starting
                waitOnFlip = True
                win.callOnFlip(response.mouseClock.reset) # t=0 on next screen flip
                win.callOnFlip(response.clickReset) # t=0 on next screen flip
                prevButtonState = response.getPressed()[0]  # if button is down already this ISN'T a new click

            if response.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > response.tStartRefresh + 2-frameTolerance:
                    # keep track of stop time/frame for later
                    response.tStop = t  # not accounting for scr refresh
                    response.frameNStop = frameN  # exact frame index
                    win.timeOnFlip(response, 'tStopRefresh')  # time at next scr refresh
                    response.status = FINISHED
            if response.status == STARTED and not waitOnFlip:
                response.click, response.rt = response_2.getPressed(getTime = True)
                response.click = response.click[0]
                response.rt = response.rt[0]
                if response.click != prevButtonState:  # button state changed?
                    prevButtonState = response.click
                if response.click == 1 and gotValidClick == False:
                    print(str(response.click), str(response.rt))
                    if corrAns != None:
                        response.corr = 1
                        if biopac_exists:
                            biopac.setData(biopac, 0)
                            biopac.setData(biopac, nback_hit)
                    else:
                        response.corr = 0;  # failed to respond (incorrectly)
                        if biopac_exists:
                            biopac.setData(biopac, 0)
                            biopac.setData(biopac, nback_comiss) # mark comission error
                    gotValidClick = True

            # check for quit (typically the Esc key)
            if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
                core.quit()
            
            # check if all components have finished
            if not continueRoutine:  # a component has requested a forced-end of Routine
                break
            continueRoutine = False  # will revert to True if at least one component still running
            for thisComponent in N_back_1_TrialComponents:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished
            
            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()
        
        # -------Ending Routine "N_back_1_Trial"-------
        if biopac_exists:
            biopac.setData(biopac, 0)
        for thisComponent in N_back_1_TrialComponents:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        trials.addData('grid_lines.started', grid_lines.tStartRefresh)
        trials.addData('grid_lines.stopped', grid_lines.tStopRefresh)
        trials.addData('target_square.started', target_square.tStartRefresh)
        trials.addData('target_square.stopped', target_square.tStopRefresh)
        trials.addData('fixation_2.started', fixation_2.tStartRefresh)
        trials.addData('fixation_2.stopped', fixation_2.tStopRefresh)
        # store data for trials (TrialHandler)
        trials.addData('response.keys',response.keys)
        trials.addData('response.corr', response.corr)
        
        trials.addData('response.x', x)
        trials.addData('response.y', y)
        trials.addData('response.leftButton', response.click)

        if response.keys != None:  # we had a response
            trials.addData('response.rt', response.rt)
        trials.addData('response.click',response.click)
        trials.addData('response.corr', response.corr)
        trials.addData('response.started', response.tStartRefresh)
        trials.addData('response.stopped', response.tStopRefresh)
        thisExp.nextEntry()
        
        # completed 4 repeats of 'trials'

    """
    2-Back Prompt
    """

    """
    Fixation Cross
    """
    # ------Prepare to start Routine "Fixation"-------
    continueRoutine = True
    routineTimer.add(1.000000)
    # update component parameters for each repeat
    # keep track of which components have finished
    FixationComponents = [fixation_1]
    for thisComponent in FixationComponents:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    FixationClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    frameN = -1

    # -------Run Routine "Fixation"-------
    while continueRoutine and routineTimer.getTime() > 0:
        # get current time
        t = FixationClock.getTime()
        tThisFlip = win.getFutureFlipTime(clock=FixationClock)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *fixation_1* updates
        if fixation_1.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            fixation_1.frameNStart = frameN  # exact frame index
            fixation_1.tStart = t  # local t and not account for scr refresh
            fixation_1.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(fixation_1, 'tStartRefresh')  # time at next scr refresh
            fixation_1.setAutoDraw(True)
        if fixation_1.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > fixation_1.tStartRefresh + 1.0-frameTolerance:
                # keep track of stop time/frame for later
                fixation_1.tStop = t  # not accounting for scr refresh
                fixation_1.frameNStop = frameN  # exact frame index
                win.timeOnFlip(fixation_1, 'tStopRefresh')  # time at next scr refresh
                fixation_1.setAutoDraw(False)
        
        # check for quit (typically the Esc key)
        if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
            core.quit()
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in FixationComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()

    # -------Ending Routine "Fixation"-------
    for thisComponent in FixationComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    thisExp.addData('fixation_1.started', fixation_1.tStartRefresh)
    thisExp.addData('fixation_1.stopped', fixation_1.tStopRefresh)

    """ 
    7. 2-Back Real
    """
    for thisTrial_2 in trials_2:
        currentLoop = trials_2
        # abbreviate parameter names if possible (e.g. rgb = thisTrial_2.rgb)
        if thisTrial_2 != None:
            for paramName in thisTrial_2:
                exec('{} = thisTrial_2[paramName]'.format(paramName))
        
        # ------Prepare to start Routine "N_back_2_trials"-------
        continueRoutine = True
        routineTimer.add(2.000000)
        # update component parameters for each repeat
        target_square_2.setPos(location)
        response_2 = event.Mouse(win=win, visible=False) # Re-initialize
        response_2.click = []
        response_2.rt = []
        response_2.corr = []
        x, y = [None, None]
        gotValidClick = False  # until a click is received
        
        # keep track of which components have finished
        N_back_2_trialsComponents = [grid_lines_2, target_square_2, fixation_3, response_2]
        for thisComponent in N_back_2_trialsComponents:
            thisComponent.tStart = None
            thisComponent.tStop = None
            thisComponent.tStartRefresh = None
            thisComponent.tStopRefresh = None
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        # reset timers
        t = 0
        _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        N_back_2_trialsClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
        frameN = -1
        
        # -------Run Routine "N_back_2_trials"-------
        while continueRoutine and routineTimer.getTime() > 0:
            # get current time
            t = N_back_2_trialsClock.getTime()
            tThisFlip = win.getFutureFlipTime(clock=N_back_2_trialsClock)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame

            # *response_2* updates
            waitOnFlip = False
            if response_2.status == NOT_STARTED and t >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                response_2.frameNStart = frameN  # exact frame index
                response_2.tStart = t  # local t and not account for scr refresh
                response_2.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(response_2, 'tStartRefresh')  # time at next scr refresh
                response_2.status = STARTED
                waitOnFlip = True
                win.callOnFlip(response_2.mouseClock.reset) # t=0 on next screen flip
                win.callOnFlip(response_2.clickReset) # t=0 on next screen flip
                prevButtonState = response_2.getPressed()[0]  # if button is down already this ISN'T a new click
            if response_2.status == STARTED:  # only update if started and not finished!
                if tThisFlipGlobal > response_2.tStartRefresh + 2-frameTolerance:
                    # keep track of stop time/frame for later
                    response_2.tStop = t  # not accounting for scr refresh
                    response_2.frameNStop = frameN  # exact frame index
                    win.timeOnFlip(response_2, 'tStopRefresh')  # time at next scr refresh
                    response_2.status = FINISHED
            if response_2.status == STARTED and not waitOnFlip:
                response_2.click, response_2.rt = response_2.getPressed(getTime = True)
                response_2.click = response_2.click[0]
                response_2.rt = response_2.rt[0]
                if response_2.click != prevButtonState:  # button state changed?
                    prevButtonState = response_2.click
                if response_2.click == 1 and gotValidClick == False:
                    print(str(response_2.click), str(response_2.rt))
                    if corrAns != None:
                        response_2.corr = 1
                        if biopac_exists:
                            biopac.setData(biopac, 0)
                            biopac.setData(biopac, nback_hit)
                    else:
                        response_2.corr = 0;  # failed to respond (incorrectly)
                        if biopac_exists:
                            biopac.setData(biopac, 0)
                            biopac.setData(biopac, nback_comiss) # mark comission error
                    gotValidClick = True
            
            # *grid_lines_2* updates
            if grid_lines_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                grid_lines_2.frameNStart = frameN  # exact frame index
                grid_lines_2.tStart = t  # local t and not account for scr refresh
                grid_lines_2.tStartRefresh = tThisFlipGlobal  # on global time
                if biopac_exists:
                    win.callOnFlip(biopac.setData, biopac, 0)
                    win.callOnFlip(biopac.setData, biopac, nback_trial_start)
                win.timeOnFlip(grid_lines_2, 'tStartRefresh')  # time at next scr refresh
                grid_lines_2.setAutoDraw(True)
            if grid_lines_2.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > grid_lines_2.tStartRefresh + 2-frameTolerance:
                    # keep track of stop time/frame for later
                    grid_lines_2.tStop = t  # not accounting for scr refresh
                    grid_lines_2.frameNStop = frameN  # exact frame index
                    win.timeOnFlip(grid_lines_2, 'tStopRefresh')  # time at next scr refresh
                    grid_lines_2.setAutoDraw(False)
            
            # *target_square_2* updates
            if target_square_2.status == NOT_STARTED and tThisFlip >= 0-frameTolerance:
                # keep track of start time/frame for later
                target_square_2.frameNStart = frameN  # exact frame index
                target_square_2.tStart = t  # local t and not account for scr refresh
                target_square_2.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(target_square_2, 'tStartRefresh')  # time at next scr refresh
                target_square_2.setAutoDraw(True)
            if target_square_2.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > target_square_2.tStartRefresh + 1.0-frameTolerance:
                    # keep track of stop time/frame for later
                    target_square_2.tStop = t  # not accounting for scr refresh
                    target_square_2.frameNStop = frameN  # exact frame index
                    win.timeOnFlip(target_square_2, 'tStopRefresh')  # time at next scr refresh
                    target_square_2.setAutoDraw(False)
            
            # *fixation_3* updates
            if fixation_3.status == NOT_STARTED and tThisFlip >= 1-frameTolerance:
                # keep track of start time/frame for later
                fixation_3.frameNStart = frameN  # exact frame index
                fixation_3.tStart = t  # local t and not account for scr refresh
                fixation_3.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(fixation_3, 'tStartRefresh')  # time at next scr refresh
                fixation_3.setAutoDraw(True)
            if fixation_3.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > fixation_3.tStartRefresh + 1-frameTolerance:
                    # keep track of stop time/frame for later
                    fixation_3.tStop = t  # not accounting for scr refresh
                    fixation_3.frameNStop = frameN  # exact frame index
                    win.timeOnFlip(fixation_3, 'tStopRefresh')  # time at next scr refresh
                    fixation_3.setAutoDraw(False)

            # # Autoresponder
            # if t >= thisSimKey.rt and autorespond == 1:
            #     _response_2_allKeys.extend([thisSimKey])

            # check for quit (typically the Esc key)
            if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
                core.quit()
            
            # check if all components have finished
            if not continueRoutine:  # a component has requested a forced-end of Routine
                break
            continueRoutine = False  # will revert to True if at least one component still running
            for thisComponent in N_back_2_trialsComponents:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished
            
            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()
        
        # -------Ending Routine "N_back_2_trials"-------
        if biopac_exists:
            biopac.setData(biopac, 0)
        for thisComponent in N_back_2_trialsComponents:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)

        # Check non-response
        if response_2.click == 0 and gotValidClick == False:
            response_2.rt = None
            if str(corrAns).lower() == 'none':
                response_2.corr = 1;  # correct non-response
            else:
                response_2.corr = 0;  # failed to respond (incorrectly)

        trials_2.addData('response_2.x', x)
        trials_2.addData('response_2.y', y)
        trials_2.addData('response_2.leftButton', response_2.click)
        trials_2.addData('grid_lines_2.started', grid_lines_2.tStartRefresh)
        trials_2.addData('grid_lines_2.stopped', grid_lines_2.tStopRefresh)
        trials_2.addData('target_square_2.started', target_square_2.tStartRefresh)
        trials_2.addData('target_square_2.stopped', target_square_2.tStopRefresh)
        trials_2.addData('fixation_3.started', fixation_3.tStartRefresh)
        trials_2.addData('fixation_3.stopped', fixation_3.tStopRefresh)

        if response_2.click == 1:  # we had a response
            trials_2.addData('response_2.rt', response_2.rt)

        # store data for trials_2 (TrialHandler)
        trials_2.addData('response_2.click',response_2.click)
        trials_2.addData('response_2.corr', response_2.corr)
        trials_2.addData('response_2.started', response_2.tStartRefresh)
        trials_2.addData('response_2.stopped', response_2.tStopRefresh)
        nback_bids_trial = []
        nback_bids_trial.extend((order_no, grid_lines_2.tStartRefresh, t, response_2.rt, response_2.corr))
        nback_bids.append(nback_bids_trial)

        thisExp.nextEntry()
        
    # completed 1 repeats of 'trials_2'

    """
    1-Back Prompt
    """



    """ 
    7. 1-Back Real
    """






    """
    8. End of Run, Wait for Experimenter instructions to begin next run
    """   
    message = visual.TextStim(win, text=in_between_run_msg, height=0.05, units='height')
    message.draw()
    win.callOnFlip(print, "Awaiting Experimenter to start next run...\nPress [e] to continue")
    if biopac_exists:
        win.callOnFlip(biopac.setData, biopac,0)
        win.callOnFlip(biopac.setData, biopac,second_run)
        win.callOnFlip(biopac.setData,biopac,0)
    win.flip()
    # Autoresponder
    if autorespond != 1:
        event.waitKeys(keyList = 'e')

win.flip()

"""
9. Save data into Excel and .CSV formats and Tying up Loose Ends
""" 
if biopac_exists:
    biopac.setData(biopac,0)
    biopac.setData(biopac,end_task)
    biopac.setData(biopac,0)
nback_bids_data = pd.DataFrame(nback_bids, columns = ['order', 'onset', 'duration', 'rt', 'correct'])

bids_filename = sub_dir + os.sep + u'sub-%05d_ses-%02d_task-%s_acq-order%d_events.tsv' % (int(expInfo['subject number']), int(expInfo['session']), 'nback', order_no)
nback_bids_data.to_csv(bids_filename, sep="\t")



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