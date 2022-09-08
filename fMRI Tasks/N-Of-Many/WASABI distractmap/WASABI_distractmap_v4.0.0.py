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

The paradigm will generate these files of name:
1x sub-XXXX_ses-XX_task-Practice1back_events.tsv
1x sub-XXXX_ses-XX_task-Practice2back_events.tsv
8x sub-XXXX_ses-XX_task-distractmap_acq-[bodySite]_run-XX_events.tsv

x16 trials per file with the following
headers:

'SID', 'date', 'gender', 'session', 'handedness', 'scanner', 'onset', 'duration', 'temperature', 'body_site', 'condition', 'rt'	'mouseclick'	'correct'	'condition'	'score' 'biopac_channel'

SID: DBIC Subject ID
date: the mm/dd/yyyy date
gender
session
handedness
scanner: Initials of the scan operator of the day. 
onset: seconds
duration: seconds
temperature
body_site
condition: string
rt: seconds
mouseclick: 
    0: left click, 1: middle click, 2: right click
correct:
    0: False, 1: True
score: float
biopac_channel

Design 4.0.0 of the Distractmap was generated because, we wanted to randomly switch between 0-back and 2-back conditions, but also have participants have these skills practiced before they enter the scanner.
The 0-back condition is supposed to control for visual stimulation and motor movement relative to the 2-back condition.

0. Import Libraries
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

from WASABI_psychopy_utilities import *
from WASABI_config import *

__author__ = "Michael Sun"
__version__ = "4.0.0"
__email__ = "msun@dartmouth.edu"
__status__ = "Production"

"""
1. Experimental Parameters
Clocks, paths, etc.
"""
# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)
main_dir = _thisDir
stimuli_dir = main_dir + os.sep + "stimuli"
instructions_dir = main_dir + os.sep + 'instruction_stim'
nback_dir = main_dir + os.sep + "nbackorder"

# Brings up the Calibration/Data folder to load the appropriate calibration data right away.
calibration_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir, 'WASABI bodyCalibration', 'data')

"""
2. Start Experimental Dialog Boxes
"""
# Upload participant file: Browse for file
# Store info about the experiment session
psychopyVersion = '2020.2.10'
expName = 'distractmap'  # from the Builder filename that created this script

expInfo = {
'DBIC Number': '', 
'gender': '',
'session': '',
'handedness': '', 
'scanner': '',
'run': '10'
}

# Load the subject's calibration file and ensure that it is valid
if debug==1:
    expInfo = {
        'DBIC Number': '999', 
        'gender': 'm',
        'session': '99',
        'handedness': 'r', 
        'scanner': 'TEST',
        'run': '1',
        'body sites': ''
    }
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
else:
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

                expInfo2 = {
                'session': '',
                'scanner': '',
                'run': '',
                'body sites': ''
                }
                dlg2 = gui.DlgFromDict(title="Distraction Map Scan", dictionary=expInfo2, sortKeys=False) 
                expInfo['session'] = expInfo2['session']
                expInfo['scanner'] = expInfo2['scanner']
                expInfo['run'] = expInfo2['run']
                expInfo['body sites'] = expInfo2['body sites']
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
        ## This is used if an appropriate calibration is not selected. Generate a list of temperature choices.
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

        subjectInfoBox("DistractMap Scan", expInfo)
        pphDlg = gui.DlgFromDict(participant_settingsHeat, 
                                title='Participant Heat Parameters')
        if pphDlg.OK == False:
            core.quit()

expInfo['date'] = data.getDateStr()  # add a simple timestamp
expInfo['psychopyVersion'] = psychopyVersion
expName = 'distractmap'
expInfo['expName'] = expName
expInfo['run']=int(expInfo['run'])


"""
3. Configure the Stimuli Arrays
"""
if expInfo['body sites']=="":
    ## Based on our discussion with Tor, these body sites will likely have to change to Right Leg and Chest.
    # bodySites1 = ['Right Leg', 'Left Face', 'Right Leg', 'Left Face']
    # bodySites2 = ['Left Face', 'Right Leg', 'Left Face', 'Right Leg'] 

    # We will only have time for 2 runs on each day.
    bodySites1 = ['Right Leg', 'Left Face']
    bodySites2 = ['Left Face', 'Right Leg'] 
    

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

