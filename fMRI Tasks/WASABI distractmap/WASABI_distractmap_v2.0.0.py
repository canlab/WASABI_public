
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

The paradigm will generate these files of name:
1x sub-XXXX_ses-XX_task-Practice1back_events.tsv
1x sub-XXXX_ses-XX_task-Practice2back_events.tsv
8x sub-XXXX_ses-XX_task-distractmap_acq-[bodySite]_run-XX_events.tsv

x16 trials per file with the following
headers:
'onset','duration','rt','response','correct','attempt','condition'

'onset', 'duration', 'rt', 'response', 'correct', 'bodySite', 'temperature', 'condition', 'pretrial-jitter', 'posttrial-jitter'

'onset', 'duration', 'bodySite', 'intensity', 'temperature', 'condition', 'posttrial-jitter'

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

import random

__author__ = "Michael Sun"
__version__ = "2.0.0"
__email__ = "msun@dartmouth.edu"
__status__ = "Production"

"""  
0b. Beta-Testing Togglers
Set to 1 during development, 0 during production
"""
debug = 0
cheat = 0
autorespond = 0
# Device togglers
biopac_exists = 1
thermode_exists = 1

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

def rescale(self, width=0, height=0, operation='', units=None, log=True):
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
task_ID=7
intro=193

bodymapping_instruction=15
leftface_heat=17
rightface_heat=18
leftarm_heat=19
rightarm_heat=20
leftleg_heat=21
rightleg_heat=22
chest_heat=23
abdomen_heat=24

nback_instructions=186
nback_fixation=187
nback_trial_start=188
next_run=189
nback_hit=190
nback_comiss=191

nback_feedback_pos=194
nback_feedback_miss=195
nback_feedback_neg=196

intensity_rating=43

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
stimuli_dir = main_dir + os.sep + "stimuli"
instructions_dir = main_dir + os.sep + 'instruction_stim'
nback_dir = main_dir + os.sep + "nbackorder"

# Brings up the Calibration/Data folder to load the appropriate calibration data right away.
calibration_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir, os.path.pardir, 'Calibration', 'data')

"""
2. Start Experimental Dialog Boxes
"""
# Upload participant file: Browse for file
# Store info about the experiment session
psychopyVersion = '2020.2.10'
expName = 'distractmap'  # from the Builder filename that created this script
if debug == 1:
    expInfo = {
    'subject number': '99',
    'gender': 'm',
    'distractMap first- or second-half (1 or 2)': '1', 
    'session': '99',
    'handedness': 'r', 
    'scanner': 'MS'
    }
else:
    expInfo = {
    'subject number': '', 
    'gender': '',
    'distractMap first- or second-half (1 or 2)': '',
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

# Load the subject's calibration file and ensure that it is valid
if debug==1:
    expInfo = {
        'subject number': '999', 
        'gender': 'm',
        'distractMap first- or second-half (1 or 2)': '2',
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
                distractmap_num = str(1)
                ses_num = str(1) 
                expInfo2 = {
                'distractMap first- or second-half (1 or 2)': distractmap_num,
                'session': ses_num,
                'scanner': ''
                }
                dlg2 = gui.DlgFromDict(title="WASABI Distraction Map Scan", dictionary=expInfo2, sortKeys=False) 
                expInfo['session'] = expInfo2['session']
                expInfo['scanner'] = expInfo2['scanner']
                bodySites = bodySites.strip('][').replace("'","").split(', ')
                if expInfo2['distractMap first- or second-half (1 or 2)'] == '1':
                    bodySites = bodySites[0:4]
                if expInfo2['distractMap first- or second-half (1 or 2)'] == '2':
                    bodySites = bodySites[4:8]
                expInfo['distractMap first- or second-half (1 or 2)'] = expInfo2['distractMap first- or second-half (1 or 2)']
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
        dlg2 = gui.DlgFromDict(title="WASABI DistractMap Scan", dictionary=expInfo, sortKeys=False)
        if dlg2.OK == False:
            core.quit()  # user pressed cancel
        pphDlg = gui.DlgFromDict(participant_settingsHeat, 
                                title='Participant Heat Parameters')
        if pphDlg.OK == False:
            core.quit()

expInfo['date'] = data.getDateStr()  # add a simple timestamp
expInfo['psychopyVersion'] = psychopyVersion

if expInfo['distractMap first- or second-half (1 or 2)'] == '1':
    expName = 'distractmap1'
if expInfo['distractMap first- or second-half (1 or 2)'] == '2':
    expName = 'distractmap2'
expInfo['expName'] = expName

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
4. Prepare Experimental Dictionaries for Body-Site Cues and Medoc Temperature Programs
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
                        "Right Face": rightface_heat, 
                        "Left Arm": leftarm_heat, 
                        "Right Arm": rightarm_heat, 
                        "Left Leg": leftleg_heat, 
                        "Right Leg": rightleg_heat, 
                        "Chest": chest_heat,
                        "Abdomen": abdomen_heat 
                        }

# Set up a dictionary for all the configured Medoc programs for the main thermode
thermode1_temp2program = {}
with open("thermode1_programs.txt") as f:
    for line in f:
       (key, val) = line.split()
       thermode1_temp2program[float(key)] = int(val)

"""
5. Create Body-Site Pairs for each run for this participant
"""
try:
    bodySites
except NameError:
    bodySites_exists = False
else:
    bodySites_exists = True
if bodySites_exists == False:
    bodySites = ["Left Face", "Right Face", "Left Arm", "Right Arm", "Left Leg", "Right Leg", "Chest", "Abdomen"]
    random.shuffle(bodySites)
    bodySites = bodySites[0:4]

random.shuffle(bodySites)

expInfo['body_site_order'] = str(bodySites)

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

Practice_1back_trial = []
Practice_1back = []
Practice_2back_trial = []
Practice_2back = []

distractmap_bids_trial = []
distractmap_bids = []

# rating_bids_trial = []
# rating_bids = []

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
    font='Arial', wrapWidth=1.75,
    pos=(0, 0.0), units='height', height=0.05, 
    color='white', colorSpace='rgb', opacity=1)
