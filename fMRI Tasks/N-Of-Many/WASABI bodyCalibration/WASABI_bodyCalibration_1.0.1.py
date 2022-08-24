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

The paradigm will generate 8x of these files of name:
sub-SIDXXXXX_task-bodyCalibration_acq-[bodysite]_run-XX_events.tsv

Trials per file are defined by the following headers:
onset   duration    trial_type  body_site   temp

after every stimulation there will be rows for:
[x] "Was that painful?"
[x] "How intense was the heat stimulation?" (Bartoshuk gLMS)
[x] "Was it tolerable, and can you take more of that heat?"

The design is as follows:
1. Start with a 48 degree stimulation trial (to be thrown away)
2. If not painful, increase the temperature by .5 degrees (max at 48.5)
3. If intolerable, then reduce the temperature by .5 degrees and set that new temperature as the maximum temperature for the bodysite.
4. Average the ratings of the 6 subsequent trials

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
from datetime import datetime

__author__ = "Michael Sun"
__version__ = "1.0.1"
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

# Set this later
# task_ID=8   # If experience
# task_ID=9  # If regulate

task_ID=1
task_start=7

bodymapping_instruction=15
leftface_heat=17
rightface_heat=18
leftarm_heat=19
rightarm_heat=20
leftleg_heat=21
rightleg_heat=22
chest_heat=23
abdomen_heat=24

instruction_code=198

pain_binary=42
intensity_rating=43
tolerance_binary=44

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

"""
2. Start Experimental Dialog Boxes
"""
# Upload participant file: Browse for file
# Store info about the experiment session
psychopyVersion = '2020.2.10'
expName = 'bodyCalibration'  # from the Builder filename that created this script
if debug == 1:
    expInfo = {
    'DBIC Number': '99',
    'dob (mm/dd/yyyy)': '06/20/1988',
    'gender': 'm',
    'session': '99',
    'handedness': 'r', 
    'scanner': 'MS',
    }
else:
    expInfo = {
    'DBIC Number': '',
    'dob (mm/dd/yyyy)': '', 
    'gender': '',
    'session': '',
    'handedness': '', 
    'scanner': '',
    }


dlg = gui.DlgFromDict(title="WASABI BodyCalibration Scan", dictionary=expInfo, sortKeys=False)
if dlg.OK == False:
    core.quit()  # user pressed cancel

expInfo['date'] = data.getDateStr()  # add a simple timestamp
expInfo['psychopyVersion'] = psychopyVersion
expInfo['expName'] = expName

InstructionText = "Experience the following sensations as they come."

"""
5. Configure the Body-Site for each run
"""
bodySites = ["Left Face", "Right Face", "Left Arm", "Right Arm", "Left Leg", "Right Leg", "Chest", "Abdomen"]
random.shuffle(bodySites)

# If bodysites and run order need to be manually set for the participant uncomment below and edit:
# bodySites = ["Left Leg"]