""" 
4. Setup the Window
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
4. Prepare Experimental Dictionaries for Body-Site Cues and Medoc Temperature Programs
"""
cueImg = os.sep.join([stimuli_dir, "cue", "thermode.png"])
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

"""
5. Prepare files to write
"""
sub_dir = os.path.join(_thisDir, 'data', 'sub-SID%06d' % (int(expInfo['DBIC Number'])), 'ses-%02d' % (int(expInfo['session'])))
if not os.path.exists(sub_dir):
    os.makedirs(sub_dir)

varNames=['SID', 'date', 'gender', 'session', 'handedness', 'scanner', 'onset', 'duration', 'temperature', 'body_site', 'condition', 'rt', 'mouseclick', 'correct', 'score', 'biopac_channel']
nback_bids=pd.DataFrame(columns=varNames)

"""
5. Initialize Custom Components
"""
# General Instructional Text
start_msg = 'Please wait. \nThe scan will begin shortly. \n Experimenter press [s] to continue.'
in_between_run_msg = 'Thank you.\n Please wait for the next scan to start \n Experimenter press [e] to continue.'
end_msg = 'Please wait for instructions from the experimenter'

InstructionText = "Welcome to N-back testing. \n\nRemember your practice, \nLeft Click for \"yes\" and Right Click for \"no\"\n\nWe will add some difficulty by periodically sending painful thermal stimulations to a designated body-site. \nDuring the task it is very important that you respond as fast and as accurately as possible.\n\n\nYou should try to respond shortly after the square is presented. This might be difficult, so it is important that you concentrate!\n\nExperimenter press [Space] to continue."

# Rating question text
painText="Was that painful?"
trialIntensityText="How intense was the heat stimulation?"
distractText="Was the pain distracting?"

stimtrialTime = 15 # This becomes very unreliable with the use of poll_for_change().

if debug==1:
    ratingTime = 1 # Rating Time limit in seconds during the inter-stimulus-interval
else:    
    ratingTime = 5 # Rating Time limit in seconds during the inter-stimulus-interval

# create a default keyboard (e.g. to check for escape)
defaultKeyboard = keyboard.Keyboard()

# 06/29/2022: Tor suggested we impose mini-blocks of each condition
# Number of trials per mini-block of each of 4 conditions.
trials_per_block=3

# 06/29/2022: Tor suggested we add an audio ding
rating_sound=mySound=sound.Sound('B', octave=5, stereo=1, secs=.5)  
## When you want to play the sound, run this line of code:
# rating_sound.play()

IntensityText = 'HOW INTENSE was the WORST heat you experienced?'
ComfortText = "How comfortable do you feel right now?" # (Bipolar)
ValenceText = "HOW UNPLEASANT was the WORST heat you experienced?"  # 0 -- Most Unpleasant (Unipolar)
AvoidText = "Please rate HOW MUCH you want to avoid this experience in the future?" # Not at all -- Most(Unipolar)
RelaxText = "How relaxed are you feeling right now?" # Least relaxed -- Most Relaxed (Unipolar)
TaskAttentionText = "During the last scan, how well could you keep your attention on the task?" # Not at all -- Best (Unipolar)
BoredomText = "During the last scan, how bored were you?" # Not bored at all -- Extremely Bored (Unipolar)
AlertnessText = "During the last scan how sleepy vs. alert were you?" # Extremely Sleepy - Neutral - Extremely Alert (Bipolar)
PosThxText = "The thoughts I experienced during the last scan were POSITIVE" # Strongly disagree - Neither - Strongly Agree (Bipolar)
NegThxText = "The thoughts I experienced during the last scan were NEGATIVE" # Strongly disagree - Neither - Strongly agree (bipolar)
SelfText = "The thoughts I experienced during the last scan were related to myself" # Strongly disagree -- Neither -- Strongly Agree (Bipolar)
OtherText = "The thoughts I experienced during the last scan concerned other people." # Strongly disagree - Neither - Strongly agree (Bipolar)
ImageryText = "The thoughts I experienced during the last scan were experienced with clear and vivid mental imagery" # Strongly disagree - Neither - Strongly agree (bipolar)
PresentText = "The thoughts I experienced during the last scan pertained to the immediate PRESENT (the here and now)" # Strongly disagree - Neither - Strongly agree (bipolar)