NbackInstructionImg = visual.ImageStim(
    win=win,
    name='NbackInstructionImg', 
    image= 'instruction_stim/1.png', mask=None,
    ori=0, pos=(0, 0.15), size=(0.3, 0.3),
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

ClickPrompt = visual.TextStim(win=win, name='ClickPrompt',
    text='',
    font='Arial',
    pos=(0, -.4), units='height', height=0.05, 
    color='white', colorSpace='rgb', opacity=1)

NbackStart = keyboard.Keyboard()

# Initialize components for Routine "ButtonTest"
ButtonTestClock = core.Clock()
box1Text = visual.TextStim(win=win, name='box1Text',
    text="Button/key 1 \nindicates \"Yes\", a match.",
    font='Arial',
    pos=(0, 0.1), units='height', height=0.05, 
    color='white', colorSpace='rgb', opacity=1)
box2Text = visual.TextStim(win=win, name='box2Text',
    text="Button/key 2 \nindicates \"No\", a mismatch.",
    font='Arial',
    pos=(0, -0.1), units='height', height=0.05, 
    color='white', colorSpace='rgb', opacity=1)
box1Check = visual.TextStim(win=win, name='box1Check',
    text="X",
    font='Arial',
    pos=(-.2, .15), units='height', height=0.05, 
    color='red', colorSpace='rgb', opacity=1)
box2Check = visual.TextStim(win=win, name='box2Check',
    text="X",
    font='Arial',
    pos=(-.2, -0.05), units='height', height=0.05, 
    color='red', colorSpace='rgb', opacity=1)
box1 = visual.Rect(
    win=win, name='box1',
    width=(0.05, 0.05)[0], height=(0.05, 0.05)[1],
    ori=0, 
    pos=(-0.2, 0.15),
    lineWidth=1, lineColorSpace='rgb',
    fillColorSpace='rgb', lineColor=[1,1,1], fillColor=[1,1,1],
    opacity=1, depth=0.0, interpolate=True)
box2 = visual.Rect(
    win=win, name='box2',
    width=(0.05, 0.05)[0], height=(0.05, 0.05)[1],
    ori=0, 
    pos=(-0.2, -0.05),
    lineWidth=1, lineColorSpace='rgb',
    fillColorSpace='rgb', lineColor=[1,1,1], fillColor=[1,1,1],
    opacity=1, depth=0.0, interpolate=True)
mouse = event.Mouse(win=win, visible=False)
x, y = [None, None]
mouse.mouseClock = core.Clock()

continueText = visual.TextStim(win=win, name='continueText',
    text='Experimenter press [Space] to continue.',
    font='Arial',
    pos=(0, -.35), units='height', height=0.05, 
    color='white', colorSpace='rgb', opacity=1)
# continueKey = keyboard.Keyboard()

incorrect_text = "Incorrect!"
noresponse_text = "No Response!"
correct_text = "Correct!"

Feedback = visual.TextStim(win=win, name='Feedback',
    text="",
    font='Arial',
    pos=(0, -0.35), units='height', height=0.05, 
    color='white', colorSpace='rgb', opacity=1)

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
N_back_1_TrialClock = core.Clock()
grid_lines = visual.ImageStim(
    win=win,
    name='grid_lines', 
    image='grid.png', mask=None,
    ori=0, pos=(0, 0), size=(0.6, 0.6),
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=0.0)
target_square = visual.Rect(
    win=win, name='target_square',
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
response = event.Mouse(win=win)
response.mouseClock = core.Clock()

# Initialize components for Routine "N_back_2_trials"
N_back_2_TrialClock = core.Clock()
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

# Initialize components for Routine "ScoreReport"
ScoreReportClock = core.Clock()
ScoreReportText = visual.TextStim(win=win, name='ScoreReportText',
    text='This text is for reporting your score performance.',
    font='Arial', wrapWidth=1.75,
    pos=(0, 0.0), units='height', height=0.05, 
    color='white', colorSpace='rgb', opacity=1)
ScoreReportResponse = keyboard.Keyboard()

# Initialize components for Routine "BodySiteInstruction"
BodySiteInstructionClock = core.Clock()
BodySiteInstructionRead = keyboard.Keyboard()
BodySiteInstructionText = visual.TextStim(win, name='BodySiteInstructionText', 
    text="Experimenter: Please place thermodes on the designated body-site.",
    font = 'Arial',
    pos=(0, -.2), height=0.05, wrapWidth=1.6, ori=0, 
    color='white', colorSpace='rgb', opacity=1, 
    languageStyle='LTR',
    depth=0.0, 
    anchorHoriz='center')
BodySiteImg = visual.ImageStim(
    win=win,
    name='BodySiteImg', 
    mask=None,
    ori=0, pos=(0, 0), size=(.40,.40),
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=512, interpolate=True, depth=0.0)

# Initialize components for each Rating
ratingTime = 5 # Rating Time limit in seconds
TIME_INTERVAL = 0.005   # Speed at which slider ratings udpate
ratingScaleWidth=1.5
ratingScaleHeight=.4
sliderMin = -.75
sliderMax = .75
intensityText = "How intense was that overall?"
black_triangle_verts = [(sliderMin, .2),    # left point
                        (sliderMax, .2),    # right point
                        (0, -.2)]           # bottom-point
# Initialize components for Routine "IntensityRating"
IntensityRatingClock = core.Clock()
IntensityMouse = event.Mouse(win=win, visible=False)
IntensityMouse.mouseClock = core.Clock()
IntensityRating = visual.Rect(win, height=ratingScaleHeight, width=abs(sliderMin), pos= [sliderMin/2, -.1], fillColor='red', lineColor='black')
IntensityBlackTriangle = visual.ShapeStim(
    win, 
    vertices=[(sliderMin, .2), # left point
            (sliderMax, .2),     # right point
            (sliderMin, -.2)],   # bottom-point, 
    fillColor='black', lineColor='black')
IntensityAnchors = visual.ImageStim(
    win=win,
    image= os.sep.join([stimuli_dir,"ratingscale","intensityScale.png"]),
    name='intensityAnchors', 
    mask=None,
    ori=0, pos=(0, -0.09), size=(1.5, .4),
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=512, interpolate=True, depth=0.0)
IntensityPrompt = visual.TextStim(win, name='IntensityPrompt', 
    text=intensityText,
    font = 'Arial',
    pos=(0, 0.3), height=0.05, wrapWidth=None, ori=0, 
    color='white', colorSpace='rgb', opacity=1, 
    languageStyle='LTR',
    depth=0.0,
    anchorHoriz='center')

# Create some handy timers
globalClock = core.Clock()  # to track the time since experiment started
routineTimer = core.CountdownTimer()  # to track time remaining of each (non-slip) routine 

OnebackFiles = ["N-back-1_1.xlsx", "N-back-1_2.xlsx", "N-back-1_3.xlsx", "N-back-1_4.xlsx", "N-back-1_5.xlsx", "N-back-1_6.xlsx", "N-back-1_7.xlsx", "N-back-1_8.xlsx"]
TwobackFiles = ["N-back-2_1.xlsx", "N-back-2_2.xlsx", "N-back-2_3.xlsx", "N-back-2_4.xlsx", "N-back-2_5.xlsx", "N-back-2_6.xlsx", "N-back-2_7.xlsx", "N-back-2_8.xlsx"]

if biopac_exists:
    biopac.setData(biopac, 0)
    biopac.setData(biopac, task_ID) # Start demarcation of the T1 task in Biopac Acqknowledge

win.mouseVisible = False

"""
6. Welcome Instructions
"""
NbackInstructionText1 = "Welcome to the n-back task \n\n\nPlease read the following instructions \nvery carefully.\n\n\n\nExperimenter press [Space] to continue."
NbackInstructionText2 = "During the task you will be presented a white square in one of nine positions on a grid. \n\n\n\n\n\n\nDepending on the instruction, your task is to indicate whether the \ncurrent position is the same as either:\nthe position on the last trial\nor the position two trials ago\n\n\nExperimenter press [Space] to continue."
NbackInstructionText3 = "Between each trial, a fixation cross will appear in the middle of the grid. \n\n\n\n\n\n\n\n\nYou do not need to respond during this time. \nSimply wait for the next trial.\n\n\n\nExperimenter press [Space] to continue."
NbackInstructionText4 = "\n1-back\n\n\n\n\n\n\n\nDuring 1-back you will have to indicate whether the current position matches the position that was presented in the last trial, by either pressing the \"yes\" button (left click) or the \"no\" button (right click).\n\n\nExperimenter press [Space] to show an example."

NbackInstructions.setText(NbackInstructionText1)
NbackInstructions.draw()
win.flip()
# event.waitKeys(keyList = 'space')
continueRoutine = True
event.clearEvents()
while continueRoutine == True:
    if 'space' in event.getKeys(keyList = 'space'):
        continueRoutine = False

NbackInstructions.setText(NbackInstructionText2)
NbackInstructions.draw()
NbackInstructionImg.setImage(os.path.join(instructions_dir, '1.png'))
NbackInstructionImg.draw()
win.flip()
# event.waitKeys(keyList = 'space')
continueRoutine = True
event.clearEvents()
while continueRoutine == True:
    if 'space' in event.getKeys(keyList = 'space'):
        continueRoutine = False

NbackInstructions.setText(NbackInstructionText3)
NbackInstructions.draw()
NbackInstructionImg.setImage(os.path.join(instructions_dir, '2.png'))
NbackInstructionImg.draw()
win.flip()
# event.waitKeys(keyList = 'space')
continueRoutine = True
event.clearEvents()
while continueRoutine == True:
    if 'space' in event.getKeys(keyList = 'space'):
        continueRoutine = False
NbackInstructionImg.setAutoDraw(False)
NbackInstructions.setText(NbackInstructionText4)
NbackInstructions.draw()
NbackInstructionImg.draw()
win.flip()
#event.waitKeys(keyList = 'space')
continueRoutine = True
event.clearEvents()
while continueRoutine == True:
    if 'space' in event.getKeys(keyList = 'space'):
        continueRoutine = False
routineTimer.reset()

"""
7. Button Test
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

# keep track of which components have finished
trialComponents = [box1Text, box2Text, box1, box2, box1Check, box2Check, mouse, continueText]
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
# trialClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
frameN = -1

# -------Run Routine "ButtonTest"-------
while continueRoutine:
    # get current time
    t = ButtonTestClock.getTime()
    tThisFlip = win.getFutureFlipTime(clock=ButtonTestClock)
    tThisFlipGlobal = win.getFutureFlipTime(clock=None)
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame

    # *box1* updates
    if box1.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        box1Text.setAutoDraw(True)
        box1.setAutoDraw(True)
    
    # *box2* updates
    if box2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        box2Text.setAutoDraw(True)
        box2.setAutoDraw(True)
    
    if mouse.getPressed()[0] == 0 & mouse.getPressed()[2] == 0:
        mouseDown = False
        
    if mouse.getPressed()[0]==1 and box1.name not in clicked and not mouseDown:
        # box1.color = "black"        # replace this with a check mark?
        box1Check.setAutoDraw(True)
        clicked.append(box1.name)
        mouseDown = True  
    if mouse.getPressed()[2]==1 and box2.name not in clicked and not mouseDown:
        # box2.color = "black"        # replace this with a check mark?
        box2Check.setAutoDraw(True)
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
    
    if box1.name in clicked and box2.name in clicked:
        continueText.setAutoDraw(True)
        win.flip()
        continueRoutine = False


    # check for quit (typically the Esc key)
    if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
        core.quit()
    
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        win.flip()
        # event.waitKeys(keyList = 'space')
        continueRoutine = True
        event.clearEvents()
        while continueRoutine == True:
            if 'space' in event.getKeys(keyList = 'space'):
                continueRoutine = False        
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in trialComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

# -------Ending Routine "ButtonTest"-------
for thisComponent in trialComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)
routineTimer.reset()

"""
8. Start Practice 1-back
"""
turns = 0
score = 0
while turns <= 3 and score <= 70:
    NbackInstructionText5 = "In the below 1-back example you should not respond to the first trial (as there is no trial before it), make a \"no\" response (right click) on trial 2, since the positions on trials 1 and 2 do not match, and make a \"yes\" response on trial 3, since the position is the same as the position on trial 2.\n\n\n\n\n\n\n\n\n\n"
    ClickToContinueText = "Click to continue"
    NbackInstructionText6 = "First, we will practice some trials so that you can get used to the procedure.\nAfter each response you'll see whether your response was correct, incorrect, or whether you forgot to respond.\n\n\n\n\n\n\n\n\nGood Luck!"
    ClickToStartText = "Click to start practice"

    InstructionImageArray = ['7.png', '8.png', '9.png', '10.png', '11.png', '12.png', '13.png', '14.png']
    iteration = 0
    NbackInstructions.setText(NbackInstructionText5)
    NbackInstructions.setAutoDraw(True)
    ClickPrompt.setText(ClickToContinueText)
    mouse = event.Mouse(win=win, visible=False)
    prevButtonState = mouse.getPressed()  # if button is down already this ISN'T a new click
    buttons = prevButtonState

    NbackInstructionWideImg.setImage(os.path.join(instructions_dir, InstructionImageArray[0]))
    NbackInstructionWideImg.draw()
    if biopac_exists:
        biopac.setData(biopac, 0)
        biopac.setData(biopac, nback_instructions)
    win.flip()

    continueRoutine = True
    i = 0
    stimTimer = core.CountdownTimer(1)    
    while (continueRoutine == True):
        if iteration == 1 and mouse.getPressed()[0] == 1:
            continueRoutine = False
            break
        if i > len(InstructionImageArray)-1:
            iteration = 1
            i = 0
            ClickPrompt.setAutoDraw(True)
        if stimTimer.getTime() < 0:
            stimTimer = core.CountdownTimer(1)
            NbackInstructionWideImg.setImage(os.path.join(instructions_dir, InstructionImageArray[i]))
            i=i+1
        NbackInstructionWideImg.setAutoDraw(True)
        win.flip()

    NbackInstructionWideImg.setImage(os.path.join(instructions_dir, InstructionImageArray[len(InstructionImageArray)-1])) # Stay on the last image
    NbackInstructions.setText(NbackInstructionText6)
    NbackInstructions.setAutoDraw(True)
    win.flip()
    timer = core.CountdownTimer()
    timer.add(2)
    while timer.getTime() > 0:
        continue          

    mouse = event.Mouse(win=win, visible=False)
    while(mouse.getPressed()[0] != 1):
        ClickPrompt.setText(ClickToStartText)
        ClickPrompt.setAutoDraw(True)
        win.flip()

    # Wipe the screen
    ClickPrompt.setAutoDraw(False)
    NbackInstructions.setAutoDraw(False)
    NbackInstructionWideImg.setAutoDraw(False)
    if biopac_exists:
        biopac.setData(biopac, 0)
    win.flip()
    routineTimer.reset()

    ########################
    # Practice 1-back Begins
    ########################
    correct = 0
    score = 0

    """ 
    8i. Pre-1-Back Task Fixation Cross
    """
    # ------Prepare to start Routine "Fixation"-------
    continueRoutine = True
    routineTimer.add(1.000000)      # 1 second pre-task fixation
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
            if biopac_exists:
                win.callOnFlip(biopac.setData, biopac, 0)
                win.callOnFlip(biopac.setData, biopac, nback_fixation)
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
    if biopac_exists:
        win.callOnFlip(biopac.setData, biopac, 0)
    for thisComponent in FixationComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    thisExp.addData('fixation_1.started', fixation_1.tStartRefresh)
    thisExp.addData('fixation_1.stopped', fixation_1.tStopRefresh)
    routineTimer.reset()

    """ 
    8ii. Practice 1-back Start
    """
    # Feedback Text
    incorrect_text = "Incorrect!"
    noresponse_text = "No Response!"
    correct_text = "Correct!"

    # set up handler to look after randomisation of conditions etc
    Nback1 = os.sep.join([nback_dir, "Practice_N-back-1.xlsx"])
    trials = data.TrialHandler(nReps=1, method='sequential', 
        extraInfo=expInfo, originPath=-1,
        trialList=data.importConditions(Nback1),
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
        routineTimer.add(2.000000)          # Each trial is 2 seconds
        feedbacktype = "none"
        # update component parameters for each repeat
        target_square.setPos(location)
        response.rt = []

        gotValidClick = False  # until a click is received

        # keep track of which components have finished
        N_back_1_TrialComponents = [grid_lines, target_square, fixation_2, response, Feedback]
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
            # gotValidClick = False
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
                if biopac_exists == 1:
                    win.callOnFlip(biopac.setData, biopac, 0)
                    win.callOnFlip(biopac.setData, biopac, nback_trial_start)
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
                prevButtonState = response.getPressed()  # if button is down already this ISN'T a new click
            if response.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > response.tStartRefresh + 2-frameTolerance:
                    # keep track of stop time/frame for later
                    response.tStop = t  # not accounting for scr refresh
                    response.frameNStop = frameN  # exact frame index
                    win.timeOnFlip(response, 'tStopRefresh')  # time at next scr refresh
                    response.status = FINISHED
            if response.status == STARTED and not waitOnFlip:
                response.click, response.rt = response.getPressed(getTime = True)
                response.click_left = response.click[0]
                response.click_right = response.click[2]
                response.rt_left = response.rt[0]
                response.rt_right = response.rt[2]
                if response.click_left != prevButtonState[0] or response.click_right != prevButtonState[2]:  # button state changed?
                    prevButtonState = response.click
                    if (response.click_left == 1 or response.click_right == 1) and gotValidClick == False:
                        print(str(response.click), str(response.rt))
                        if (corrAns == 1 and response.click_left == 1) or (corrAns == 0 and response.click_right == 1):
                            response.corr = 1
                            correct = correct + 1
                            Feedback.setText(correct_text)
                            feedbacktype = "pos"
                            if biopac_exists:
                                biopac.setData(biopac, 0)
                                biopac.setData(biopac, nback_hit)
                        else:
                            response.corr = 0
                            Feedback.setText(incorrect_text)
                            feedbacktype = "neg"
                            if biopac_exists:
                                biopac.setData(biopac, 0)
                                biopac.setData(biopac, nback_comiss) # mark comission error
                        if response.click_left == 1: 
                            mouse_response = 0; 
                            mouse_response_rt = response.rt_left
                        elif response.click_right == 1: 
                            mouse_response = 2 
                            mouse_response_rt = response.rt_right
                        gotValidClick = True
                elif response.click_left == 0 and response.click_right == 0 and gotValidClick==False:  # No response was made
                    mouse_response = None
                    mouse_response_rt = None
                    if str(corrAns).lower() != 'none':
                        Feedback.setText(noresponse_text)
                        feedbacktype = "miss"
                    else:
                        Feedback.setText("")
                
            # *Feedback* updates
            waitOnFlip = False
            if Feedback.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                Feedback.frameNStart = frameN  # exact frame index
                Feedback.tStart = t  # local t and not account for scr refresh
                Feedback.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(Feedback, 'tStartRefresh')  # time at next scr refresh
                Feedback.status = STARTED
                Feedback.setAutoDraw(False)

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
                if 1 < N_back_1_TrialClock.getTime() < 1.75:
                    Feedback.draw()
                    if biopac_exists:
                        if feedbacktype == "pos":
                            biopac.setData(biopac, nback_feedback_pos)
                        if feedbacktype == "neg":
                            biopac.setData(biopac, nback_feedback_neg)
                        if feedbacktype == "miss":
                            biopac.setData(biopac, nback_feedback_miss)
                else:
                    if biopac_exists:
                        biopac.setData(biopac, 0)
                win.flip()
        
        # -------Ending Routine "N_back_1_Trial"-------
        if biopac_exists:
            biopac.setData(biopac, 0)
        for thisComponent in N_back_1_TrialComponents:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        
        if gotValidClick==False:  # No response was made
            response_2.rt = None
            if str(corrAns).lower() == 'none':
                response.corr=1
                correct = correct + 1
            else:
                response.corr = 0;  # failed to respond (incorrectly)
                Feedback.setText(noresponse_text)

        trials.addData('grid_lines.started', grid_lines.tStartRefresh)
        trials.addData('grid_lines.stopped', grid_lines.tStopRefresh)
        trials.addData('target_square.started', target_square.tStartRefresh)
        trials.addData('target_square.stopped', target_square.tStopRefresh)
        trials.addData('fixation_2.started', fixation_2.tStartRefresh)
        trials.addData('fixation_2.stopped', fixation_2.tStopRefresh)
        # store data for trials (TrialHandler)
        trials.addData('response.corr', response.corr)
        trials.addData('response.x', x)
        trials.addData('response.y', y)
        trials.addData('response.leftButton', response.click)

        if gotValidClick==True and (response.click_left == 1 or response.click_right == 1):  # we had a response
            trials.addData('response.rt_left', response.rt_left)
            trials.addData('response.rt_right', response.rt_right)
        trials.addData('response.click_left',response.click_left)
        trials.addData('response.click_right',response.click_right)
        trials.addData('response.corr', response.corr)
        trials.addData('response.started', response.tStartRefresh)
        trials.addData('response.stopped', response.tStopRefresh)

        Practice_1back_trial = []
        Practice_1back_trial.extend((grid_lines.tStartRefresh, t, mouse_response_rt, mouse_response, response.corr, turns, "1back"))
        Practice_1back.append(Practice_1back_trial)

        thisExp.nextEntry()

        if cheat == 1:
            score = 100
        else:
            score = correct*100/trials.nTotal

    """ 
    8iii. Practice 1-back Score Report
    """
    # Score Feedback Text
    ScoreText = "Your score was " + str(score)

    if debug == 1:
        TryAgainText = "Let's try that again...\n\n\n" + ScoreText + "\n\n\n\nExperimenter press [Space] to continue."
        PleaseWaitText = ScoreText + "\n\n\nPlease wait for the experimenter ..."
        PassedText = "Okay! Let's move on.\n\n\n" + ScoreText + "\n\n\n\nExperimenter press [Space] to continue."
        PerfectText = "Perfect! Let's move on.\n\n\n" + ScoreText + "\n\n\n\nExperimenter press [Space] to continue."
    else:
        TryAgainText = "Let's try that again...\n\n\n\n\n\n\n\nExperimenter press [Space] to continue."
        PleaseWaitText = "Please wait for the experimenter ..."
        PassedText = "Okay! Let's move on.\n\n\n\n\n\n\n\nExperimenter press [Space] to continue."
        PerfectText = "Perfect! Let's move on.\n\n\n\n\n\n\n\nExperimenter press [Space] to continue."


    # ------Prepare to start Routine "ScoreReport"-------
    continueRoutine = True
    # update component parameters for each repeat
    ScoreReportResponse.keys = []
    ScoreReportResponse.rt = []
    _ScoreReportResponse_allKeys = []
    # keep track of which components have finished
    ScoreReportComponents = [ScoreReportText, ScoreReportResponse]
    for thisComponent in ScoreReportComponents:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    ScoreReportClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    frameN = -1

    if (score <= 70):
        ScoreReportText.setText(TryAgainText)
        nback_feedback = nback_feedback_neg
    if turns >= 3 and score <= 70:
        ScoreReportText.setText(PleaseWaitText)
        nback_feedback = nback_feedback_neg
    if (score > 70):
        ScoreReportText.setText(PassedText)
        nback_feedback = nback_feedback_pos
    if (score == 100):
        ScoreReportText.setText( PerfectText)
        nback_feedback = nback_feedback_pos

    # -------Run Routine "ScoreReport"-------
    while continueRoutine:
        # get current time
        t = ScoreReportClock.getTime()
        tThisFlip = win.getFutureFlipTime(clock=ScoreReportClock)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *ScoreReportText* updates
        if ScoreReportText.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            ScoreReportText.frameNStart = frameN  # exact frame index
            ScoreReportText.tStart = t  # local t and not account for scr refresh
            ScoreReportText.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(ScoreReportText, 'tStartRefresh')  # time at next scr refresh
            if biopac_exists:
                win.callOnFlip(biopac.setData, biopac, 0)
                win.callOnFlip(biopac.setData, biopac, nback_feedback)
            ScoreReportText.setAutoDraw(True)
        
        # *ScoreReportResponse* updates
        waitOnFlip = False
        if ScoreReportResponse.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            ScoreReportResponse.frameNStart = frameN  # exact frame index
            ScoreReportResponse.tStart = t  # local t and not account for scr refresh
            ScoreReportResponse.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(ScoreReportResponse, 'tStartRefresh')  # time at next scr refresh
            ScoreReportResponse.status = STARTED
            # keyboard checking is just starting
            waitOnFlip = True
            win.callOnFlip(ScoreReportResponse.clock.reset)  # t=0 on next screen flip
            win.callOnFlip(ScoreReportResponse.clearEvents, eventType='keyboard')  # clear events on next screen flip
        if ScoreReportResponse.status == STARTED and not waitOnFlip:
            theseKeys = ScoreReportResponse.getKeys(keyList=['space'], waitRelease=False)
            _ScoreReportResponse_allKeys.extend(theseKeys)
            if len(_ScoreReportResponse_allKeys):
                ScoreReportResponse.keys = _ScoreReportResponse_allKeys[-1].name  # just the last key pressed
                ScoreReportResponse.rt = _ScoreReportResponse_allKeys[-1].rt
                # a response ends the routine
                continueRoutine = False
        
        # Autoresponder
        if t >= thisSimKey.rt and autorespond == 1:
            _ScoreReportResponse_allKeys.extend([thisSimKey])

        # check for quit (typically the Esc key)
        if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
            core.quit()
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in ScoreReportComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()

    # -------Ending Routine "ScoreReport"-------
    if biopac_exists:
        biopac.setData(biopac, 0)
    for thisComponent in ScoreReportComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    thisExp.addData('ScoreReportText.started', ScoreReportText.tStartRefresh)
    thisExp.addData('ScoreReportText.stopped', ScoreReportText.tStopRefresh)
    # check responses
    thisExp.addData('ScoreReportResponse.keys', ScoreReportResponse.keys)
    thisExp.addData('ScoreReportResponse.started', ScoreReportResponse.tStartRefresh)
    thisExp.addData('ScoreReportResponse.stopped', ScoreReportResponse.tStopRefresh)
    Practice_1back.append(["score: ", score])
    thisExp.nextEntry()
    routineTimer.reset()

    turns = turns + 1

"""
9. Save Practice-1back File
"""
# each _%s refers to the respective field in the parentheses
Practice_1back_bids_name = sub_dir + os.sep + u'sub-%05d_ses-%02d_task-%s_acq-%s_events.tsv' % (int(expInfo['subject number']), int(expInfo['session']), expName, "Practice1back")
Practice_1back = pd.DataFrame(Practice_1back, columns = ['onset','duration','rt','response','correct','attempt','condition'])
Practice_1back.to_csv(Practice_1back_bids_name, sep="\t")

"""
10. Start Practice 2-back
"""
turns = 0
score = 0
while turns <= 3 and score <= 70:
    # ------Prepare to start Routine "Instructions_2"-------
    NbackInstructionText8 = "2-back\n\n\nDuring 2-back you will have to indicate whether the current position matches the position that was presented two trials ago, by either pressing the \"yes\" button (left click) or the \"no\" button (right click).\n\n\nExperimenter press [Space] to see an example."

    NbackInstructions.setText(NbackInstructionText8)
    NbackInstructions.draw()
    if biopac_exists:
        biopac.setData(biopac, 0)
        biopac.setData(biopac, nback_instructions)
    win.flip()
    continueRoutine = True
    event.clearEvents()
    while continueRoutine == True:
        if 'space' in event.getKeys(keyList = 'space'):
            continueRoutine = False
    routineTimer.reset()

    NbackInstructionText9 = "In this 2-back example you should not respond to the first trial or the second trial (as there are insufficient previous trials), and make a \"yes\" response (left click) on trial 3, since the position is the same as the position on trial 1.\n\n\n\n\n\n\n\n\n\n"
    # Picture Loop 17-30.png
    ClickToContinueText = "Click to continue"

    NbackInstructionText10 = "Now, we will practice some trials so that you can get used to the procedure.\nAfter each response you'll see whether your response was correct, incorrect, or whether you forgot to respond.\n\n\n\n\n\n\n\n\nGood Luck!"
    ClickToStart = "Click to start practice"

    InstructionImageArray = ['18.png', '19.png', '20.png', '21.png', '22.png', '23.png', '24.png']
    iteration = 0
    NbackInstructions.setText(NbackInstructionText9)
    NbackInstructions.setAutoDraw(True)
    ClickPrompt.setText(ClickToContinueText)
    mouse = event.Mouse(win=win, visible=False)
    prevButtonState = mouse.getPressed()  # if button is down already this ISN'T a new click
    buttons = prevButtonState

    NbackInstructionWideImg.setImage(os.path.join(instructions_dir, InstructionImageArray[0]))
    NbackInstructionWideImg.draw()
    win.flip()

    continueRoutine = True
    i = 0
    stimTimer = core.CountdownTimer(1)    
    while (continueRoutine == True):
        if iteration == 1 and mouse.getPressed()[0] == 1:
            continueRoutine = False
            break
        if i > len(InstructionImageArray)-1:
            iteration = 1
            i = 0
            ClickPrompt.setAutoDraw(True)
        if stimTimer.getTime() < 0:
            stimTimer = core.CountdownTimer(1)
            NbackInstructionWideImg.setImage(os.path.join(instructions_dir, InstructionImageArray[i]))
            NbackInstructionWideImg.draw()
            i=i+1
        NbackInstructionWideImg.setAutoDraw(True)
        win.flip()

    NbackInstructionWideImg.setImage(os.path.join(instructions_dir, InstructionImageArray[len(InstructionImageArray)-1])) # Stay on the last image
    NbackInstructions.setText(NbackInstructionText10)
    NbackInstructions.setAutoDraw(True)
    win.flip()
    timer = core.CountdownTimer()
    timer.add(2)
    while timer.getTime() > 0:
        continue          
    mouse = event.Mouse(win=win, visible=False)
    while(mouse.getPressed()[0] != 1):
        ClickPrompt.setText(ClickToStartText)
        ClickPrompt.setAutoDraw(True)
        win.flip()

    # Wipe the screen
    ClickPrompt.setAutoDraw(False)
    NbackInstructions.setAutoDraw(False)
    NbackInstructionWideImg.setAutoDraw(False)
    if biopac_exists:
        biopac.setData(biopac, 0)
    win.flip()
    routineTimer.reset()

    ########################
    # Practice 2-back Begins
    ########################
    Feedback.setText("")
    correct = 0
    score = 0

    """ 
    10i. Pre-2-Back Task Fixation Cross
    """
    # ------Prepare to start Routine "Fixation"-------
    continueRoutine = True
    routineTimer.add(1.000000)      # 1 second pre-task fixation
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
                if biopac_exists:
                    win.callOnFlip(biopac.setData, biopac, 0)
                    win.callOnFlip(biopac.setData, biopac, nback_fixation)
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
        if biopac_exists:
            win.callOnFlip(biopac.setData, biopac, 0)
        for thisComponent in FixationComponents:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        thisExp.addData('fixation_1.started', fixation_1.tStartRefresh)
        thisExp.addData('fixation_1.stopped', fixation_1.tStopRefresh)
        routineTimer.reset()

        """ 
        10ii. Practice 2-back Start
        """
        # set up handler to look after randomisation of conditions etc
        Nback2 = os.sep.join([nback_dir, "Practice_N-back-2.xlsx"])
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

        for thisTrial_2 in trials_2:
            currentLoop = trials_2
            # abbreviate parameter names if possible (e.g. rgb = thisTrial_2.rgb)
            if thisTrial_2 != None:
                for paramName in thisTrial_2:
                    exec('{} = thisTrial_2[paramName]'.format(paramName))
            
            # ------Prepare to start Routine "N_back_2_trials"-------
            continueRoutine = True
            routineTimer.add(2.000000)          # Each trial is 2 seconds
            feedbacktype = "none"
            # update component parameters for each repeat
            target_square_2.setPos(location)
            response_2 = event.Mouse(win=win, visible=False) # Re-initialize
            response_2.click = []
            response_2.rt = []
            response_2.corr = []
            x, y = [None, None]
            gotValidClick = False  # until a click is received
            
            # keep track of which components have finished
            N_back_2_trialsComponents = [grid_lines_2, target_square_2, fixation_3, response_2, Feedback]
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
            N_back_2_TrialClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
            frameN = -1
            
            # -------Run Routine "N_back_2_trials"-------
            while continueRoutine and routineTimer.getTime() > 0:
                # get current time
                t = N_back_2_TrialClock.getTime()
                tThisFlip = win.getFutureFlipTime(clock=N_back_2_TrialClock)
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
                    prevButtonState = response_2.getPressed()  # if button is down already this ISN'T a new click
                if response_2.status == STARTED:  # only update if started and not finished!
                    if tThisFlipGlobal > response_2.tStartRefresh + 2-frameTolerance:
                        # keep track of stop time/frame for later
                        response_2.tStop = t  # not accounting for scr refresh
                        response_2.frameNStop = frameN  # exact frame index
                        win.timeOnFlip(response_2, 'tStopRefresh')  # time at next scr refresh
                        response_2.status = FINISHED
                if response_2.status == STARTED and not waitOnFlip:
                    response_2.click, response_2.rt = response_2.getPressed(getTime = True)
                    response_2.click_left = response_2.click[0]
                    response_2.click_right = response_2.click[2]
                    response_2.rt_left = response_2.rt[0]
                    response_2.rt_right = response_2.rt[2]
                    if response_2.click_left != prevButtonState[0] or response_2.click_right != prevButtonState[2]:  # button state changed?
                        prevButtonState = response_2.click
                        if (response_2.click_left == 1 or response_2.click_right == 1) and gotValidClick == False:
                            print(str(response_2.click), str(response_2.rt))
                            if (corrAns == 1 and response_2.click_left == 1) or (corrAns == 0 and response_2.click_right == 1):
                                response_2.corr = 1
                                correct = correct + 1
                                Feedback.setText(correct_text)
                                feedbacktype = "pos"
                                if biopac_exists:
                                    biopac.setData(biopac, 0)
                                    biopac.setData(biopac, nback_hit)
                            else:
                                response_2.corr = 0
                                Feedback.setText(incorrect_text)
                                feedbacktype = "neg"
                                if biopac_exists:
                                    biopac.setData(biopac, 0)
                                    biopac.setData(biopac, nback_comiss) # mark comission error
                            if response_2.click_left == 1: 
                                mouse_response = 0
                                mouse_response_rt = response_2.rt_left
                            elif response_2.click_right == 1:
                                mouse_response = 2
                                mouse_response_rt = response_2.rt_right
                            gotValidClick = True
                    elif response_2.click_left == 0 and response_2.click_right == 0 and gotValidClick==False:  # No response was made
                        mouse_response = None
                        mouse_response_rt = None
                        if str(corrAns).lower() != 'none':
                            Feedback.setText(noresponse_text)
                            feedbacktype = "miss"
                        else:
                            Feedback.setText("")
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
                
                # *Feedback* updates
                waitOnFlip = False
                if Feedback.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    Feedback.frameNStart = frameN  # exact frame index
                    Feedback.tStart = t  # local t and not account for scr refresh
                    Feedback.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(Feedback, 'tStartRefresh')  # time at next scr refresh
                    Feedback.status = STARTED
                    Feedback.setAutoDraw(False)

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
                    if 1 < N_back_2_TrialClock.getTime() < 1.75:
                        Feedback.draw()
                        if biopac_exists:
                            if feedbacktype == "pos":
                                biopac.setData(biopac, nback_feedback_pos)
                            if feedbacktype == "neg":
                                biopac.setData(biopac, nback_feedback_neg)
                            if feedbacktype == "miss":
                                biopac.setData(biopac, nback_feedback_miss)
                    else:
                        if biopac_exists:
                            biopac.setData(biopac, 0)
                    win.flip()
            
            
            # -------Ending Routine "N_back_2_trials"-------
            if biopac_exists:
                biopac.setData(biopac, 0)
            for thisComponent in N_back_2_trialsComponents:
                if hasattr(thisComponent, "setAutoDraw"):
                    thisComponent.setAutoDraw(False)

            # Check non-response
            if gotValidClick==False:  # No response was made
                response_2.rt = None
                if str(corrAns).lower() == 'none':
                    response_2.corr=1
                    correct = correct + 1
                else:
                    response_2.corr = 0;  # failed to respond (incorrectly)
                    Feedback.setText(noresponse_text)

            trials_2.addData('response_2.x', x)
            trials_2.addData('response_2.y', y)
            trials_2.addData('response_2.leftButton', response_2.click)
            trials_2.addData('grid_lines_2.started', grid_lines_2.tStartRefresh)
            trials_2.addData('grid_lines_2.stopped', grid_lines_2.tStopRefresh)
            trials_2.addData('target_square_2.started', target_square_2.tStartRefresh)
            trials_2.addData('target_square_2.stopped', target_square_2.tStopRefresh)
            trials_2.addData('fixation_3.started', fixation_3.tStartRefresh)
            trials_2.addData('fixation_3.stopped', fixation_3.tStopRefresh)

            if gotValidClick==True and (response_2.click_left == 1 or response_2.click_right == 1):  # we had a response
                trials.addData('response_2.rt_left', response_2.rt_left)
                trials.addData('response_2.rt_right', response_2.rt_right)

            # store data for trials_2 (TrialHandler)
            trials_2.addData('response_2.click',response_2.click)
            trials_2.addData('response_2.corr', response_2.corr)
            trials_2.addData('response_2.started', response_2.tStartRefresh)
            trials_2.addData('response_2.stopped', response_2.tStopRefresh)

            Practice_2back_trial = []
            Practice_2back_trial.extend((grid_lines_2.tStartRefresh, t, mouse_response_rt, mouse_response, response_2.corr, turns, "2back"))
            Practice_2back.append(Practice_2back_trial)

            routineTimer.reset()
            thisExp.nextEntry()

            if cheat == 1:
                score = 100
            else:
                score = correct*100/trials.nTotal

        """ 
        10iii. Practice 2-back Score Report
        """
        # Score Feedback Text
        ScoreText = "Your score was " + str(score)

        if debug == 1:
            TryAgainText = "Let's try that again...\n\n\n" + ScoreText + "\n\n\n\nExperimenter press [Space] to continue."
            PleaseWaitText = ScoreText + "\n\n\nPlease wait for the experimenter ..."
            PassedText = "Okay! Let's move on.\n\n\n" + ScoreText + "\n\n\n\nExperimenter press [Space] to continue."
            PerfectText = "Perfect! Let's move on.\n\n\n" + ScoreText + "\n\n\n\nExperimenter press [Space] to continue."
        else:
            TryAgainText = "Let's try that again...\n\n\n\n\n\n\n\nExperimenter press [Space] to continue."
            PleaseWaitText = "Please wait for the experimenter ..."
            PassedText = "Okay! Let's move on.\n\n\n\n\n\n\n\nExperimenter press [Space] to continue."
            PerfectText = "Perfect! Let's move on.\n\n\n\n\n\n\n\nExperimenter press [Space] to continue."

        # ------Prepare to start Routine "ScoreReport_2"-------
        continueRoutine = True
        # update component parameters for each repeat
        ScoreReportResponse.keys = []
        ScoreReportResponse.rt = []
        _ScoreReportResponse_allKeys = []
        # keep track of which components have finished
        ScoreReportComponents = [ScoreReportText, ScoreReportResponse]
        for thisComponent in ScoreReportComponents:
            thisComponent.tStart = None
            thisComponent.tStop = None
            thisComponent.tStartRefresh = None
            thisComponent.tStopRefresh = None
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        # reset timers
        t = 0
        _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        ScoreReportClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
        frameN = -1

        if (score <= 70):
            ScoreReportText.setText(TryAgainText)
            nback_feedback = nback_feedback_neg
        if turns >= 3 and score <= 70:
            ScoreReportText.setText(PleaseWaitText)
            nback_feedback = nback_feedback_neg
        if (score > 70):
            ScoreReportText.setText(PassedText)
            nback_feedback = nback_feedback_pos
        if (score == 100):
            ScoreReportText.setText( PerfectText)
            nback_feedback = nback_feedback_pos

        # -------Run Routine "ScoreReport"-------
        while continueRoutine:
            # get current time
            t = ScoreReportClock.getTime()
            tThisFlip = win.getFutureFlipTime(clock=ScoreReportClock)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame
            
            # *ScoreReportText* updates
            if ScoreReportText.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                ScoreReportText.frameNStart = frameN  # exact frame index
                ScoreReportText.tStart = t  # local t and not account for scr refresh
                ScoreReportText.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(ScoreReportText, 'tStartRefresh')  # time at next scr refresh
                if biopac_exists:
                    win.callOnFlip(biopac.setData, biopac, 0)
                    win.callOnFlip(biopac.setData, biopac, nback_feedback)
                ScoreReportText.setAutoDraw(True)
            
            # *ScoreReportResponse* updates
            waitOnFlip = False
            if ScoreReportResponse.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                ScoreReportResponse.frameNStart = frameN  # exact frame index
                ScoreReportResponse.tStart = t  # local t and not account for scr refresh
                ScoreReportResponse.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(ScoreReportResponse, 'tStartRefresh')  # time at next scr refresh
                ScoreReportResponse.status = STARTED
                # keyboard checking is just starting
                waitOnFlip = True
                win.callOnFlip(ScoreReportResponse.clock.reset)  # t=0 on next screen flip
                win.callOnFlip(ScoreReportResponse.clearEvents, eventType='keyboard')  # clear events on next screen flip
            if ScoreReportResponse.status == STARTED and not waitOnFlip:
                theseKeys = ScoreReportResponse.getKeys(keyList=['space'], waitRelease=False)
                _ScoreReportResponse_allKeys.extend(theseKeys)
                if len(_ScoreReportResponse_allKeys):
                    ScoreReportResponse.keys = _ScoreReportResponse_allKeys[-1].name  # just the last key pressed
                    ScoreReportResponse.rt = _ScoreReportResponse_allKeys[-1].rt
                    # a response ends the routine
                    continueRoutine = False
            
            # Autoresponder
            if t >= thisSimKey.rt and autorespond == 1:
                _ScoreReportResponse_allKeys.extend([thisSimKey])

            # check for quit (typically the Esc key)
            if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
                core.quit()
            
            # check if all components have finished
            if not continueRoutine:  # a component has requested a forced-end of Routine
                break
            continueRoutine = False  # will revert to True if at least one component still running
            for thisComponent in ScoreReportComponents:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished
            
            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()

        # -------Ending Routine "ScoreReport"-------
        if biopac_exists:
            biopac.setData(biopac, 0)
        for thisComponent in ScoreReportComponents:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        thisExp.addData('ScoreReportText.started', ScoreReportText.tStartRefresh)
        thisExp.addData('ScoreReportText.stopped', ScoreReportText.tStopRefresh)
        # check responses
        thisExp.addData('ScoreReportResponse.keys', ScoreReportResponse.keys)
        thisExp.addData('ScoreReportResponse.started', ScoreReportResponse.tStartRefresh)
        thisExp.addData('ScoreReportResponse.stopped', ScoreReportResponse.tStopRefresh)
        Practice_2back.append(["score: ", score])
        thisExp.nextEntry()
        routineTimer.reset()

        turns = turns + 1

"""
11. Save Practice-2back File
"""
# each _%s refers to the respective field in the parentheses
Practice_2back_bids_name = sub_dir + os.sep + u'sub-%05d_ses-%02d_task-%s_acq-%s_events.tsv' % (int(expInfo['subject number']), int(expInfo['session']), expName, "Practice2back")
Practice_2back = pd.DataFrame(Practice_2back, columns = ['onset','duration','rt','response','correct','attempt','condition'])
Practice_2back.to_csv(Practice_2back_bids_name, sep="\t")

###################
# Real Trials Start
###################

NbackInstructionText11 = "The tutorial is now over, we will now begin our scans, after which you will be instructed of the task assigned to you.\n\n\nWe will add some difficulty by periodically sending painful thermal stimulations to a designated body-site. \nDuring the task it is very important that you respond as fast and as accurately as possible.\n\n\nYou should try to respond shortly after the square is presented. This might be difficult, so it is important that you concentrate!\n\nExperimenter press [Space] to continue."
NbackInstructions.setText(NbackInstructionText11)
NbackInstructions.draw()
win.flip()
continueRoutine = True
event.clearEvents()
while continueRoutine == True:
    if 'space' in event.getKeys(keyList = 'space'):
        continueRoutine = False
routineTimer.reset()

BigTrialList = [[2, 1, 2, 1, 2, 1, 1, 2, 1, 1, 1, 2, 2, 2, 1, 2], 
                [1, 2, 2, 2, 1, 1, 2, 1, 1, 1, 2, 1, 2, 2, 1, 2],
                [1, 2, 2, 1, 2, 1, 1, 1, 2, 2, 2, 1, 1, 1, 2, 2],
                [1, 1, 1, 2, 2, 2, 1, 2, 1, 2, 2, 1, 1, 1, 2, 2],
                [1, 1, 2, 2, 1, 1, 1, 2, 2, 1, 1, 2, 1, 2, 2, 2],
                [1, 1, 1, 2, 1, 2, 1, 2, 2, 2, 1, 1, 2, 2, 2, 1],
                [2, 1, 1, 1, 2, 2, 2, 1, 1, 1, 2, 2, 1, 2, 2, 1],
                [2, 2, 1, 2, 2, 2, 1, 2, 1, 1, 1, 2, 1, 1, 1, 2],
                [2, 1, 1, 2, 2, 2, 1, 1, 1, 2, 1, 1, 1, 2, 2, 2]]


for runs in range(len(bodySites)):
    """
    12. Body-Site Instructions: Instruct the Experimenter on the Body Sites to attach thermodes to at the beginning of each run
        Also, generate a list of 16 N-back trialTypes to be randomly presented 
    """
    # trialTypes = [1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2]
    # random.shuffle(trialTypes)
    # NbackTrials = []
    # triplicate = 0
    # lastElement = 0
    # while trialTypes:
    #     element = trialTypes.pop()
    #     if element == lastElement:
    #         triplicate = triplicate + 1
    #     else:
    #         triplicate = 0
    #     if triplicate >= 3:
    #         lastElement = element
    #         trialTypes.insert(0, element)
    #     else:
    #         lastElement = element
    #         NbackTrials.insert(0,element)
    # print(NbackTrials)

    random.shuffle(BigTrialList)
    NbackTrials = BigTrialList.pop()

    # ------Prepare to start Routine "BodySiteInstruction"-------
    routineTimer.reset()

    continueRoutine = True
    # update component parameters for each repeat
    BodySiteInstructionRead.keys = []
    BodySiteInstructionRead.rt = []
    _BodySiteInstructionRead_allKeys = []
    # Update instructions and cues based on current run's body-sites:
    BodySiteInstructionText.text="Experimenter: \nPlease place the thermode on the: \n" + bodySites[runs].lower()
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
            BodySiteImg.image = bodysite_word2img[bodySites[runs]]
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
    thisExp.addData('BodySiteInstructionText.started', BodySiteInstructionText.tStartRefresh)
    thisExp.addData('BodySiteImg.started', BodySiteImg.tStartRefresh)
    thisExp.addData('BodySiteImg.stopped', BodySiteImg.tStopRefresh)
    # check responses
    if BodySiteInstructionRead.keys in ['', [], None]:  # No response was made
        BodySiteInstructionRead.keys = None
    thisExp.addData('BodySiteInstructionRead.keys',BodySiteInstructionRead.keys)
    if BodySiteInstructionRead.keys != None:  # we had a response
        thisExp.addData('BodySiteInstructionRead.rt', BodySiteInstructionRead.rt)
    thisExp.addData('BodySiteInstructionRead.started', BodySiteInstructionRead.tStartRefresh)
    thisExp.addData('BodySiteInstructionRead.stopped', BodySiteInstructionRead.tStopRefresh)
    # Start a new BIDS data collection array for each run
    bodymap_bids_data = []
    # the Routine "BodySiteInstruction" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()

    """
    13. Start Scanner
    """
    start = visual.TextStim(win, text=start_msg, height=.05, color=win.rgb + 0.5)
    start.draw()  # Automatically draw every frame
    win.flip()
    fmriStart = globalClock.getTime()   # Start the clock
    if autorespond != 1:   
        TR = 0.46
       
        continueRoutine = True
        event.clearEvents()
        while continueRoutine == True:
            if 's' in event.getKeys(keyList = 's'):         # experimenter start key - safe key before fMRI trigger
                event.clearEvents()
                while continueRoutine == True:
                    if '5' in event.getKeys(keyList = '5'): # fMRI trigger
                        fmriStart = globalClock.getTime()   # Start the clock
                        timer = core.CountdownTimer()   # Wait 6 TRs, Dummy Scans
                        timer.add(TR*6)
                        while timer.getTime() > 0:
                            continue
                        continueRoutine = False

    jitter2 = None  # Reset Jitter2
    bodySiteData = bodySites[runs]
    temperature = participant_settingsHeat[bodySites[runs]]
    BiopacChannel = bodysite_word2heatcode[bodySites[runs]]
    thermodeCommand = thermode1_temp2program[participant_settingsHeat[bodySites[runs]]]  
    routineTimer.reset()

    for r in NbackTrials: # 16 repetitions
        # Randomly select either 1-back or 2-back
    
        if r == 1:

            """ 
            14. Begin 1-Back Trials
            """


            NbackInstructions.setText("The following trials will be 1-back, please indicate whether or not the square in the current position matches the position that was presented in the last trial.")
            NbackInstructions.draw()
            if biopac_exists:
                biopac.setData(biopac, 0)
                biopac.setData(biopac, nback_instructions)
            onset = globalClock.getTime() - fmriStart
            win.flip()

            timer = core.CountdownTimer()
            timer.add(5)
            while timer.getTime() > 0:
                continue
            
            distractmap_bids_trial = []
            distractmap_bids_trial.extend((onset, globalClock.getTime() - fmriStart, None, None, None, bodySites[runs], temperature, "1back Instructions", None))
            distractmap_bids.append(distractmap_bids_trial)
            
            routineTimer.reset()
            # jitter2 = None # Reset jitter2
                
            """
            14i. Select Medoc Thermal Program
            """
            if thermode_exists == 1:
                sendCommand('select_tp', thermodeCommand)
            """ 
            14ii. Pre-1-Back Task Fixation Cross
            """
            # ------Prepare to start Routine "Fixation"-------
            continueRoutine = True
            if not jitter2:
                jitter1 = random.choice([3,5,7])
            elif jitter2 == 3:
                jitter1 = 7
            elif jitter2 == 5:
                jitter1 = 5
            elif jitter2 == 7:
                jitter1 = 3
            routineTimer.add(jitter1)
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
                    if biopac_exists:
                        win.callOnFlip(biopac.setData, biopac, 0)
                        win.callOnFlip(biopac.setData, biopac, nback_fixation)
                    fixation_1.setAutoDraw(True)
                if fixation_1.status == STARTED:
                    # is it time to stop? (based on global clock, using actual start)
                    if tThisFlipGlobal > fixation_1.tStartRefresh + jitter1-frameTolerance:
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
            if biopac_exists:
                win.callOnFlip(biopac.setData, biopac, 0)
            for thisComponent in FixationComponents:
                if hasattr(thisComponent, "setAutoDraw"):
                    thisComponent.setAutoDraw(False)
            thisExp.addData('fixation_1.started', fixation_1.tStartRefresh)
            thisExp.addData('fixation_1.stopped', fixation_1.tStopRefresh)

            routineTimer.reset()

            """
            14iii. First Phase: 4 trials of 1-Back Task Start
            """
            # set up handler to look after randomisation of conditions etc
            if not OnebackFiles:
                OnebackFiles = ["N-back-1_1.xlsx", "N-back-1_2.xlsx", "N-back-1_3.xlsx", "N-back-1_4.xlsx", "N-back-1_5.xlsx", "N-back-1_6.xlsx", "N-back-1_7.xlsx", "N-back-1_8.xlsx"] 
            Nback = os.sep.join([nback_dir, OnebackFiles.pop()])
            trials = data.TrialHandler(nReps=1, method='sequential', 
                extraInfo=expInfo, originPath=-1,
                trialList=data.importConditions(Nback), # Randomize the order
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
                # Trigger Thermal Program
                if trials.thisTrialN == 4 and thermode_exists == 1:
                    sendCommand('trigger')                          # Trigger the thermode
                
                continueRoutine = True
                routineTimer.add(2.000000)
                # update component parameters for each repeat
                target_square.setPos(location)
                response.rt = []

                gotValidClick = False  # until a click is received

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
                onset = globalClock.getTime() - fmriStart           # Record onset time of the trial
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
                        if biopac_exists == 1:
                            win.callOnFlip(biopac.setData, biopac, 0)
                            win.callOnFlip(biopac.setData, biopac, nback_trial_start)
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
                        prevButtonState = response.getPressed()  # if button is down already this ISN'T a new click

                    if response.status == STARTED:
                        # is it time to stop? (based on global clock, using actual start)
                        if tThisFlipGlobal > response.tStartRefresh + 2-frameTolerance:
                            # keep track of stop time/frame for later
                            response.tStop = t  # not accounting for scr refresh
                            response.frameNStop = frameN  # exact frame index
                            win.timeOnFlip(response, 'tStopRefresh')  # time at next scr refresh
                            response.status = FINISHED
                    if response.status == STARTED and not waitOnFlip:
                            response.click, response.rt = response.getPressed(getTime = True)
                            response.click_left = response.click[0]
                            response.click_right = response.click[2]
                            response.rt_left = response.rt[0]
                            response.rt_right = response.rt[2]
                            if response.click_left != prevButtonState[0] or response.click_right != prevButtonState[2]:  # button state changed?
                                prevButtonState = response.click
                                if (response.click_left == 1 or response.click_right == 1) and gotValidClick == False:
                                    print(str(response.click), str(response.rt))
                                    if (corrAns == 1 and response.click_left == 1) or (corrAns == 0 and response.click_right == 1):
                                        response.corr = 1
                                        correct = correct + 1
                                        if biopac_exists:
                                            biopac.setData(biopac, 0)
                                            biopac.setData(biopac, nback_hit)
                                    else:
                                        response.corr = 0
                                        if biopac_exists:
                                            biopac.setData(biopac, 0)
                                            biopac.setData(biopac, nback_comiss) # mark comission error
                                    if response.click_left == 1: 
                                        mouse_response = 0
                                        mouse_response_rt = response.rt_left
                                    elif response.click_right == 1: 
                                        mouse_response = 2
                                        mouse_response_rt = response.rt_right
                                    gotValidClick = True
                            elif response.click_left == 0 and response.click_right == 0 and gotValidClick==False:  # No response was made
                                mouse_response = None
                                mouse_response_rt = None
                                
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
                
                if gotValidClick==False:  # No response was made
                    response_2.rt = None
                    if str(corrAns).lower() == 'none':
                        response.corr=1
                        correct = correct + 1
                    else:
                        response.corr = 0;  # failed to respond (incorrectly)

                trials.addData('grid_lines.started', grid_lines.tStartRefresh)
                trials.addData('grid_lines.stopped', grid_lines.tStopRefresh)
                trials.addData('target_square.started', target_square.tStartRefresh)
                trials.addData('target_square.stopped', target_square.tStopRefresh)
                trials.addData('fixation_2.started', fixation_2.tStartRefresh)
                trials.addData('fixation_2.stopped', fixation_2.tStopRefresh)
                # store data for trials (TrialHandler)
                trials.addData('response.corr', response.corr)
                
                trials.addData('response.x', x)
                trials.addData('response.y', y)
                trials.addData('response.leftButton', response.click)

                if gotValidClick==True and (response.click_left == 1 or response.click_right == 1):  # we had a response
                    trials.addData('response.rt_left', response.rt_left)
                    trials.addData('response.rt_right', response.rt_right)

                trials.addData('response.click',response.click)
                trials.addData('response.corr', response.corr)
                trials.addData('response.started', response.tStartRefresh)
                trials.addData('response.stopped', response.tStopRefresh)

                distractmap_bids_trial = []
                if trials.thisTrialN == 1:
                    distractmap_bids_trial.extend((onset, t, mouse_response_rt, mouse_response, response.corr, bodySites[runs], temperature, "1back", jitter1))
                else:
                    distractmap_bids_trial.extend((onset, t, mouse_response_rt, mouse_response, response.corr, bodySites[runs], temperature, "1back", None))
                distractmap_bids.append(distractmap_bids_trial)

                routineTimer.reset()
                thisExp.nextEntry()
                        
            """ 
            14iv. Post First 1-Back Fixation Cross
            """
            # ------Prepare to start Routine "Fixation"-------
            continueRoutine = True
            jitter2 = random.choice([3,5,7])
            routineTimer.add(jitter2)
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
                    if biopac_exists:
                        win.callOnFlip(biopac.setData, biopac, 0)
                        win.callOnFlip(biopac.setData, biopac, nback_fixation)
                    fixation_1.setAutoDraw(True)
                if fixation_1.status == STARTED:
                    # is it time to stop? (based on global clock, using actual start)
                    if tThisFlipGlobal > fixation_1.tStartRefresh + jitter2-frameTolerance:
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
            if biopac_exists:
                win.callOnFlip(biopac.setData, biopac, 0)
            for thisComponent in FixationComponents:
                if hasattr(thisComponent, "setAutoDraw"):
                    thisComponent.setAutoDraw(False)
            thisExp.addData('fixation_1.started', fixation_1.tStartRefresh)
            thisExp.addData('fixation_1.stopped', fixation_1.tStopRefresh)

            routineTimer.reset()

            """
            14v. Phase-1 1-back Pain Rating Trial
            """
            # ------Prepare to start Routine "IntensityRating"-------
            continueRoutine = True
            routineTimer.add(ratingTime)
            # update component parameters for each repeat
            # keep track of which components have finished
            IntensityMouse = event.Mouse(win=win, visible=False) # Re-initialize IntensityMouse
            IntensityMouse.setPos((0,0))
            timeAtLastInterval = 0
            mouseX = 0
            oldMouseX = 0
            IntensityRating.width = abs(sliderMin)
            IntensityRating.pos = [sliderMin/2, -.1]

            IntensityRatingComponents = [IntensityMouse, IntensityBlackTriangle, IntensityRating, IntensityAnchors, IntensityPrompt]
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

            IntensityRating.fillColor='red'
            obtainedRating = 0

            # -------Run Routine "IntensityRating"-------
            onset = globalClock.getTime() - fmriStart           # Record onset time of the trial
            while continueRoutine:
                if obtainedRating == 0:
                    timeNow = globalClock.getTime()
                    if (timeNow - timeAtLastInterval) > TIME_INTERVAL:
                        mouseRel=IntensityMouse.getRel()
                        mouseX=oldMouseX + mouseRel[0]
                    IntensityRating.pos = ((sliderMin + mouseX)/2,0)
                    IntensityRating.width = abs((mouseX-sliderMin))
                    if mouseX > sliderMax:
                        mouseX = sliderMax
                    if mouseX < sliderMin:
                        mouseX = sliderMin
                    timeAtLastInterval = timeNow
                    oldMouseX=mouseX
                    sliderValue = (mouseX - sliderMin) / (sliderMax - sliderMin) * 100

                # get current time
                t = IntensityRatingClock.getTime()
                tThisFlip = win.getFutureFlipTime(clock=IntensityRatingClock)
                tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                # update/draw components on each frame
                
                # *IntensityMouse* updates
                if IntensityMouse.status == NOT_STARTED and t >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    IntensityMouse.frameNStart = frameN  # exact frame index
                    IntensityMouse.tStart = t  # local t and not account for scr refresh
                    IntensityMouse.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(IntensityMouse, 'tStartRefresh')  # time at next scr refresh
                    IntensityMouse.status = STARTED
                    IntensityMouse.mouseClock.reset()
                    prevButtonState = IntensityMouse.getPressed()  # if button is down already this ISN'T a new click
                if IntensityMouse.status == STARTED:  # only update if started and not finished!
                    if tThisFlipGlobal > IntensityMouse.tStartRefresh + ratingTime-frameTolerance:
                        # keep track of stop time/frame for later
                        IntensityMouse.tStop = t  # not accounting for scr refresh
                        IntensityMouse.frameNStop = frameN  # exact frame index
                        IntensityMouse.status = FINISHED
                    buttons = IntensityMouse.getPressed()
                    if buttons != prevButtonState:  # button state changed?
                        prevButtonState = buttons
                        if sum(buttons) > 0:  # state changed to a new click
                            IntensityRating.fillColor='white'
                            obtainedRating = 1
                
                # *IntensityRating* updates
                if IntensityRating.status == NOT_STARTED and t >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    IntensityRating.frameNStart = frameN  # exact frame index
                    IntensityRating.tStart = t  # local t and not account for scr refresh
                    IntensityRating.tStartRefresh = tThisFlipGlobal  # on global time
                    win.callOnFlip(print, "Show Intensity Rating")
                    if biopac_exists == 1:
                        win.callOnFlip(biopac.setData, biopac, 0)
                        win.callOnFlip(biopac.setData, biopac, intensity_rating)
                    win.timeOnFlip(IntensityRating, 'tStartRefresh')  # time at next scr refresh
                    IntensityRating.setAutoDraw(True)
                if IntensityRating.status == STARTED:
                    # is it time to stop? (based on global clock, using actual start)
                    if tThisFlipGlobal > IntensityRating.tStartRefresh + ratingTime-frameTolerance:
                        # keep track of stop time/frame for later
                        IntensityRating.tStop = t  # not accounting for scr refresh
                        IntensityRating.frameNStop = frameN  # exact frame index
                        win.timeOnFlip(IntensityRating, 'tStopRefresh')  # time at next scr refresh
                        IntensityRating.setAutoDraw(False)
                
                # *IntensityBlackTriangle* updates
                if IntensityBlackTriangle.status == NOT_STARTED and t >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    IntensityBlackTriangle.frameNStart = frameN  # exact frame index
                    IntensityBlackTriangle.tStart = t  # local t and not account for scr refresh
                    IntensityBlackTriangle.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(IntensityBlackTriangle, 'tStartRefresh')  # time at next scr refresh
                    IntensityBlackTriangle.setAutoDraw(True)
                if IntensityBlackTriangle.status == STARTED:
                    # is it time to stop? (based on global clock, using actual start)
                    if tThisFlipGlobal > IntensityBlackTriangle.tStartRefresh + ratingTime-frameTolerance:
                        # keep track of stop time/frame for later
                        IntensityBlackTriangle.tStop = t  # not accounting for scr refresh
                        IntensityBlackTriangle.frameNStop = frameN  # exact frame index
                        win.timeOnFlip(IntensityBlackTriangle, 'tStopRefresh')  # time at next scr refresh
                        IntensityBlackTriangle.setAutoDraw(False)
                
                # *IntensityAnchors* updates
                if IntensityAnchors.status == NOT_STARTED and t >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    IntensityAnchors.frameNStart = frameN  # exact frame index
                    IntensityAnchors.tStart = t  # local t and not account for scr refresh
                    IntensityAnchors.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(IntensityAnchors, 'tStartRefresh')  # time at next scr refresh
                    IntensityAnchors.setAutoDraw(True)
                if IntensityAnchors.status == STARTED:
                    # is it time to stop? (based on global clock, using actual start)
                    if tThisFlipGlobal > IntensityAnchors.tStartRefresh + ratingTime-frameTolerance:
                        # keep track of stop time/frame for later
                        IntensityAnchors.tStop = t  # not accounting for scr refresh
                        IntensityAnchors.frameNStop = frameN  # exact frame index
                        win.timeOnFlip(IntensityAnchors, 'tStopRefresh')  # time at next scr refresh
                        IntensityAnchors.setAutoDraw(False)
                
                # *IntensityPrompt* updates
                if IntensityPrompt.status == NOT_STARTED and t >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    IntensityPrompt.frameNStart = frameN  # exact frame index
                    IntensityPrompt.tStart = t  # local t and not account for scr refresh
                    IntensityPrompt.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(IntensityPrompt, 'tStartRefresh')  # time at next scr refresh
                    IntensityPrompt.setAutoDraw(True)
                if IntensityPrompt.status == STARTED:
                    # is it time to stop? (based on global clock, using actual start)
                    if tThisFlipGlobal > IntensityPrompt.tStartRefresh + ratingTime-frameTolerance:
                        # keep track of stop time/frame for later
                        IntensityPrompt.tStop = t  # not accounting for scr refresh
                        IntensityPrompt.frameNStop = frameN  # exact frame index
                        win.timeOnFlip(IntensityPrompt, 'tStopRefresh')  # time at next scr refresh
                        IntensityPrompt.setAutoDraw(False)

                # Autoresponder
                if t >= thisSimKey.rt and autorespond == 1:
                    sliderValue = random.randint(0,100)
                    continueRoutine = False

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
                if continueRoutine:
                    win.flip()

            # -------Ending Routine "IntensityRating"-------
            print("CueOff Channel " + str(intensity_rating))
            for thisComponent in IntensityRatingComponents:
                if hasattr(thisComponent, "setAutoDraw"):
                    thisComponent.setAutoDraw(False)
            # store data for thisExp (ExperimentHandler)
            thisExp.addData('IntensityRating.response', sliderValue)
            thisExp.addData('IntensityRating.rt', timeNow - IntensityRating.tStart)
            thisExp.nextEntry()
            thisExp.addData('IntensityRating.started', IntensityRating.tStart)
            thisExp.addData('IntensityRating.stopped', IntensityRating.tStop)

            # rating_bids_trial = []
            # rating_bids_trial.extend((onset, t, bodySites[runs], sliderValue, temperature, "1back", jitter1, jitter2))
            # rating_bids.append(rating_bids_trial)

            distractmap_bids_trial = []
            distractmap_bids_trial.extend((onset, t, None, sliderValue, None, bodySites[runs], temperature, "1back Rating", jitter2))
            distractmap_bids.append(distractmap_bids_trial)

            # the Routine "IntensityRating" was not non-slip safe, so reset the non-slip timer
            routineTimer.reset()
    
        if r == 2:
            """ 
            15. Begin First 2-Back Trials
            """
            NbackInstructions.setText("The following trials will be 2-back, please indicate whether or not the square in the current position matches the position that was presented two trials before.")
            NbackInstructions.draw()
            if biopac_exists:
                biopac.setData(biopac, 0)
                biopac.setData(biopac, nback_instructions)
            onset = globalClock.getTime() - fmriStart
            win.flip()

            timer = core.CountdownTimer()
            timer.add(5)
            while timer.getTime() > 0:
                continue
            routineTimer.reset()
            # jitter2 = None # Reset jitter2 

            distractmap_bids_trial = []
            distractmap_bids_trial.extend((onset, globalClock.getTime() - fmriStart, None, None, None, bodySites[runs], temperature, "2back Instructions", None))
            distractmap_bids.append(distractmap_bids_trial)

            """
            15i. Select Medoc Thermal Program
            """
            if thermode_exists == 1:
                sendCommand('select_tp', thermodeCommand)
            """
            15ii. Pre-2-Back Task Fixation Cross
            """
            # ------Prepare to start Routine "Fixation"-------
            continueRoutine = True
            if not jitter2:
                jitter1 = random.choice([3,5,7])
            elif jitter2 == 3:
                jitter1 = 7
            elif jitter2 == 5:
                jitter1 = 5
            elif jitter2 == 7:
                jitter1 = 3
            routineTimer.add(jitter1)
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
                    if biopac_exists:
                        win.callOnFlip(biopac.setData, biopac, 0)
                        win.callOnFlip(biopac.setData, biopac, nback_fixation)
                    fixation_1.setAutoDraw(True)
                if fixation_1.status == STARTED:
                    # is it time to stop? (based on global clock, using actual start)
                    if tThisFlipGlobal > fixation_1.tStartRefresh + jitter1-frameTolerance:
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
            if biopac_exists:
                win.callOnFlip(biopac.setData, biopac, 0)
            for thisComponent in FixationComponents:
                if hasattr(thisComponent, "setAutoDraw"):
                    thisComponent.setAutoDraw(False)
            thisExp.addData('fixation_1.started', fixation_1.tStartRefresh)
            thisExp.addData('fixation_1.stopped', fixation_1.tStopRefresh)

            routineTimer.reset()

            """
            15iii. 2-Back Task Start
            """
            # set up handler to look after randomisation of conditions etc
            if not TwobackFiles:
                TwobackFiles = ["N-back-2_1.xlsx", "N-back-2_2.xlsx", "N-back-2_3.xlsx", "N-back-2_4.xlsx", "N-back-2_5.xlsx", "N-back-2_6.xlsx", "N-back-2_7.xlsx", "N-back-2_8.xlsx"]
            Nback = os.sep.join([nback_dir, TwobackFiles.pop()])
            trials_2 = data.TrialHandler(nReps=1, method='sequential', 
                extraInfo=expInfo, originPath=-1,
                trialList=data.importConditions(Nback),
                seed=None, name='trials_2')
            thisExp.addLoop(trials_2)  # add the loop to the experiment
            thisTrial_2 = trials_2.trialList[0]  # so we can initialise stimuli with some values
            # abbreviate parameter names if possible (e.g. rgb = thisTrial_2.rgb)
            if thisTrial_2 != None:
                for paramName in thisTrial_2:
                    exec('{} = thisTrial_2[paramName]'.format(paramName))

            for thisTrial_2 in trials_2:
                currentLoop = trials_2
                # abbreviate parameter names if possible (e.g. rgb = thisTrial_2.rgb)
                if thisTrial_2 != None:
                    for paramName in thisTrial_2:
                        exec('{} = thisTrial_2[paramName]'.format(paramName))
                
                # ------Prepare to start Routine "N_back_2_trials"-------
                # Trigger Thermal Program
                if trials_2.thisTrialN == 4 and thermode_exists == 1:
                    sendCommand('trigger')

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
                N_back_2_trialsComponents = [grid_lines_2, target_square_2, fixation_3, response_2, Feedback]
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
                N_back_2_TrialClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
                frameN = -1
                
                # -------Run Routine "N_back_2_trials"-------
                onset = globalClock.getTime() - fmriStart
                while continueRoutine and routineTimer.getTime() > 0:
                    # get current time
                    t = N_back_2_TrialClock.getTime()
                    tThisFlip = win.getFutureFlipTime(clock=N_back_2_TrialClock)
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
                        prevButtonState = response_2.getPressed()  # if button is down already this ISN'T a new click
                    if response_2.status == STARTED:  # only update if started and not finished!
                        if tThisFlipGlobal > response_2.tStartRefresh + 2-frameTolerance:
                            # keep track of stop time/frame for later
                            response_2.tStop = t  # not accounting for scr refresh
                            response_2.frameNStop = frameN  # exact frame index
                            win.timeOnFlip(response_2, 'tStopRefresh')  # time at next scr refresh
                            response_2.status = FINISHED
                    if response_2.status == STARTED and not waitOnFlip:
                        response_2.click, response_2.rt = response_2.getPressed(getTime = True)
                        response_2.click_left = response_2.click[0]
                        response_2.click_right = response_2.click[2]
                        response_2.rt_left = response_2.rt[0]
                        response_2.rt_right = response_2.rt[2]
                        if response_2.click_left != prevButtonState[0] or response_2.click_right != prevButtonState[2]:  # button state changed?
                            prevButtonState = response_2.click
                            if (response_2.click_left == 1 or response_2.click_right == 1) and gotValidClick == False:
                                print(str(response_2.click), str(response_2.rt))
                                if (corrAns == 1 and response_2.click_left == 1) or (corrAns == 0 and response_2.click_right == 1):
                                    response_2.corr = 1
                                    correct = correct + 1
                                    if biopac_exists:
                                        biopac.setData(biopac, 0)
                                        biopac.setData(biopac, nback_hit)
                                else:
                                    response_2.corr = 0
                                    if biopac_exists:
                                        biopac.setData(biopac, 0)
                                        biopac.setData(biopac, nback_comiss) # mark comission error
                                if response_2.click_left == 1: 
                                    mouse_response = 0
                                    mouse_response_rt = response_2.rt_left
                                elif response_2.click_right == 1: 
                                    mouse_response = 2
                                    mouse_response_rt = response_2.rt_left
                                gotValidClick = True
                        elif response_2.click_left == 0 and response_2.click_right == 0 and gotValidClick==False:  # No response was made
                            mouse_response = None
                            mouse_response_rt = None

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
                if gotValidClick==False:  # No response was made
                    response_2.rt = None
                    if str(corrAns).lower() == 'none':
                        response_2.corr=1
                        correct = correct + 1
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

                if gotValidClick==True and (response_2.click_left == 1 or response_2.click_right == 1):  # we had a response
                    trials.addData('response_2.rt_left', response_2.rt_left)
                    trials.addData('response_2.rt_right', response_2.rt_right)

                # store data for trials_2 (TrialHandler)
                trials_2.addData('response_2.click',response_2.click)
                trials_2.addData('response_2.corr', response_2.corr)
                trials_2.addData('response_2.started', response_2.tStartRefresh)
                trials_2.addData('response_2.stopped', response_2.tStopRefresh)

                distractmap_bids_trial = []
                if trials_2.thisTrialN == 1:
                    distractmap_bids_trial.extend((onset, t, mouse_response_rt, mouse_response, response_2.corr, bodySites[runs], temperature, "2back", jitter1))
                else:
                    distractmap_bids_trial.extend((onset, t, mouse_response_rt, mouse_response, response_2.corr, bodySites[runs], temperature, "2back", None))
                distractmap_bids.append(distractmap_bids_trial)
                routineTimer.reset()
                thisExp.nextEntry()
                
            # completed 1 repeats of 'trials_2'
            """
            15iv. Post 2-Back Fixation Cross
            """
            # ------Prepare to start Routine "Fixation"-------
            continueRoutine = True
            jitter2 = random.choice([3,5,7])
            routineTimer.add(jitter2)
        
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
                    if biopac_exists:
                        win.callOnFlip(biopac.setData, biopac, 0)
                        win.callOnFlip(biopac.setData, biopac, nback_fixation)
                    fixation_1.setAutoDraw(True)
                if fixation_1.status == STARTED:
                    # is it time to stop? (based on global clock, using actual start)
                    if tThisFlipGlobal > fixation_1.tStartRefresh + jitter2-frameTolerance:
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
            if biopac_exists:
                win.callOnFlip(biopac.setData, biopac, 0)
            for thisComponent in FixationComponents:
                if hasattr(thisComponent, "setAutoDraw"):
                    thisComponent.setAutoDraw(False)
            thisExp.addData('fixation_1.started', fixation_1.tStartRefresh)
            thisExp.addData('fixation_1.stopped', fixation_1.tStopRefresh)

            routineTimer.reset()

            """
            15v. 2-back Pain Rating Trial
            """
            ############ ASK PAIN INTENSITY #######################################
            # ------Prepare to start Routine "IntensityRating"-------
            continueRoutine = True
            routineTimer.add(ratingTime)
            # update component parameters for each repeat
            # keep track of which components have finished
            IntensityMouse = event.Mouse(win=win, visible=False) # Re-initialize IntensityMouse
            IntensityMouse.setPos((0,0))
            timeAtLastInterval = 0
            mouseX = 0
            oldMouseX = 0
            IntensityRating.width = abs(sliderMin)
            IntensityRating.pos = [sliderMin/2, -.1]

            IntensityRatingComponents = [IntensityMouse, IntensityBlackTriangle, IntensityRating, IntensityAnchors, IntensityPrompt]
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

            IntensityRating.fillColor='red'
            obtainedRating = 0

            # -------Run Routine "IntensityRating"-------
            onset = globalClock.getTime() - fmriStart           # Record onset time of the trial
            while continueRoutine:
                if obtainedRating == 0:
                    timeNow = globalClock.getTime()
                    if (timeNow - timeAtLastInterval) > TIME_INTERVAL:
                        mouseRel=IntensityMouse.getRel()
                        mouseX=oldMouseX + mouseRel[0]
                    IntensityRating.pos = ((sliderMin + mouseX)/2,0)
                    IntensityRating.width = abs((mouseX-sliderMin))
                    if mouseX > sliderMax:
                        mouseX = sliderMax
                    if mouseX < sliderMin:
                        mouseX = sliderMin
                    timeAtLastInterval = timeNow
                    oldMouseX=mouseX
                    sliderValue = (mouseX - sliderMin) / (sliderMax - sliderMin) * 100

                # get current time
                t = IntensityRatingClock.getTime()
                tThisFlip = win.getFutureFlipTime(clock=IntensityRatingClock)
                tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                # update/draw components on each frame
                
                # *IntensityMouse* updates
                if IntensityMouse.status == NOT_STARTED and t >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    IntensityMouse.frameNStart = frameN  # exact frame index
                    IntensityMouse.tStart = t  # local t and not account for scr refresh
                    IntensityMouse.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(IntensityMouse, 'tStartRefresh')  # time at next scr refresh
                    IntensityMouse.status = STARTED
                    IntensityMouse.mouseClock.reset()
                    prevButtonState = IntensityMouse.getPressed()  # if button is down already this ISN'T a new click
                if IntensityMouse.status == STARTED:  # only update if started and not finished!
                    if tThisFlipGlobal > IntensityMouse.tStartRefresh + ratingTime-frameTolerance:
                        # keep track of stop time/frame for later
                        IntensityMouse.tStop = t  # not accounting for scr refresh
                        IntensityMouse.frameNStop = frameN  # exact frame index
                        IntensityMouse.status = FINISHED
                    buttons = IntensityMouse.getPressed()
                    if buttons != prevButtonState:  # button state changed?
                        prevButtonState = buttons
                        if sum(buttons) > 0:  # state changed to a new click
                            IntensityRating.fillColor='white'
                            obtainedRating = 1
                
                # *IntensityRating* updates
                if IntensityRating.status == NOT_STARTED and t >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    IntensityRating.frameNStart = frameN  # exact frame index
                    IntensityRating.tStart = t  # local t and not account for scr refresh
                    IntensityRating.tStartRefresh = tThisFlipGlobal  # on global time
                    win.callOnFlip(print, "Show Intensity Rating")
                    if biopac_exists == 1:
                        win.callOnFlip(biopac.setData, biopac, 0)
                        win.callOnFlip(biopac.setData, biopac, intensity_rating)
                    win.timeOnFlip(IntensityRating, 'tStartRefresh')  # time at next scr refresh
                    IntensityRating.setAutoDraw(True)
                if IntensityRating.status == STARTED:
                    # is it time to stop? (based on global clock, using actual start)
                    if tThisFlipGlobal > IntensityRating.tStartRefresh + ratingTime-frameTolerance:
                        # keep track of stop time/frame for later
                        IntensityRating.tStop = t  # not accounting for scr refresh
                        IntensityRating.frameNStop = frameN  # exact frame index
                        win.timeOnFlip(IntensityRating, 'tStopRefresh')  # time at next scr refresh
                        IntensityRating.setAutoDraw(False)
                
                # *IntensityBlackTriangle* updates
                if IntensityBlackTriangle.status == NOT_STARTED and t >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    IntensityBlackTriangle.frameNStart = frameN  # exact frame index
                    IntensityBlackTriangle.tStart = t  # local t and not account for scr refresh
                    IntensityBlackTriangle.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(IntensityBlackTriangle, 'tStartRefresh')  # time at next scr refresh
                    IntensityBlackTriangle.setAutoDraw(True)
                if IntensityBlackTriangle.status == STARTED:
                    # is it time to stop? (based on global clock, using actual start)
                    if tThisFlipGlobal > IntensityBlackTriangle.tStartRefresh + ratingTime-frameTolerance:
                        # keep track of stop time/frame for later
                        IntensityBlackTriangle.tStop = t  # not accounting for scr refresh
                        IntensityBlackTriangle.frameNStop = frameN  # exact frame index
                        win.timeOnFlip(IntensityBlackTriangle, 'tStopRefresh')  # time at next scr refresh
                        IntensityBlackTriangle.setAutoDraw(False)
                
                # *IntensityAnchors* updates
                if IntensityAnchors.status == NOT_STARTED and t >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    IntensityAnchors.frameNStart = frameN  # exact frame index
                    IntensityAnchors.tStart = t  # local t and not account for scr refresh
                    IntensityAnchors.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(IntensityAnchors, 'tStartRefresh')  # time at next scr refresh
                    IntensityAnchors.setAutoDraw(True)
                if IntensityAnchors.status == STARTED:
                    # is it time to stop? (based on global clock, using actual start)
                    if tThisFlipGlobal > IntensityAnchors.tStartRefresh + ratingTime-frameTolerance:
                        # keep track of stop time/frame for later
                        IntensityAnchors.tStop = t  # not accounting for scr refresh
                        IntensityAnchors.frameNStop = frameN  # exact frame index
                        win.timeOnFlip(IntensityAnchors, 'tStopRefresh')  # time at next scr refresh
                        IntensityAnchors.setAutoDraw(False)
                
                # *IntensityPrompt* updates
                if IntensityPrompt.status == NOT_STARTED and t >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    IntensityPrompt.frameNStart = frameN  # exact frame index
                    IntensityPrompt.tStart = t  # local t and not account for scr refresh
                    IntensityPrompt.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(IntensityPrompt, 'tStartRefresh')  # time at next scr refresh
                    IntensityPrompt.setAutoDraw(True)
                if IntensityPrompt.status == STARTED:
                    # is it time to stop? (based on global clock, using actual start)
                    if tThisFlipGlobal > IntensityPrompt.tStartRefresh + ratingTime-frameTolerance:
                        # keep track of stop time/frame for later
                        IntensityPrompt.tStop = t  # not accounting for scr refresh
                        IntensityPrompt.frameNStop = frameN  # exact frame index
                        win.timeOnFlip(IntensityPrompt, 'tStopRefresh')  # time at next scr refresh
                        IntensityPrompt.setAutoDraw(False)

                # Autoresponder
                if t >= thisSimKey.rt and autorespond == 1:
                    sliderValue = random.randint(0,100)
                    continueRoutine = False

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
                if continueRoutine:
                    win.flip()

            # -------Ending Routine "IntensityRating"-------
            print("CueOff Channel " + str(intensity_rating))
            for thisComponent in IntensityRatingComponents:
                if hasattr(thisComponent, "setAutoDraw"):
                    thisComponent.setAutoDraw(False)
            # store data for thisExp (ExperimentHandler)
            thisExp.addData('IntensityRating.response', sliderValue)
            thisExp.addData('IntensityRating.rt', timeNow - IntensityRating.tStart)
            thisExp.nextEntry()
            thisExp.addData('IntensityRating.started', IntensityRating.tStart)
            thisExp.addData('IntensityRating.stopped', IntensityRating.tStop)

            # rating_bids_trial = []
            # rating_bids_trial.extend((onset, t, bodySites[runs], sliderValue, temperature, "2back", jitter1, jitter2))
            # rating_bids.append(rating_bids_trial)

            distractmap_bids_trial = []
            distractmap_bids_trial.extend((onset, t, None, sliderValue, None, bodySites[runs], temperature, "2back Rating", jitter2))
            distractmap_bids.append(distractmap_bids_trial)
            
            # the Routine "IntensityRating" was not non-slip safe, so reset the non-slip timer
            routineTimer.reset()

    """
    17. Save data into Excel and .CSV formats and Tying up Loose Ends
    """ 
    distractmap_bids_data = pd.DataFrame(distractmap_bids, columns = ['onset', 'duration', 'rt', 'response', 'correct', 'bodySite', 'temperature', 'condition', 'pretrial-jitter'])
    distractmap_bids_filename = sub_dir + os.sep + u'sub-%05d_ses-%02d_task-%s_acq-%s_run-%s_events.tsv' % (int(expInfo['subject number']), int(expInfo['session']), expName, bodySites[runs].replace(" ", "").lower(), str(runs+1))
    distractmap_bids_data.to_csv(distractmap_bids_filename, sep="\t")
    
    # rating_bids_data = pd.DataFrame(rating_bids, columns = ['onset', 'duration', 'bodySite', 'intensity', 'temperature', 'condition', 'pretrial-jitter', 'posttrial-jitter'])
    # rating_bids_filename = sub_dir + os.sep + u'sub-%05d_ses-%02d_task-%s_acq-%s_run-%s_events.tsv' % (int(expInfo['subject number']), int(expInfo['session']), 'distractmap-ratings', bodySites[runs].replace(" ", "").lower(), str(runs+1))
    # rating_bids_data.to_csv(rating_bids_filename, sep="\t")

    # Reset for the next run
    distractmap_bids_data = []
    distractmap_bids = []

    # rating_bids_data = []
    # rating_bids = []

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