expInfo['body_site_order'] = str(bodySites)
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
4. Prepare files to write
"""
sub_dir = os.path.join(_thisDir, 'data', 'sub-SID%06d' % (int(expInfo['DBIC Number'])), 'ses-%02d' % (int(expInfo['session'])))
if not os.path.exists(sub_dir):
    os.makedirs(sub_dir)

psypy_filename = os.path.join(sub_dir, 'SID%06d_%s_%s' % (int(expInfo['DBIC Number']), expName, expInfo['date']))

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

bodyCalibration_bids_total = []
bodyCalibration_bids_trial = []
bodyCalibration_bids = []

averaged_data = []


"""
5. Initialize Trial-level Components
"""
# General Instructional Text
start_msg = 'Please wait. \nThe scan will begin shortly. \n Experimenter press [s] to continue.'
s_text='[s]-press confirmed.'
in_between_run_msg = 'Thank you.\n Please wait for the next scan to start \n Experimenter press [e] to continue.'
end_msg = 'Please wait for instructions from the experimenter'

totalTrials = 7 # Figure out how many trials would be equated to 5 minutes
stimtrialTime = 20 # This becomes very unreliable with the use of poll_for_change().

if debug == 1:
    stimtrialTime = 1 # This becomes very unreliable with the use of poll_for_change().
    totalTrials = 2
# create a default keyboard (e.g. to check for escape)
defaultKeyboard = keyboard.Keyboard()

# 06/29/2022: Tor suggested we add an audio ding
rating_sound=mySound=sound.Sound('B', octave=5, stereo=1, secs=.5)  
## When you want to play the sound, run this line of code:
# rating_sound.play()

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

# Initialize components for Routine "Instructions"
InstructionsClock = core.Clock()
Instructions = visual.TextStim(win=win, name='Instructions',
    text='Welcome to the scan\nPlease read the following instructions \nvery carefully.\n\n\n\nExperimenter press [Space] to continue.',
    font='Arial', wrapWidth=1.75,
    pos=(0, 0.0), units='height', height=0.05, 
    color='white', colorSpace='rgb', opacity=1)

# Initialize components for Routine "Fixation"
FixationClock = core.Clock()
fixation = visual.TextStim(win=win, name='fixation',
    text='+',
    font='Arial',
    pos=(0, 0), height=0.05, wrapWidth=None, ori=0, 
    color='white', colorSpace='rgb', opacity=1, 
    languageStyle='LTR',
    depth=-2.0)

# Initialize components for each Rating
TIME_INTERVAL = 0.005   # Speed at which slider ratings udpate
ratingScaleWidth=1.5
ratingScaleHeight=.4
sliderMin = -.75
sliderMax = .75
bipolar_verts = [(sliderMin, .2),    # left point
                        (sliderMax, .2),    # right point
                        (0, -.2)]           # bottom-point
unipolar_verts = [(sliderMin, .2), # left point
            (sliderMax, .2),     # right point
            (sliderMin, -.2)]   # bottom-point, # bottom-point

## These Ratings are taken after every heat stimulation
painText="Was that painful?"
intensityText="How intense was the heat stimulation?"
tolerableText="Was it tolerable, and can you take more of that heat?"

# Initialize components for Routine "PainBinary"
PainBinaryClock = core.Clock()
PainBinary = visual.Rect(win, height=ratingScaleHeight, width=0, pos= [0, 0], fillColor='red', lineColor='black')
PainMouse = event.Mouse(win=win)
PainMouse.mouseClock = core.Clock()
PainAnchors = visual.ImageStim(
    win=win,
    image= os.sep.join([stimuli_dir,"ratingscale","YesNo.png"]),
    name='PainQuestion', 
    mask=None,
    ori=0, pos=(0, 0), size=(1, .25),
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=512, interpolate=True, depth=0.0)
PainPrompt = visual.TextStim(win, name='PainPrompt', 
    text=painText,
    font = 'Arial',
    pos=(0, 0.3), height=0.05, wrapWidth=None, ori=0, 
    color='white', colorSpace='rgb', opacity=1, 
    languageStyle='LTR',
    depth=0.0,
    anchorHoriz='center')

# Initialize components for Routine "IntensityRating"
IntensityRatingClock = core.Clock()
IntensityMouse = event.Mouse(win=win)
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

# Initialize components for Routine "ToleranceBinary"
ToleranceBinaryClock = core.Clock()
ToleranceBinary = visual.Rect(win, height=ratingScaleHeight, width=0, pos= [0, 0], fillColor='red', lineColor='black')
ToleranceMouse = event.Mouse(win=win)
ToleranceMouse.mouseClock = core.Clock()
ToleranceAnchors = visual.ImageStim(
    win=win,
    image= os.sep.join([stimuli_dir,"ratingscale","YesNo.png"]),
    name='ToleranceQuestion', 
    mask=None,
    ori=0, pos=(0, 0), size=(1, .25),
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=512, interpolate=True, depth=0.0)
TolerancePrompt = visual.TextStim(win, name='TolerancePrompt', 
    text=tolerableText,
    font = 'Arial',
    pos=(0, 0.3), height=0.05, wrapWidth=None, ori=0, 
    color='white', colorSpace='rgb', opacity=1, 
    languageStyle='LTR',
    depth=0.0,
    anchorHoriz='center')


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
# Show Instructions for 6 seconds
Instructions.draw()
win.flip()
continueRoutine=True
while continueRoutine == True:
    if 'space' in event.getKeys(keyList = 'space'):
        continueRoutine = False

for runs in range(len(bodySites)):
    ratingTime = 5 # Intensity Rating Time limit in seconds during the inter-trial-interval

    """
    7. Body-Site Instructions: Instruct the Experimenter on the Body Sites to attach thermodes to at the beginning of each run 
    """
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
    # the Routine "BodySiteInstruction" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()

    """
    8. Start Scanner
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
                s_confirm = visual.TextStim(win, text=s_text, height =.05, color="green", pos=(0.0, -.3))
                start.draw()
                s_confirm.draw()
                win.flip()
                event.clearEvents()
                if debug==1:
                    continueRoutine=False
                while continueRoutine == True:
                    if '5' in event.getKeys(keyList = '5'): # fMRI trigger
                        fmriStart = globalClock.getTime()   # Start the clock
                        timer = core.CountdownTimer()   # Wait 6 TRs, Dummy Scans
                        timer.add(TR*6)
                        while timer.getTime() > 0:
                            continue
                        continueRoutine = False

    """
    9. Set Trial parameters
    """
    jitter2 = None  # Reset Jitter2

    currentTemp=48
    maxTemp=48.5
    minTemp=45

    bodySiteData = bodySites[runs]
    BiopacChannel = bodysite_word2heatcode[bodySites[runs]]
    # thermodeCommand = 135 # 49 degrees
    # thermodeCommand = 132 # Set to 47.5 for Maryam
    routineTimer.reset()

    """
    10. Start Trial Loop
    """
    for r in range(totalTrials): # 7 repetitions
        """
        11. Show the Instructions prior to the First Trial
        """
        if r == 0:      # First trial
            Instructions.setText(InstructionText)
            Instructions.draw()
            if biopac_exists:
                biopac.setData(biopac, 0)
                biopac.setData(biopac, instruction_code)
            onset = globalClock.getTime() - fmriStart
            win.flip()

            timer = core.CountdownTimer()
            if debug==1:
                timer.add(1)
            else:
                timer.add(5)
            while timer.getTime() > 0:
                continue
            
            bodyCalibration_bids_trial = []
            bodyCalibration_bids_trial.extend((onset, globalClock.getTime() - fmriStart - onset, None, None, bodySites[runs], currentTemp, 'Instruction', None))
            bodyCalibration_bids.append(bodyCalibration_bids_trial)
            
            routineTimer.reset()

        # Select Medoc Thermal Program
        if thermode_exists == 1:
            sendCommand('select_tp', thermode1_temp2program[currentTemp])

        """ 
        12. Pre-Heat Fixation Cross
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

        if debug==1:
            jitter1=1
            jitter2=1

        routineTimer.add(jitter1)
        # update component parameters for each repeat
        # keep track of which components have finished
        FixationComponents = [fixation]
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
            
            # *fixation* updates
            if fixation.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                fixation.frameNStart = frameN  # exact frame index
                fixation.tStart = t  # local t and not account for scr refresh
                fixation.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(fixation, 'tStartRefresh')  # time at next scr refresh
                # if biopac_exists:
                #     win.callOnFlip(biopac.setData, biopac, 0)
                #     win.callOnFlip(biopac.setData, biopac, acceptmap_fixation)
                fixation.setAutoDraw(True)
            if fixation.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > fixation.tStartRefresh + jitter1-frameTolerance:
                    # keep track of stop time/frame for later
                    fixation.tStop = t  # not accounting for scr refresh
                    fixation.frameNStop = frameN  # exact frame index
                    win.timeOnFlip(fixation, 'tStopRefresh')  # time at next scr refresh
                    fixation.setAutoDraw(False)
            
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
        thisExp.addData('fixation.started', fixation.tStartRefresh)
        thisExp.addData('fixation.stopped', fixation.tStopRefresh)

        routineTimer.reset()

        """ 
        13. Heat-Trial Fixation Cross
        """
        # ------Prepare to start Routine "Fixation"-------
        # Trigger Thermal Program
        if thermode_exists == 1:
            sendCommand('trigger') # Trigger the thermode

        continueRoutine = True

        routineTimer.add(stimtrialTime)

        # update component parameters for each repeat
        # keep track of which components have finished
        FixationComponents = [fixation]
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
        onset = globalClock.getTime() - fmriStart           # Record onset time of the trial
        while continueRoutine and routineTimer.getTime() > 0:
            # get current time
            t = FixationClock.getTime()
            tThisFlip = win.getFutureFlipTime(clock=FixationClock)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame
            
            # *fixation* updates
            if fixation.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                fixation.frameNStart = frameN  # exact frame index
                fixation.tStart = t  # local t and not account for scr refresh
                fixation.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(fixation, 'tStartRefresh')  # time at next scr refresh
                if biopac_exists:
                    win.callOnFlip(biopac.setData, biopac, 0)
                    win.callOnFlip(biopac.setData, biopac, BiopacChannel)
                fixation.setAutoDraw(True)
            if fixation.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > fixation.tStartRefresh + stimtrialTime-frameTolerance:
                    # keep track of stop time/frame for later
                    fixation.tStop = t  # not accounting for scr refresh
                    fixation.frameNStop = frameN  # exact frame index
                    win.timeOnFlip(fixation, 'tStopRefresh')  # time at next scr refresh
                    fixation.setAutoDraw(False)
            
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
        thisExp.addData('fixation.started', fixation.tStartRefresh)
        thisExp.addData('fixation.stopped', fixation.tStopRefresh)

        bodyCalibration_bids_trial = []
        bodyCalibration_bids_trial.extend((onset, globalClock.getTime() - fmriStart - onset, r+1, None, bodySites[runs], currentTemp, 'Heat Stimulation', jitter1))
        bodyCalibration_bids.append(bodyCalibration_bids_trial)

        routineTimer.reset()

        """
        14. Post-Heat Fixation Cross
        """
        # ------Prepare to start Routine "Fixation"-------
        continueRoutine = True
        jitter2 = random.choice([3,5,7])

        if debug==1:
            jitter1=1
            jitter2=1


        routineTimer.add(jitter2)

        # update component parameters for each repeat
        # keep track of which components have finished
        FixationComponents = [fixation]
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
            
            # *fixation* updates
            if fixation.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                fixation.frameNStart = frameN  # exact frame index
                fixation.tStart = t  # local t and not account for scr refresh
                fixation.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(fixation, 'tStartRefresh')  # time at next scr refresh
                # if biopac_exists:
                #     win.callOnFlip(biopac.setData, biopac, 0)
                #     win.callOnFlip(biopac.setData, biopac, nback_fixation)
                fixation.setAutoDraw(True)
            if fixation.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > fixation.tStartRefresh + jitter2-frameTolerance:
                    # keep track of stop time/frame for later
                    fixation.tStop = t  # not accounting for scr refresh
                    fixation.frameNStop = frameN  # exact frame index
                    win.timeOnFlip(fixation, 'tStopRefresh')  # time at next scr refresh
                    fixation.setAutoDraw(False)
            
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
        thisExp.addData('fixation.started', fixation.tStartRefresh)
        thisExp.addData('fixation.stopped', fixation.tStopRefresh)

        rating_sound.play()
        routineTimer.reset()

        """
        8f. Begin post-trial self-report questions
        """        
        ############ ASK PAIN BINARY Question #######################################
        # ------Prepare to start Routine "PainBinary"-------
        continueRoutine = True
        routineTimer.add(ratingTime)
        # update component parameters for each repeat
        # setup some python lists for storing info about the mouse
        
        PainMouse = event.Mouse(win=win, visible=False) # Re-initialize PainMouse
        PainMouse.setPos((0,0))
        timeAtLastInterval = 0
        mouseX = 0
        oldMouseX = 0
        PainBinary.width = 0
        PainBinary.pos = (0,0)
        
        # keep track of which components have finished
        PainBinaryComponents = [PainMouse, PainBinary, PainAnchors, PainPrompt]
        for thisComponent in PainBinaryComponents:
            thisComponent.tStart = None
            thisComponent.tStop = None
            thisComponent.tStartRefresh = None
            thisComponent.tStopRefresh = None
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        # reset timers
        t = 0
        _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        PainBinaryClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
        frameN = -1

        # -------Run Routine "PainBinary"-------
        onset = globalClock.getTime() - fmriStart           # Record onset time of the trial
        while continueRoutine:
            # get current time
            t = PainBinaryClock.getTime()
            tThisFlip = win.getFutureFlipTime(clock=PainBinaryClock)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame

            timeNow = globalClock.getTime()
            if (timeNow - timeAtLastInterval) > TIME_INTERVAL:
                mouseRel=PainMouse.getRel()
                mouseX=oldMouseX + mouseRel[0]

            if mouseX==0:
                PainBinary.width = 0
            else:
                if mouseX>0:
                    PainBinary.pos = (.28,0)
                    sliderValue=1
                elif mouseX<0:
                    PainBinary.pos = (-.4,0)
                    sliderValue=-1
                PainBinary.width = .5

            timeAtLastInterval = timeNow
            oldMouseX=mouseX


            # *PainMouse* updates
            if PainMouse.status == NOT_STARTED and t >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                PainMouse.frameNStart = frameN  # exact frame index
                PainMouse.tStart = t  # local t and not account for scr refresh
                PainMouse.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(PainMouse, 'tStartRefresh')  # time at next scr refresh
                PainMouse.status = STARTED
                PainMouse.mouseClock.reset()
                prevButtonState = PainMouse.getPressed()  # if button is down already this ISN'T a new click
            if PainMouse.status == STARTED:  # only update if started and not finished!
                if tThisFlipGlobal > PainMouse.tStartRefresh + ratingTime-frameTolerance:
                    # keep track of stop time/frame for later
                    PainMouse.tStop = t  # not accounting for scr refresh
                    PainMouse.frameNStop = frameN  # exact frame index
                    PainMouse.status = FINISHED
                buttons = PainMouse.getPressed()
                if buttons != prevButtonState:  # button state changed?
                    prevButtonState = buttons
                    if sum(buttons) > 0:  # state changed to a new click
                        # abort routine on response
                        continueRoutine = False

            # *PainBinary* updates
            if PainBinary.status == NOT_STARTED and t >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                PainBinary.frameNStart = frameN  # exact frame index
                PainBinary.tStart = t  # local t and not account for scr refresh
                PainBinary.tStartRefresh = tThisFlipGlobal  # on global time
                win.callOnFlip(print, "Show Pain Rating")
                if biopac_exists == 1:
                    win.callOnFlip(biopac.setData, biopac, 0)
                    win.callOnFlip(biopac.setData, biopac, pain_binary)
                win.timeOnFlip(PainBinary, 'tStartRefresh')  # time at next scr refresh
                PainBinary.setAutoDraw(True)
            if PainBinary.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > PainBinary.tStartRefresh + ratingTime-frameTolerance:
                    # keep track of stop time/frame for later
                    PainBinary.tStop = t  # not accounting for scr refresh
                    PainBinary.frameNStop = frameN  # exact frame index
                    win.timeOnFlip(PainBinary, 'tStopRefresh')  # time at next scr refresh
                    PainBinary.setAutoDraw(False)
            
            # *PainAnchors* updates
            if PainAnchors.status == NOT_STARTED and t >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                PainAnchors.frameNStart = frameN  # exact frame index
                PainAnchors.tStart = t  # local t and not account for scr refresh
                PainAnchors.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(PainAnchors, 'tStartRefresh')  # time at next scr refresh
                PainAnchors.setAutoDraw(True)
            if PainAnchors.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > PainAnchors.tStartRefresh + ratingTime-frameTolerance:
                    # keep track of stop time/frame for later
                    PainAnchors.tStop = t  # not accounting for scr refresh
                    PainAnchors.frameNStop = frameN  # exact frame index
                    win.timeOnFlip(PainAnchors, 'tStopRefresh')  # time at next scr refresh
                    PainAnchors.setAutoDraw(False)

            # *PainPrompt* updates
            if PainPrompt.status == NOT_STARTED and t >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                PainPrompt.frameNStart = frameN  # exact frame index
                PainPrompt.tStart = t  # local t and not account for scr refresh
                PainPrompt.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(PainPrompt, 'tStartRefresh')  # time at next scr refresh
                PainPrompt.setAutoDraw(True)
            if PainPrompt.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > PainPrompt.tStartRefresh + ratingTime-frameTolerance:
                    # keep track of stop time/frame for later
                    PainPrompt.tStop = t  # not accounting for scr refresh
                    PainPrompt.frameNStop = frameN  # exact frame index
                    win.timeOnFlip(PainPrompt, 'tStopRefresh')  # time at next scr refresh
                    PainPrompt.setAutoDraw(False)

            # Autoresponder
            if t >= thisSimKey.rt and autorespond == 1:
                sliderValue = random.randint(-100,100)
                continueRoutine = False

            # check for quit (typically the Esc key)
            if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
                core.quit()
            
            # check if all components have finished
            if not continueRoutine:  # a component has requested a forced-end of Routine
                break
            continueRoutine = False  # will revert to True if at least one component still running
            for thisComponent in PainBinaryComponents:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished
            
            # refresh the screen
            if continueRoutine:
                win.flip()

        # -------Ending Routine "PainBinary"-------
        print("CueOff Channel " + str(pain_binary))
        for thisComponent in PainBinaryComponents:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        # store data for thisExp (ExperimentHandler)
        thisExp.addData('PainBinary.response', sliderValue)
        thisExp.addData('PainBinary.rt', timeNow-PainBinary.tStart)
        thisExp.nextEntry()
        thisExp.addData('PainBinary.started', PainBinary.tStart)
        thisExp.addData('PainBinary.stopped', PainBinary.tStop)
        painRating=sliderValue
        # bodyCalibration_bids_data.append(["Pain Binary:", sliderValue])

        bodyCalibration_bids_trial = []
        bodyCalibration_bids_trial.extend((onset, globalClock.getTime() - fmriStart - onset, None, painRating, bodySites[runs], currentTemp, 'Pain Rating', jitter2))
        bodyCalibration_bids.append(bodyCalibration_bids_trial)

        # Update Temperature if Pain Binary is -1
        if painRating<0 and currentTemp < maxTemp:
            currentTemp=currentTemp+.5

        # the Routine "PainBinary" was not non-slip safe, so reset the non-slip timer
        routineTimer.reset()

        if painRating < 0:
            ## Show nothing for 10 seconds
            win.flip()
            onset = globalClock.getTime() - fmriStart

            timer = core.CountdownTimer()
            if debug==1:
                timer.add(1)
            else:
                timer.add(10)
            while timer.getTime() > 0:
                continue
            
            bodyCalibration_bids_trial = []
            bodyCalibration_bids_trial.extend((onset, globalClock.getTime() - fmriStart - onset, None, None, bodySites[runs], currentTemp, 'No-Pain Interval', None))
            bodyCalibration_bids.append(bodyCalibration_bids_trial)

            bodyCalibration_total_trial =[]
            bodyCalibration_total_trial.extend((r+1, bodySites[runs], currentTemp, painRating, None, 1))
            bodyCalibration_bids_total.append(bodyCalibration_total_trial)
            
            routineTimer.reset()
        else:
            ## Otherwise show Intensity and Tolerance Ratings
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

            # -------Run Routine "IntensityRating"-------
            onset = globalClock.getTime() - fmriStart           # Record onset time of the trial
            while continueRoutine:
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
                            # abort routine on response
                            continueRoutine = False
                
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

            intensityRating=sliderValue
            bodyCalibration_bids_trial = []
            bodyCalibration_bids_trial.extend((onset, globalClock.getTime() - fmriStart - onset, None, intensityRating, bodySites[runs], currentTemp, 'Intensity Rating', None))
            bodyCalibration_bids.append(bodyCalibration_bids_trial)

            # the Routine "IntensityRating" was not non-slip safe, so reset the non-slip timer
            routineTimer.reset()

            ############ ASK TOLERANCE BINARY Question #######################################
            # ------Prepare to start Routine "ToleranceBinary"-------
            continueRoutine = True
            routineTimer.add(ratingTime)
            # update component parameters for each repeat
            # setup some python lists for storing info about the mouse
            
            ToleranceMouse = event.Mouse(win=win, visible=False) # Re-initialize ToleranceMouse
            ToleranceMouse.setPos((0,0))
            timeAtLastInterval = 0
            mouseX = 0
            oldMouseX = 0
            ToleranceBinary.width = 0
            ToleranceBinary.pos = (0,0)
            
            # keep track of which components have finished
            ToleranceBinaryComponents = [ToleranceMouse, ToleranceBinary, ToleranceAnchors, TolerancePrompt]
            for thisComponent in ToleranceBinaryComponents:
                thisComponent.tStart = None
                thisComponent.tStop = None
                thisComponent.tStartRefresh = None
                thisComponent.tStopRefresh = None
                if hasattr(thisComponent, 'status'):
                    thisComponent.status = NOT_STARTED
            # reset timers
            t = 0
            _timeToFirstFrame = win.getFutureFlipTime(clock="now")
            ToleranceBinaryClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
            frameN = -1

            # -------Run Routine "ToleranceBinary"-------
            onset = globalClock.getTime() - fmriStart           # Record onset time of the trial
            while continueRoutine:
                # get current time
                t = ToleranceBinaryClock.getTime()
                tThisFlip = win.getFutureFlipTime(clock=ToleranceBinaryClock)
                tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                # update/draw components on each frame

                timeNow = globalClock.getTime()
                if (timeNow - timeAtLastInterval) > TIME_INTERVAL:
                    mouseRel=ToleranceMouse.getRel()
                    mouseX=oldMouseX + mouseRel[0]

                if mouseX==0:
                    ToleranceBinary.width = 0
                else:
                    if mouseX>0:
                        ToleranceBinary.pos = (.28,0)
                        sliderValue = 1 
                    elif mouseX<0:
                        ToleranceBinary.pos = (-.4,0)
                        sliderValue = -1
                    ToleranceBinary.width = .5

                timeAtLastInterval = timeNow
                oldMouseX=mouseX

                # *ToleranceMouse* updates
                if ToleranceMouse.status == NOT_STARTED and t >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    ToleranceMouse.frameNStart = frameN  # exact frame index
                    ToleranceMouse.tStart = t  # local t and not account for scr refresh
                    ToleranceMouse.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(ToleranceMouse, 'tStartRefresh')  # time at next scr refresh
                    ToleranceMouse.status = STARTED
                    ToleranceMouse.mouseClock.reset()
                    prevButtonState = ToleranceMouse.getPressed()  # if button is down already this ISN'T a new click
                if ToleranceMouse.status == STARTED:  # only update if started and not finished!
                    if tThisFlipGlobal > ToleranceMouse.tStartRefresh + ratingTime-frameTolerance:
                        # keep track of stop time/frame for later
                        ToleranceMouse.tStop = t  # not accounting for scr refresh
                        ToleranceMouse.frameNStop = frameN  # exact frame index
                        ToleranceMouse.status = FINISHED
                    buttons = ToleranceMouse.getPressed()
                    if buttons != prevButtonState:  # button state changed?
                        prevButtonState = buttons
                        if sum(buttons) > 0:  # state changed to a new click
                            # abort routine on response
                            continueRoutine = False

                # *ToleranceBinary* updates
                if ToleranceBinary.status == NOT_STARTED and t >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    ToleranceBinary.frameNStart = frameN  # exact frame index
                    ToleranceBinary.tStart = t  # local t and not account for scr refresh
                    ToleranceBinary.tStartRefresh = tThisFlipGlobal  # on global time
                    win.callOnFlip(print, "Show Tolerance Binary")
                    if biopac_exists == 1:
                        win.callOnFlip(biopac.setData, biopac, 0)
                        win.callOnFlip(biopac.setData, biopac, tolerance_binary)
                    win.timeOnFlip(ToleranceBinary, 'tStartRefresh')  # time at next scr refresh
                    ToleranceBinary.setAutoDraw(True)
                if ToleranceBinary.status == STARTED:
                    # is it time to stop? (based on global clock, using actual start)
                    if tThisFlipGlobal > ToleranceBinary.tStartRefresh + ratingTime-frameTolerance:
                        # keep track of stop time/frame for later
                        ToleranceBinary.tStop = t  # not accounting for scr refresh
                        ToleranceBinary.frameNStop = frameN  # exact frame index
                        win.timeOnFlip(ToleranceBinary, 'tStopRefresh')  # time at next scr refresh
                        ToleranceBinary.setAutoDraw(False)
                
                # *ToleranceAnchors* updates
                if ToleranceAnchors.status == NOT_STARTED and t >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    ToleranceAnchors.frameNStart = frameN  # exact frame index
                    ToleranceAnchors.tStart = t  # local t and not account for scr refresh
                    ToleranceAnchors.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(ToleranceAnchors, 'tStartRefresh')  # time at next scr refresh
                    ToleranceAnchors.setAutoDraw(True)
                if ToleranceAnchors.status == STARTED:
                    # is it time to stop? (based on global clock, using actual start)
                    if tThisFlipGlobal > ToleranceAnchors.tStartRefresh + ratingTime-frameTolerance:
                        # keep track of stop time/frame for later
                        ToleranceAnchors.tStop = t  # not accounting for scr refresh
                        ToleranceAnchors.frameNStop = frameN  # exact frame index
                        win.timeOnFlip(ToleranceAnchors, 'tStopRefresh')  # time at next scr refresh
                        ToleranceAnchors.setAutoDraw(False)

                # *TolerancePrompt* updates
                if TolerancePrompt.status == NOT_STARTED and t >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    TolerancePrompt.frameNStart = frameN  # exact frame index
                    TolerancePrompt.tStart = t  # local t and not account for scr refresh
                    TolerancePrompt.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(TolerancePrompt, 'tStartRefresh')  # time at next scr refresh
                    TolerancePrompt.setAutoDraw(True)
                if TolerancePrompt.status == STARTED:
                    # is it time to stop? (based on global clock, using actual start)
                    if tThisFlipGlobal > TolerancePrompt.tStartRefresh + ratingTime-frameTolerance:
                        # keep track of stop time/frame for later
                        TolerancePrompt.tStop = t  # not accounting for scr refresh
                        TolerancePrompt.frameNStop = frameN  # exact frame index
                        win.timeOnFlip(TolerancePrompt, 'tStopRefresh')  # time at next scr refresh
                        TolerancePrompt.setAutoDraw(False)

                # Autoresponder
                if t >= thisSimKey.rt and autorespond == 1:
                    sliderValue = random.randint(-100,100)
                    continueRoutine = False

                # check for quit (typically the Esc key)
                if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
                    core.quit()
                
                # check if all components have finished
                if not continueRoutine:  # a component has requested a forced-end of Routine
                    break
                continueRoutine = False  # will revert to True if at least one component still running
                for thisComponent in ToleranceBinaryComponents:
                    if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                        continueRoutine = True
                        break  # at least one component has not yet finished
                
                # refresh the screen
                if continueRoutine:
                    win.flip()

            # -------Ending Routine "ToleranceBinary"-------
            print("CueOff Channel " + str(tolerance_binary))
            for thisComponent in ToleranceBinaryComponents:
                if hasattr(thisComponent, "setAutoDraw"):
                    thisComponent.setAutoDraw(False)
            # store data for thisExp (ExperimentHandler)
            thisExp.addData('ToleranceBinary.response', sliderValue)
            thisExp.addData('ToleranceBinary.rt', timeNow-ToleranceBinary.tStart)
            thisExp.nextEntry()
            thisExp.addData('ToleranceBinary.started', ToleranceBinary.tStart)
            thisExp.addData('ToleranceBinary.stopped', ToleranceBinary.tStop)

            toleranceRating=sliderValue

            bodyCalibration_bids_trial = []
            bodyCalibration_bids_trial.extend((onset, globalClock.getTime() - fmriStart - onset, None, toleranceRating, bodySites[runs], currentTemp, 'Tolerance Rating', None))
            bodyCalibration_bids.append(bodyCalibration_bids_trial)

            bodyCalibration_total_trial =[]
            bodyCalibration_total_trial.extend((r+1, bodySites[runs], currentTemp, painRating, intensityRating, toleranceRating))
            bodyCalibration_bids_total.append(bodyCalibration_total_trial)

            # Adjust temperature down if the temperature is not tolerable
            if toleranceRating<0 and currentTemp > minTemp:
                currentTemp=currentTemp-.5
                maxTemp = currentTemp
            if toleranceRating<0 and currentTemp == minTemp:
                # End the run.
                break

            # the Routine "ToleranceBinary" was not non-slip safe, so reset the non-slip timer
            routineTimer.reset()

            ########################## END SELF REPORT #######################################################

    """
    17. Save data into .TSV formats and Tying up Loose Ends
    """ 
    bodyCalibration_bids_data = pd.DataFrame(bodyCalibration_bids, columns = ['onset', 'duration', 'repetition', 'rating', 'bodySite', 'temperature', 'condition', 'pretrial-jitter'])
    bodyCalibration_bids_filename = sub_dir + os.sep + u'sub-SID%06d_ses-%02d_task-%s_acq-%s_run-%s_events.tsv' % (int(expInfo['DBIC Number']), int(expInfo['session']), expName, bodySites[runs].replace(" ", "").lower(), str(runs+1))
    bodyCalibration_bids_data.to_csv(bodyCalibration_bids_filename, sep="\t")

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
18. Saving data in BIDS
"""
bids_filename = sub_dir + os.sep + u'sub-SID%06d_task-%s.tsv' % (int(expInfo['DBIC Number']), expName)
bids_df=pd.DataFrame(pd.DataFrame(bodyCalibration_bids_total, columns = ['repetition', 'body_site', 'temperature', 'pain', 'intensity', 'tolerance']))
bids_df.to_csv(bids_filename, sep="\t")