######################
# N-Back Task Components
######################
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

if biopac_exists:
    biopac.setData(biopac, 0)
    biopac.setData(biopac, task_ID) # Start demarcation of the T1 task in Biopac Acqknowledge

win.mouseVisible = False

"""
7. Welcome and Button Test
"""
showText(win, "Instructions", InstructionText, biopacCode=instructions, noRecord=True)
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

ClickToContinueText = "Click to continue"
ClickToStartText = "Click to start practice"

###################
# Real Trials Start
###################

# 6/29/2022: Tor's suggestion: Mini-blocks of 3 trials each.
# 1. 1x 0-back Task - no-stimulation                       [3 trials]
# 2. 2x 0-back Task - Cue + high-heat stimulation (~49 degrees)  [6 trials]
# 3. 1x 2-back Task - No Stimulation                       [3 trials]
# 4. 2x 2-back Task - Cue + high-heat stimulation (~49 degrees)  [6 trials]
# There should be no back-to-back repetitions of blocks of the same condition

BigTrialList = [[4, 1, 2, 3, 4, 2], 
                [2, 3, 4, 2, 1, 4],
                [3, 4, 1, 2, 4, 2],
                [1, 4, 2, 3, 2, 4],
                [2, 3, 4, 1, 4, 2],
                [3, 2, 4, 1, 2, 4],
                [1, 2, 4, 3, 2, 4],
                [4, 2, 4, 1, 2, 3],
                [4, 3, 2, 1, 4, 2]]

# if expInfo['run']>1:
#     runRange=range(expInfo['run'], expInfo['run']+4)
# else:
#     runRange=range(10, 10+len(bodySites)) # +1 for hyperalignment