averaged_filename = sub_dir + os.sep + u'sub-SID%06d_task-%s_participants.tsv' % (int(expInfo['DBIC Number']), expName)
averaged_data.extend([expInfo['date'], expInfo['DBIC Number'], calculate_age(expInfo['dob (mm/dd/yyyy)']), expInfo['dob (mm/dd/yyyy)'], expInfo['gender'], expInfo['handedness'], bodySites,
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

averaged_df = pd.DataFrame(data = [averaged_data], columns = ['date','DBIC_id','age','dob','gender','handedness','calibration_order',
                                                    'leftarm_ht','rightarm_ht','leftleg_ht','rightleg_ht','leftface_ht','rightface_ht','chest_ht','abdomen_ht',
                                                    'leftarm_i','rightarm_i','leftleg_i','rightleg_i','leftface_i','rightface_i','chest_i','abdomen_i'])
averaged_df.to_csv(averaged_filename, sep="\t")

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

# If there are no left face or right leg trials other than the first that are painful yet tolerable, then calibration has failed. 
if bids_df.loc[(bids_df['body_site']=='Left Face') & (bids_df['repetition']!=1) & (bids_df['pain']==1) & (bids_df['tolerance']==1)]['temperature'].count()==0:
    end_msg="Thank you for your participation. \n\n\nUnfortunately you don't qualify for the continuation of this study."

if bids_df.loc[(bids_df['body_site']=='Right Leg') & (bids_df['repetition']!=1) & (bids_df['pain']==1) & (bids_df['tolerance']==1)]['temperature'].count()==0:
    end_msg="Thank you for your participation. \n\n\nUnfortunately you don't qualify for the continuation of this study."

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