# for runs in runRange:
for runs in range(len(bodySites)):
    # Reset the trial possibilities for every run.
    ZerobackFiles = ["N-back-0_1.xlsx", "N-back-0_2.xlsx", "N-back-0_3.xlsx", "N-back-0_4.xlsx", 
                    "N-back-0_5.xlsx", "N-back-0_6.xlsx", "N-back-0_7.xlsx", "N-back-0_8.xlsx",
                    "N-back-0_1.xlsx", "N-back-0_2.xlsx", "N-back-0_3.xlsx", "N-back-0_4.xlsx", 
                    "N-back-0_5.xlsx", "N-back-0_6.xlsx", "N-back-0_7.xlsx", "N-back-0_8.xlsx"
                    ]
    TwobackFiles = ["N-back-2_1.xlsx", "N-back-2_2.xlsx", "N-back-2_3.xlsx", "N-back-2_4.xlsx", 
                    "N-back-2_5.xlsx", "N-back-2_6.xlsx", "N-back-2_7.xlsx", "N-back-2_8.xlsx",
                    "N-back-2_1.xlsx", "N-back-2_2.xlsx", "N-back-2_3.xlsx", "N-back-2_4.xlsx", 
                    "N-back-2_5.xlsx", "N-back-2_6.xlsx", "N-back-2_7.xlsx", "N-back-2_8.xlsx"]

    random.shuffle(ZerobackFiles)
    random.shuffle(TwobackFiles)

    """
    8. Body-Site Instructions: Instruct the Experimenter on the Body Sites to attach thermodes to at the beginning of each run
    """
    random.shuffle(BigTrialList)
    BlockTrials=BigTrialList.pop()
    bodysiteInstruction="Experimenter: \nPlease place the thermode on the: \n" + bodySites[runs].lower()
    showTextAndImg(win, "Bodysite Instruction", bodysiteInstruction, imgPath=bodysite_word2img[bodySites[runs]], biopacCode=bodymapping_instruction, noRecord=True)
    routineTimer.reset()

    """
    9. Set Trial parameters
    """
    jitter2 = None  # Reset Jitter2
    bodySiteData = bodySites[runs]
    BiopacChannel = bodysite_word2heatcode[bodySites[runs]]
    temperature = participant_settingsHeat[bodySites[runs]]
    thermodeCommand = thermode_temp2program[temperature]

    """
    10. Start Scanner
    """
    fmriStart=confirmRunStart(win)

    for r in BlockTrials: # 6 blocks
        if r==1 or r==2:    # 0-back, no-stimulation, and high-heat stimulation
            rating_sound.play()
            nback_bids=nback_bids.append(showText(win, "0-back Instruction", "ready...\n0-back", fontSize=0.15, time=5, biopacCode=zeroback_instructions), ignore_index=True)

            for trial_in_mini_block in range(trials_per_block):
                """
                14i. Select Medoc Thermal Program
                """
                if r==2 and thermode_exists == 1:
                    sendCommand('select_tp', thermodeCommand)
                    # Show Heat Cue
                    # Need a biopac code
                    nback_bids=nback_bids.append(showImg(win, "Cue", imgPath=cueImg, time=2, biopacCode=cue), ignore_index=True)

                """ 
                14ii. Pre-Trial Fixation Cross
                """
                # ------Prepare to start Routine "Fixation"-------
                continueRoutine = True
                if not jitter2:
                    jitter1 = random.choice([5,7,9])
                elif jitter2 == 5:
                    jitter1 = 9
                elif jitter2 == 7:
                    jitter1 = 7
                elif jitter2 == 9:
                    jitter1 = 5
                if debug==1:
                    jitter1=1

                nback_bids=nback_bids.append(showFixation(win, "Pre-trial Fixation", type='big', time=jitter1, biopacCode=prefixation), ignore_index=True)
             
                """ 
                14iv. 0-back Task
                """
                Nback = os.sep.join([nback_dir, ZerobackFiles.pop()])
                
                if r==2:
                    # Trigger Thermal Program
                    if thermode_exists == 1:
                        sendCommand('trigger') # Trigger the thermode
                    nback_bids['temperature'].iloc[-1]=temperature
                else:
                    nback_bids['temperature'].iloc[-1]=32    
                nback_bids = nback_bids.append(nback(win, "0-back", answers=Nback, cheat=cheat, feedback=False), ignore_index=True)

                if debug==1:
                    jitter2=1
                else:
                    jitter2 = random.choice([5,7,9])
                nback_bids=nback_bids.append(showFixation(win, "Post-trial Fixation", type='small', time=jitter2, biopacCode=midfixation), ignore_index=True)

                if r==2:
                    """
                    14v. 0-Back Pain Rating Trial
                    """
                    rating_sound.play() # Play a sound to ensure the participant is awake.
                    nback_bids=nback_bids.append(showRatingScale(win, "PainBinary", painText, os.sep.join([stimuli_dir,"ratingscale","YesNo.png"]), type="binary", time=ratingTime, biopacCode=pain_binary), ignore_index=True)
                    nback_bids=nback_bids.append(showRatingScale(win, "IntensityRating", trialIntensityText, os.sep.join([stimuli_dir,"ratingscale","intensityScale.png"]), type="unipolar", time=ratingTime, biopacCode=trialIntensity_rating), ignore_index=True)
                    nback_bids=nback_bids.append(showRatingScale(win, "DistractBinary", distractText, os.sep.join([stimuli_dir,"ratingscale","YesNo.png"]), type="binary", time=ratingTime, biopacCode=distract_binary), ignore_index=True)
                    rating_sound.stop()

                    """
                    14vi. Post-Question jitter
                    """
                    if debug==1:
                        jitter3=1
                    else:
                        jitter3 = random.choice([5,7,9])
                    nback_bids=nback_bids.append(showFixation(win, "Post-Q-Jitter", type='big', time=jitter2, biopacCode=postfixation), ignore_index=True)

        if r==3 or r==4:
            for trial_in_mini_block in range(trials_per_block):
                """ 
                15. Begin 2-Back Trials
                """
                rating_sound.play()
                nback_bids=nback_bids.append(showText(win, "2-back Instruction", "ready...\n2-back", fontSize=0.15, time=5, biopacCode=twoback_instructions), ignore_index=True)

                """
                15i. Select Medoc Thermal Program
                """
                if r==4 and thermode_exists == 1:
                    # Show Heat Cue
                    # Need a biopac code
                    nback_bids=nback_bids.append(showImg(win, "Cue", imgPath=cueImg, time=2, biopacCode=cue), ignore_index=True)

                    sendCommand('select_tp', thermodeCommand)

                """ 
                15ii. Pre-Trial Fixation Cross
                """
                # ------Prepare to start Routine "Fixation"-------
                continueRoutine = True
                if not jitter2:
                    jitter1 = random.choice([5,7,9])
                elif jitter2 == 5:
                    jitter1 = 9
                elif jitter2 == 7:
                    jitter1 = 7
                elif jitter2 == 9:
                    jitter1 = 5
                if debug==1:
                    jitter1=1

                nback_bids=nback_bids.append(showFixation(win, "Pre-trial Jitter", type='big', time=jitter1, biopacCode=prefixation), ignore_index=True)
             
                """ 
                15iv. 2-back Task
                """
                Nback = os.sep.join([nback_dir, TwobackFiles.pop()])
                
                if r==4:
                    # Trigger Thermal Program
                    if thermode_exists == 1:
                        sendCommand('trigger') # Trigger the thermode
                    nback_bids['temperature'].iloc[-1]=temperature
                else:
                    nback_bids['temperature'].iloc[-1]=32    
                nback_bids = nback_bids.append(nback(win, "2-back", answers=Nback, cheat=cheat, feedback=False), ignore_index=True)
                
                if debug==1:
                    jitter2=1
                else:
                    jitter2 = random.choice([5,7,9])
                nback_bids=nback_bids.append(showFixation(win, "Post-trial Jitter", type='big', time=jitter2, biopacCode=midfixation), ignore_index=True)

                if r==4:
                    """
                    15v. 2-Back Pain Rating Trial
                    """
                    rating_sound.play() # Play a sound to ensure the participant is awake.
                    nback_bids=nback_bids.append(showRatingScale(win, "PainBinary", painText, os.sep.join([stimuli_dir,"ratingscale","YesNo.png"]), type="binary", time=ratingTime, biopacCode=pain_binary), ignore_index=True)
                    nback_bids=nback_bids.append(showRatingScale(win, "IntensityRating", trialIntensityText, os.sep.join([stimuli_dir,"ratingscale","intensityScale.png"]), type="unipolar", time=ratingTime, biopacCode=trialIntensity_rating), ignore_index=True)
                    nback_bids=nback_bids.append(showRatingScale(win, "DistractBinary", distractText, os.sep.join([stimuli_dir,"ratingscale","YesNo.png"]), type="binary", time=ratingTime, biopacCode=distract_binary), ignore_index=True)
                    rating_sound.stop()
                    
                    """
                    15vi. Post-Question jitter
                    """
                    if debug==1:
                        jitter3=1
                    else:
                        jitter3 = random.choice([5,7,9])
                    nback_bids=nback_bids.append(showFixation(win, "Post-Q-Jitter", type='big', time=jitter2, biopacCode=postfixation), ignore_index=True)

    """
    16. Begin post-run self-report questions
    """        
    rating_sound.stop() # I think a stop needs to be introduced in order to play again.
    rating_sound.play()

    nback_bids=nback_bids.append(showRatingScale(win, "ComfortRating", ComfortText, os.sep.join([stimuli_dir,"ratingscale","ComfortScale.png"]), type="bipolar", biopacCode=comfort_rating), ignore_index=True)
    nback_bids=nback_bids.append(showRatingScale(win, "ValenceRating", ValenceText, os.sep.join([stimuli_dir,"ratingscale","postvalenceScale.png"]), type="bipolar", biopacCode=valence_rating), ignore_index=True)
    nback_bids=nback_bids.append(showRatingScale(win, "IntensityRating", IntensityText, os.sep.join([stimuli_dir,"ratingscale","postintensityScale.png"]), type="unipolar", biopacCode=comfort_rating), ignore_index=True)
    nback_bids=nback_bids.append(showRatingScale(win, "AvoidanceRating", AvoidText, os.sep.join([stimuli_dir,"ratingscale","AvoidScale.png"]), type="bipolar", biopacCode=avoid_rating), ignore_index=True)
    nback_bids=nback_bids.append(showRatingScale(win, "RelaxationRating", RelaxText, os.sep.join([stimuli_dir,"ratingscale","RelaxScale.png"]), type="bipolar", biopacCode=relax_rating), ignore_index=True)
    nback_bids=nback_bids.append(showRatingScale(win, "AttentionRating", TaskAttentionText, os.sep.join([stimuli_dir,"ratingscale","TaskAttentionScale.png"]), type="bipolar", biopacCode=taskattention_rating), ignore_index=True)
    nback_bids=nback_bids.append(showRatingScale(win, "BoredomRating", BoredomText, os.sep.join([stimuli_dir,"ratingscale","BoredomScale.png"]), type="bipolar", biopacCode=boredom_rating), ignore_index=True)
    nback_bids=nback_bids.append(showRatingScale(win, "AlertnessRating", AlertnessText, os.sep.join([stimuli_dir,"ratingscale","AlertnessScale.png"]), type="bipolar", biopacCode=alertness_rating), ignore_index=True)
    nback_bids=nback_bids.append(showRatingScale(win, "PosThxRating", PosThxText, os.sep.join([stimuli_dir,"ratingscale","PosThxScale.png"]), type="bipolar", biopacCode=posthx_rating), ignore_index=True)
    nback_bids=nback_bids.append(showRatingScale(win, "NegThxRating", NegThxText, os.sep.join([stimuli_dir,"ratingscale","NegThxScale.png"]), type="bipolar", biopacCode=negthx_rating), ignore_index=True)  
    nback_bids=nback_bids.append(showRatingScale(win, "SelfRating", SelfText, os.sep.join([stimuli_dir,"ratingscale","SelfScale.png"]), type="bipolar", biopacCode=self_rating), ignore_index=True)
    nback_bids=nback_bids.append(showRatingScale(win, "OtherRating", OtherText, os.sep.join([stimuli_dir,"ratingscale","OtherScale.png"]), type="bipolar", biopacCode=other_rating), ignore_index=True)
    nback_bids=nback_bids.append(showRatingScale(win, "ImageryRating", ImageryText, os.sep.join([stimuli_dir,"ratingscale","ImageryScale.png"]), type="bipolar", biopacCode=posthx_rating), ignore_index=True)
    nback_bids=nback_bids.append(showRatingScale(win, "PresentRating", PresentText, os.sep.join([stimuli_dir,"ratingscale","PresentScale.png"]), type="bipolar", biopacCode=present_rating), ignore_index=True)

    rating_sound.stop() # Stop the sound so it can be played again.

    """
    17. Save data into .TSV formats and Tying up Loose Ends
    """ 
    # Append constants to the entire run
    nback_bids['SID']=expInfo['DBIC Number']
    nback_bids['date']=expInfo['date']
    nback_bids['gender']=expInfo['gender']
    nback_bids['session']=expInfo['session']
    nback_bids['handedness']=expInfo['handedness']
    nback_bids['scanner']=expInfo['scanner']
    nback_bids['body_site']=bodySites[runs]
    
    nback_bidsfilename = sub_dir + os.sep + u'sub-SID%06d_ses-%02d_task-%s_acq-%s_run-%s_events.tsv' % (int(expInfo['DBIC Number']), int(expInfo['session']), expName, bodySites[runs].replace(" ", "").lower(), str(expInfo['run']+runs))
    
    nback_bids.to_csv(nback_bidsfilename, sep="\t")
    nback_bids=pd.DataFrame(columns=varNames) # Clear it out for a new file.

    """
    18. End of Run, Wait for Experimenter instructions to begin next run
    """   
    nextRun(win)

"""
19. Wrap up
"""
endScan(win)

"""
End of Experiment
"""