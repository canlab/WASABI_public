# -*- coding: utf-8 -*-
"""
This experiment was initialized using PsychoPy3 Experiment Builder (v2020.2.5),
    on November 10, 2020, at 15:04
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
missing values are coded None or -99 (i.e., body_site for rest trials).

The paradigm will generate 8x of these files of name:
sub-XXXX_task-bodymap_acq-bodysite_run-XX_events.tsv

Trials per file are defined by the following headers:
onset   duration    trial_type  body_site   temp

after every stimulation there will be rows for:
[] "Was that painful?"
[] "How intense was the heat stimulation?" (Bartoshuk gLMS)
[] "Was it tolerable or was that too much?"

The design is as follows:
1. Start with a 47.5 degree stimulation trial (to be thrown away)
2. If tolerable, select subsequent temperatures randomized from a set of 3 temperatures [45, 46.5, 48] unless the first trial was marked as intolerable, then [45, 46, 47]
3. If a trial is marked as untolerable, update the stimulation to max at .5 degrees less than that temperature. 

Conditions: High, Medium, Low

0a. Import Libraries
"""
from __future__ import absolute_import, division

# Psychopy's __init__.py auto-generated commands for Windows are buggy. Quotations and slashes are not well formatted going from Unix-style to Windows. Check this.
from psychopy import locale_setup, prefs, logging, clock  
from psychopy import sound  # Note: You may have to delete 'sounddevice' from the Psychopy audio library in your preferences to avoid a sound-related error message
from psychopy import event
from psychopy import data
from psychopy import core
from psychopy import visual  # ensure python image library "pillow" is installed, or reinstall it. pip uninstall pillow; pip install pillow
from psychopy import gui     # ensure PyQt5 is installed. pip install pyqt5
# but make sure to install specific version, otherwise clashes with other libraries
# https://github.com/CorentinJ/Real-Time-Voice-Cloning/issues/109

# Troubleshooting Tips:
# If you get window-related errors, make sure to downgrade pyglet to 1.4.1:
# pip uninstall pyglet
# pip install pyglet==1.4.1
# If you get text uncentered problems, downgrade to pyglet 1.3.2
# pip install pyglet==1.3.2

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
import timeit

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
thermode_exists = 1

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
0c. Prepare Devices: Biopac Psychophysiological Acquisition and Medoc Thermode
"""
# Biopac parameters _________________________________________________
# Relevant Biopac commands: 
#     To send a Biopac marker code to Acqknowledge, replace the FIO number with a value between 0-255(dec), or an 8-bit word(bin) 
#     For instance, the following code would send a value of 15 by setting the first 4 bits to “1": biopac.setData(biopac, 15)
#     Toggling each of the FIO 8 channels directly: biopac.setFIOState(fioNum = 0:7, state=1)

# biopac channels EDIT
task_ID=1
task_start=7

run_start=9

bodymapping_intro=14
bodymapping_instruction=15
imagination_instruction=16

leftface_hi=17
rightface_hi=18
leftarm_hi=19
rightarm_hi=20
leftleg_hi=21
rightleg_hi=22
chest_hi=23
abdomen_hi=24

leftface_med=17
rightface_med=18
leftarm_med=19
rightarm_med=20
leftleg_med=21
rightleg_med=22
chest_med=23
abdomen_med=24

leftface_lo=17
rightface_lo=18
leftarm_lo=19
rightarm_lo=20
leftleg_lo=21
rightleg_lo=22
chest_lo=23
abdomen_lo=24

rest=41
pain_binary=42
intensity_rating=43
tolerance_binary=44

between_run_msg=45
end=46

if biopac_exists == 1:
    # Initialize LabJack U3 Device, which is connected to the Biopac MP150 psychophysiological amplifier data acquisition device
    # This involves importing the labjack U3 Parallelport to USB library
    # U3 Troubleshooting:
    # Check to see if u3 was imported correctly with: help('u3')
    # Check to see if u3 is calibrated correctly with: cal_data = biopac.getCalibrationData()
    # Check to see the data at the FIO, EIO, and CIO ports
    # Make sure UD Driver (on Windows) or Exodriver (MacOSX or Linux) is installed: win.winHandle.set_visible(False) # Make the mainscreen invisible so that the dialog boxes appear
    # Make sure LabjackPython is installed: pip install LabJackPython; If need to install to a specific version of python, use the -m flag e.g., C:\ProgramData\Anaconda3\python.exe -m pip install LabJackPython
    # If you get an SSL module error, on Windows you need to install Windows OpenSSL: https://slproweb.com/products/Win32OpenSSL.html
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
    biopac.setData(biopac, byte=0)

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
globalClock = core.Clock()              # to track the time since experiment started
routineTimer = core.CountdownTimer()    # to track time remaining of each (non-slip) routine
# fmriClock = core.Clock() 

# Paths
# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)
main_dir = _thisDir
stimuli_dir = main_dir + os.sep + "stimuli"
# Brings up the Calibration/Data folder to load the appropriate calibration data right away.
calibration_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir, os.path.pardir, 'Calibration', 'data')

"""
2. Start Experimental Dialog Boxes
"""

# Upload participant file: Browse for file
psychopyVersion = '2020.2.5'
expInfo = {
'subject number': '', 
'gender': '',
'session': '',
'handedness': '', 
'scanner': ''
}

# Load the subject's calibration file and ensure that it is valid
if debug==1:
    expInfo = {
        'subject number': '999', 
        'gender': 'm',
        'session': '99',
        'handedness': 'r', 
        'scanner': 'TEST'
    }
else:
    dlg1 = gui.DlgFromDict(title="WASABI BodyCalibration Scan", dictionary=expInfo, sortKeys=False) 
    if dlg1.OK == False:
        core.quit()  # user pressed cancel

expInfo['date'] = data.getDateStr()  # add a simple timestamp
expInfo['psychopyVersion'] = psychopyVersion
expName='bodyCalibration'
expInfo['expName'] = expName

""" 
3. Setup the Window
DBIC uses a Panasonic DW750 Projector with a native resolution of 1920x1200 (16:10), but it is configured at 1920x1080 (16:9) at DBIC
Configure a black window with a 16:9 aspect ratio during development (1280x720) and production (1920x1080)
fullscr = False for testing, True for running participants
"""
if debug == 1:
    win = visual.Window(
    size=[1280, 720], fullscr=False, 
    screen=0,   # Change this to the appropriate display 
    winType='pyglet', allowGUI=True, allowStencil=True,
    monitor='testMonitor', color=[-1.000,-1.000,-1.000], colorSpace='rgb',
    blendMode='avg', useFBO=True, 
    units='height')
else:
    win = visual.Window(
    size=[1920, 1080], fullscr=True, 
    screen=4,   # Change this to the appropriate fMRI projector 
    winType='pyglet', allowGUI=True, allowStencil=True,
    monitor='testMonitor', color=[-1.000,-1.000,-1.000], colorSpace='rgb',
    blendMode='avg', useFBO=True, 
    units='height')

# store frame rate of monitor if we can measure it
expInfo['frameRate'] = win.getActualFrameRate()
if expInfo['frameRate'] != None:
    frameDur = 1.0 / round(expInfo['frameRate'])
else:
    frameDur = 1.0 / 60.0  # could not measure, so guess

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
5. Create Body-Site arrays for each run for this participant
"""
bodySites = ["Left Face", "Right Face", "Left Arm", "Right Arm", "Left Leg", "Right Leg", "Chest", "Abdomen"]
random.shuffle(bodySites)
expInfo['body_site_order'] = str(bodySites)

"""
6. Prepare files to write
"""
sub_dir = os.path.join(_thisDir, 'data', 'sub-%05d' % (int(expInfo['subject number'])), 'ses-%02d' % (int(expInfo['session'])))
if not os.path.exists(sub_dir):
    os.makedirs(sub_dir)
psypy_filename = sub_dir + os.sep + u'sub-%05d_ses-%02d_task-%s_%s' % (int(expInfo['subject number']), int(expInfo['session']), expName, expInfo['date'])

# An ExperimentHandler isn't essential but helps with data saving
thisExp = data.ExperimentHandler(name=expName, version='1.0.0',
    extraInfo=expInfo, runtimeInfo=None,
    savePickle=True, saveWideText=True,
    dataFileName=psypy_filename)
# save a log file for detail verbose info
logFile = logging.LogFile(psypy_filename+'.log', level=logging.ERROR)
logging.console.setLevel(logging.WARNING)  # this outputs to the screen, not a file
endExpNow = False  # flag for 'escape' or other condition => quit the exp
frameTolerance = 0.001  # how close to onset before 'same' frame

"""
7. Initialize Trial-level Components
"""
# General Instructional Text
start_msg = 'Please wait. \nThe scan will begin shortly. \n Experimenter press [s] to continue.'
in_between_run_msg = 'Thank you.\n Please wait for the next scan to start. \n Experimenter press [e] to continue.'
end_msg = 'This is the end of this scan. \nPlease wait for instructions from the experimenter'

stimtrialTime = 20 # This becomes very unreliable with the use of poll_for_change().
poststimTime = 5 # Ensure that nonstimtrialTime - poststimTime is at least 5 or 6 seconds.

if debug == 1:
    stimtrialTime = 1 # This becomes very unreliable with the use of poll_for_change().
    poststimTime = 1 # Ensure that nonstimtrialTime - poststimTime is at least 5 or 6 seconds.

#############
# Body Mapping Components
#############
# Initialize components for Routine "Introduction"
IntroductionClock = core.Clock()
Begin = visual.TextStim(win=win, name='Begin',
    text='Thank you. \nPlease wait for the experimenter to press [Space].',
    font='Arial',
    pos=(0, 0), height=0.1, wrapWidth=None, ori=0, 
    color='white', colorSpace='rgb', opacity=1, 
    languageStyle='LTR',
    depth=0.0, 
    anchorHoriz='center')
BeginTask = keyboard.Keyboard()
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

# Initialize components for Routine "StimTrial"
# Three Conditions: High, Medium, Low
StimTrialClock = core.Clock()
fix_cross = visual.TextStim(win = win, text = '+', color = [1,1,1], height = 0.3, anchorHoriz='center')

# Initialize components for each Rating
ratingTime = 10 # Rating Time limit in seconds
TIME_INTERVAL = 0.005   # Speed at which slider ratings udpate
ratingScaleWidth=1.5
ratingScaleHeight=.4
sliderMin = -.75
sliderMax = .75

painText="Was that painful?"
intensityText="How intense was the heat stimulation?"
tolerableText="Was it tolerable or was that too much heat?"

black_triangle_verts = [(sliderMin, .2),    # left point
                        (sliderMax, .2),    # right point
                        (0, -.2)]           # bottom-point

## EDIT THE BOTTOM COMPONENTS:
# Initialize components for Routine "PainBinary"
PainBinaryClock = core.Clock()
PainBinary = visual.Rect(win, height=ratingScaleHeight, width=0, pos= [0, 0], fillColor='red', lineColor='black')
PainBlackTriangle = visual.ShapeStim(win, vertices=black_triangle_verts, fillColor='black', lineColor='black')
PainMouse = event.Mouse(win=win)
PainMouse.mouseClock = core.Clock()
PainAnchors = visual.ImageStim(
    win=win,
    image= os.sep.join([stimuli_dir,"ratingscale","PainScale.png"]),
    name='PainQuestion', 
    mask=None,
    ori=0, pos=(0, -.09), size=(1.5, .4),
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
ToleranceBlackTriangle = visual.ShapeStim(win, vertices=black_triangle_verts, fillColor='black', lineColor='black')
ToleranceMouse = event.Mouse(win=win)
ToleranceMouse.mouseClock = core.Clock()
ToleranceAnchors = visual.ImageStim(
    win=win,
    image= os.sep.join([stimuli_dir,"ratingscale","ToleranceScale.png"]),
    name='ToleranceQuestion', 
    mask=None,
    ori=0, pos=(0, -.09), size=(1.5, .4),
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

# Initialize components for Routine "End"
EndClock = core.Clock()
EndingText = visual.TextStim(win=win, name='EndingText',
    text='Thank you for your participation. Please press [Space] to end the task.',
    font='Arial',
    pos=(0, 0), height=0.1, wrapWidth=None, ori=0, 
    color='white', colorSpace='rgb', opacity=1, 
    languageStyle='LTR',
    depth=0.0,
    anchorHoriz='center')
ConfirmEnd = keyboard.Keyboard()

# create a default keyboard (e.g. to check for escape)
defaultKeyboard = keyboard.Keyboard()
# Turn the mouse cursor off during the duration of the scan
win.mouseVisible = False
"""
8. Start Experimental Loops: 
"""
# Start demarcation of the bodymap task in Biopac Acqknowledge
if biopac_exists:
    biopac.setData(biopac, 0)     
    biopac.setData(biopac, task_ID) 
"""
8a. Body Mapping Introduction
"""
# ------Prepare to start Routine "Introduction"-------
continueRoutine = True
# update component parameters for each repeat
BeginTask.keys = []
BeginTask.rt = []
_BeginTask_allKeys = []
# keep track of which components have finished
IntroductionComponents = [Begin, BeginTask]
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

# -------Run Routine "Introduction"-------
while continueRoutine:
    # get current time
    t = IntroductionClock.getTime()
    tThisFlip = win.getFutureFlipTime(clock=IntroductionClock)
    tThisFlipGlobal = win.getFutureFlipTime(clock=None)
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame
    
    # *Begin* updates
    if Begin.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        # keep track of start time/frame for later
        Begin.frameNStart = frameN  # exact frame index
        Begin.tStart = t  # local t and not account for scr refresh
        Begin.tStartRefresh = tThisFlipGlobal  # on global time
        win.timeOnFlip(Begin, 'tStartRefresh')  # time at next scr refresh
        Begin.setAutoDraw(True)
    
    # *BeginTask* updates
    waitOnFlip = False
    if BeginTask.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        # keep track of start time/frame for later
        BeginTask.frameNStart = frameN  # exact frame index
        BeginTask.tStart = t  # local t and not account for scr refresh
        BeginTask.tStartRefresh = tThisFlipGlobal  # on global time
        win.timeOnFlip(BeginTask, 'tStartRefresh')  # time at next scr refresh
        BeginTask.status = STARTED
        # keyboard checking is just starting
        waitOnFlip = True
        win.callOnFlip(print, "Starting Introduction")
        win.callOnFlip(print, "Cueing Biopac Channel: " + str(bodymapping_intro))
        if biopac_exists == 1:
            win.callOnFlip(biopac.setData, biopac, 0)
            win.callOnFlip(biopac.setData, biopac, bodymapping_intro)
        win.callOnFlip(BeginTask.clock.reset)  # t=0 on next screen flip
        win.callOnFlip(BeginTask.clearEvents, eventType='keyboard')  # clear events on next screen flip
    if BeginTask.status == STARTED and not waitOnFlip:
        theseKeys = BeginTask.getKeys(keyList=['space'], waitRelease=False)
        _BeginTask_allKeys.extend(theseKeys)
        if len(_BeginTask_allKeys):
            BeginTask.keys = _BeginTask_allKeys[-1].name  # just the last key pressed
            BeginTask.rt = _BeginTask_allKeys[-1].rt
            # a response ends the routine
            continueRoutine = False
    
    # Autoresponder
    if t >= thisSimKey.rt and autorespond == 1:
        _BeginTask_allKeys.extend([thisSimKey])  

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
print("CueOff Channel: " + str(bodymapping_intro))
for thisComponent in IntroductionComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)
thisExp.addData('Begin.started', Begin.tStartRefresh)
thisExp.addData('Begin.stopped', Begin.tStopRefresh)
# check responses
if BeginTask.keys in ['', [], None]:  # No response was made
    BeginTask.keys = None
thisExp.addData('BeginTask.keys',BeginTask.keys)
if BeginTask.keys != None:  # we had a response
    thisExp.addData('BeginTask.rt', BeginTask.rt)
thisExp.addData('BeginTask.started', BeginTask.tStartRefresh)
thisExp.addData('BeginTask.stopped', BeginTask.tStopRefresh)
thisExp.nextEntry()
# the Routine "Introduction" was not non-slip safe, so reset the non-slip timer
routineTimer.reset()

"""
8b. Main Run Loop
"""
# if int(expInfo['subject number']) % 2 == 0: subjectOrder = os.sep.join([stimuli_dir,"EvenOrders.xlsx"]) 
# else: subjectOrder = subjectOrder = os.sep.join([stimuli_dir,"OddOrders.xlsx"])
# ##
runLoop = data.TrialHandler(nReps=1, method='random', extraInfo=expInfo, originPath=-1, trialList=data.importConditions(subjectOrder, selection='0:8'), seed=None, name='runLoop')
# ##
thisExp.addLoop(runLoop)  # add the loop to the experiment
thisrunLoop = runLoop.trialList[0]  # so we can initialise stimuli with some values

# abbreviate parameter names if possible (e.g. rgb = thisrunLoop.rgb)
if thisrunLoop != None:
    for paramName in thisrunLoop:
        exec('{} = thisrunLoop[paramName]'.format(paramName))

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
    8d. Begin the run of XX trials. 
        3 Conditions (trial_type)
        Stimulation
            1. Hi heat applied to bodysite
            2. Med heat applied to body-site
            3. Low heat applied to body-site
    """

    # set up handler to look after randomisation of conditions etc
    trials = data.TrialHandler(nReps=1, method='sequential', extraInfo=expInfo, originPath=-1, trialList=runLoop.trialList[runLoop.thisTrialN]['runSeq'], seed=None, name='trials')
    thisExp.addLoop(trials)  # add the loop to the experiment
    thisTrial = trials.trialList[0]  # so we can initialise stimuli with some values
    # abbreviate parameter names if possible (e.g. rgb = thisTrial.rgb)

    # hot = thermode1_temp2program[participant_settingsHeat[bodySites[runLoop.thisTrialN]]]
    # warm = thermode1_temp2program[participant_settingsWarm[bodySites[runLoop.thisTrialN]]]
    """
    8e. Prepare condition array, the scanner trigger, set clock(s), and wait for dummy scans
    """
    ###############################################################################################
    # Experimenter fMRI Start Instruction ____________________________________________________
    ###############################################################################################
    start = visual.TextStim(win, text=start_msg, height=.05, color=win.rgb + 0.5)
    start.draw()  # Automatically draw every frame

    # Experimenter: Check to make sure the program is loaded if the first trial is a heat stimulation trial 
    # if thisTrial['trial_type'] == 1:
    #     print("Loading Medoc Stimulation Program ", str(thisTrial['trial_type']))
    #     thermodeCommand = thermode1_temp2program[participant_settingsHeat[bodySites[runLoop.thisTrialN]]]
    #     tp_selected = 1
    #     if thermode_exists == 1 & tp_selected ==1:
    #         win.callOnFlip(sendCommand, 'select_tp', thermodeCommand)
    # if thisTrial['trial_type'] == 2:
    #     print("Loading Medoc Stimulation Program ", str(thisTrial['trial_type']))
    #     thermodeCommand = thermode1_temp2program[participant_settingsWarm[bodySites[runLoop.thisTrialN]]]
    #     tp_selected = 1
    #     if thermode_exists == 1 & tp_selected ==1:
    #         win.callOnFlip(sendCommand, 'select_tp', thermodeCommand)

    print("Loading Medoc Stimulation Program ", str(thisTrial['trial_type']))
    currentTemp=47.5 # First stimulation will always be 47.5 degrees Celsius.
    thermodeCommand = thermode1_temp2program[currentTemp]      
    tp_selected = 1
    if thermode_exists == 1 & tp_selected ==1:
        win.callOnFlip(sendCommand, 'select_tp', thermodeCommand)

    win.flip()
    tp_selected = 0
    fmriStart = globalClock.getTime()
    
    if autorespond != 1:
        # Trigger
        event.waitKeys(keyList = 's') # experimenter start key - safe key before fMRI trigger
        event.waitKeys(keyList='5')   # fMRI trigger
        fmriStart = globalClock.getTime()
        TR = 0.46
        core.wait(TR*6)         # Wait 6 TRs, Dummy Scans

    print("Starting run " + str(runLoop.thisTrialN+1))
    print("Cue Biopac Channel " + str(run_start))
    if biopac_exists == 1:
        biopac.setData(biopac, 0)
        biopac.setData(biopac, run_start)
    routineTimer.reset()

    if thisTrial != None:
        for paramName in thisTrial:
            exec('{} = thisTrial[paramName]'.format(paramName))  
    for thisTrial in trials:
        currentLoop = trials
        # abbreviate parameter names if possible (e.g. rgb = thisTrial.rgb)
        if thisTrial != None:
            for paramName in thisTrial:
                exec('{} = thisTrial[paramName]'.format(paramName))

        # Setup the next trial if it is a thermal stimulation condition    
        next_trial = trials.getFutureTrial()
        if (trials.nRemaining > 0):
            print("Loading Program")
            print("Loading Thermal Program for Heat to", bodySites[runLoop.thisTrialN])
            thermodeCommand = thermode1_temp2program[calibrationTemp]
            tp_selected = 1

        ## Thermal Stimulation Trials:        
            startTime = timeit.default_timer()
            BiopacChannel = bodysite_word2heatcode[bodySites[runLoop.thisTrialN]]
            bodySiteData = bodySites[runLoop.thisTrialN]
            temperature = calibrationTemp
            thermodeCommand = hot

            # ------Prepare to start Routine "StimTrial"-------
            continueRoutine = True
            routineTimer.reset()
            routineTimer.add(stimtrialTime)
            # update component parameters for each repeat
            # keep track of which components have finished
            StimTrialComponents = [fix_cross]
            for thisComponent in StimTrialComponents:
                thisComponent.tStart = None
                thisComponent.tStop = None
                thisComponent.tStartRefresh = None
                thisComponent.tStopRefresh = None
                if hasattr(thisComponent, 'status'):
                    thisComponent.status = NOT_STARTED
            # reset timers
            t = 0
            _timeToFirstFrame = win.getFutureFlipTime(clock="now")
            StimTrialClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
            frameN = -1
            # -------Run Routine "StimTrial"-------
            onset = globalClock.getTime() - fmriStart   
            while continueRoutine and routineTimer.getTime() > 0:
                # get current time
                t = StimTrialClock.getTime()
                tThisFlip = win.getFutureFlipTime(clock=StimTrialClock)
                tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                # update/draw components on each frame

                # *fix_cross* updates
                if fix_cross.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    fix_cross.frameNStart = frameN  # exact frame index
                    fix_cross.tStart = t  # local t and not account for scr refresh
                    fix_cross.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(fix_cross, 'tStartRefresh')  # time at next scr refresh
                    win.callOnFlip(print, "Starting Heat Stimulation to the", bodySites[runLoop.thisTrialN])
                    if thermode_exists == 1:
                        win.callOnFlip(sendCommand, 'trigger')
                    win.callOnFlip(print, "Cue Biopac channel " + str(BiopacChannel))
                    if biopac_exists == 1:
                        win.callOnFlip(biopac.setData, biopac, 0)
                        win.callOnFlip(biopac.setData, biopac, BiopacChannel)
                    fix_cross.setAutoDraw(True)
                if fix_cross.status == STARTED:
                    if thermode_exists == 1 and tp_selected == 1 and trial_type ==4 and tThisFlipGlobal > fix_cross.tStartRefresh + poststimTime-frameTolerance:
                        sendCommand('select_tp', thermodeCommand)
                        tp_selected = 0  
                    # is it time to stop? (based on global clock, using actual start)
                    if tThisFlipGlobal > fix_cross.tStartRefresh + stimtrialTime-frameTolerance:
                        # keep track of stop time/frame for later
                        fix_cross.tStop = t  # not accounting for scr refresh
                        fix_cross.frameNStop = frameN  # exact frame index
                        win.timeOnFlip(fix_cross, 'tStopRefresh')  # time at next scr refresh
                        fix_cross.setAutoDraw(False)
                
                # check for quit (typically the Esc key)
                if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
                    core.quit()
                
                # check if all components have finished
                if not continueRoutine:  # a component has requested a forced-end of Routine
                    break
                continueRoutine = False  # will revert to True if at least one component still running
                for thisComponent in StimTrialComponents:
                    if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                        continueRoutine = True
                        break  # at least one component has not yet finished
                # refresh the screen
                if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                    win.flip()

            # -------Ending Routine "StimTrial"-------
            for thisComponent in StimTrialComponents:
                if hasattr(thisComponent, "setAutoDraw"):
                    thisComponent.setAutoDraw(False)
            trials.addData('fix_cross.started', fix_cross.tStartRefresh)
            trials.addData('fix_cross.stopped', fix_cross.tStopRefresh)
            # duration = timeit.default_timer()-startTime # Consider comparing with TTLs output.
            bodymap_trial = []
            # bodymap_trial.extend((fix_cross.tStartRefresh - fmriStart, t, trial_type, bodySiteData, temperature))
            bodymap_trial.extend((onset, t, trial_type, bodySiteData, temperature))
            bodymap_bids_data.append(bodymap_trial)
            routineTimer.reset()

            # completed 42 repeats of 'trials'
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
        PainBinaryComponents = [PainMouse, PainBinary, PainBlackTriangle, PainAnchors, PainPrompt]
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
            PainBinary.pos = (mouseX/2,0)
            PainBinary.width = abs(mouseX)

            # Binarize response:
            if mouseX > 0:
                mouseX = sliderMax
            if mouseX < 0:
                mouseX = sliderMin

            timeAtLastInterval = timeNow
            oldMouseX=mouseX

            sliderValue = mouseX/sliderMax  

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
                    win.callOnFlip(biopac.setData, biopac, Pain_rating)
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
            
            # *PainBlackTriangle* updates
            if PainBlackTriangle.status == NOT_STARTED and t >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                PainBlackTriangle.frameNStart = frameN  # exact frame index
                PainBlackTriangle.tStart = t  # local t and not account for scr refresh
                PainBlackTriangle.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(PainBlackTriangle, 'tStartRefresh')  # time at next scr refresh
                PainBlackTriangle.setAutoDraw(True)
            if PainBlackTriangle.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > PainBlackTriangle.tStartRefresh + ratingTime-frameTolerance:
                    # keep track of stop time/frame for later
                    PainBlackTriangle.tStop = t  # not accounting for scr refresh
                    PainBlackTriangle.frameNStop = frameN  # exact frame index
                    win.timeOnFlip(PainBlackTriangle, 'tStopRefresh')  # time at next scr refresh
                    PainBlackTriangle.setAutoDraw(False)

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
        bodymap_bids_data.append(["Pain Binary:", sliderValue])

        # Update Temperature if 

        # the Routine "PainBinary" was not non-slip safe, so reset the non-slip timer
        routineTimer.reset()

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
        bodymap_bids_data.append(["Intensity Rating:", sliderValue])
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
        ToleranceBinaryComponents = [ToleranceMouse, ToleranceBinary, ToleranceBlackTriangle, ToleranceAnchors, TolerancePrompt]
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
            ToleranceBinary.pos = (mouseX/2,0)
            ToleranceBinary.width = abs(mouseX)

            # Binarize response:
            if mouseX > 0:
                mouseX = sliderMax
            if mouseX < 0:
                mouseX = sliderMin
            sliderValue = mouseX/sliderMax  

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
                    win.callOnFlip(biopac.setData, biopac, Tolerance_Binary)
                win.timeOnFlip(ToleranceBinary, 'tStartRefresh')  # time at next scr refresh
                ToleranceBinary.setAutoDraw(True)
            if ToleranceBinary.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > ToleranceBinary.tStartRefresh + BinaryTime-frameTolerance:
                    # keep track of stop time/frame for later
                    ToleranceBinary.tStop = t  # not accounting for scr refresh
                    ToleranceBinary.frameNStop = frameN  # exact frame index
                    win.timeOnFlip(ToleranceBinary, 'tStopRefresh')  # time at next scr refresh
                    ToleranceBinary.setAutoDraw(False)
            
            # *ToleranceBlackTriangle* updates
            if ToleranceBlackTriangle.status == NOT_STARTED and t >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                ToleranceBlackTriangle.frameNStart = frameN  # exact frame index
                ToleranceBlackTriangle.tStart = t  # local t and not account for scr refresh
                ToleranceBlackTriangle.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(ToleranceBlackTriangle, 'tStartRefresh')  # time at next scr refresh
                ToleranceBlackTriangle.setAutoDraw(True)
            if ToleranceBlackTriangle.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > ToleranceBlackTriangle.tStartRefresh + ratingTime-frameTolerance:
                    # keep track of stop time/frame for later
                    ToleranceBlackTriangle.tStop = t  # not accounting for scr refresh
                    ToleranceBlackTriangle.frameNStop = frameN  # exact frame index
                    win.timeOnFlip(ToleranceBlackTriangle, 'tStopRefresh')  # time at next scr refresh
                    ToleranceBlackTriangle.setAutoDraw(False)

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
        # bodymap_bids_data.append(["Pain Binary:", sliderValue])
        bodymap_bids_data.append(["Tolerable:", sliderValue])

        # the Routine "PainBinary" was not non-slip safe, so reset the non-slip timer
        routineTimer.reset()


        ########################## END SELF REPORT #######################################################
    """
    9. Save Run File
    """
    # file_savename = os.sep.join([main_dir, 'data', session_info['session_id'], 'practice.csv'])
    # Data file name stem = absolute path + name; later add .psyexp, .csv, .log, etc
    # each _%s refers to the respective field in the parentheses
    ## This needs to be at the end of the run
    bids_run_filename = sub_dir + os.sep + u'sub-%05d_ses-%02d_task-%s_acq-%s_run-%s_events.tsv' % (int(expInfo['subject number']), int(expInfo['session']), expName, bodySites[runLoop.thisTrialN].replace(" ", "").lower(), str(runLoop.thisTrialN+1))
    bodymap_bids_data = pd.DataFrame(bodymap_bids_data, columns = ['onset','duration','trial_type','body_site','temp'])
    bodymap_bids_data.to_csv(bids_run_filename, sep="\t")

    """
    10. End of Run, Wait for Experimenter instructions to begin next run
    """   
    message = visual.TextStim(win, text=in_between_run_msg, height=0.05, anchorHoriz='center')
    message.draw()
    win.callOnFlip(print, "Awaiting Experimenter to start next run...")
    if biopac_exists == 1:
        win.callOnFlip(biopac.setData, biopac, 0)
        win.callOnFlip(biopac.setData, biopac, between_run_msg)
    win.flip()
    # Autoresponder
    if autorespond != 1:
        event.waitKeys(keyList = 'e')
    routineTimer.reset()
"""
11. Thanking the Participant
"""   
# ------Prepare to start Routine "End"-------
continueRoutine = True
# update component parameters for each repeat
ConfirmEnd.keys = []
ConfirmEnd.rt = []
_ConfirmEnd_allKeys = []
# keep track of which components have finished
EndComponents = [EndingText, ConfirmEnd]
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
        win.callOnFlip(print, "Thanking the participant")
        if biopac_exists == 1:
            win.callOnFlip(biopac.setData, biopac, 0)
            win.callOnFlip(biopac.setData, biopac, end)
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
    
    # Autoresponder
    if t >= thisSimKey.rt and autorespond == 1:
        _ConfirmEnd_allKeys.extend([thisSimKey])

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
print("Biopac CueOff " + str(end))
for thisComponent in EndComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)
thisExp.addData('EndingText.started', EndingText.tStartRefresh)
thisExp.addData('EndingText.stopped', EndingText.tStopRefresh)
# check responses
if ConfirmEnd.keys in ['', [], None]:  # No response was made
    ConfirmEnd.keys = None
thisExp.addData('ConfirmEnd.keys',ConfirmEnd.keys)
if ConfirmEnd.keys != None:  # we had a response
    thisExp.addData('ConfirmEnd.rt', ConfirmEnd.rt)
thisExp.addData('ConfirmEnd.started', ConfirmEnd.tStartRefresh)
thisExp.addData('ConfirmEnd.stopped', ConfirmEnd.tStopRefresh)
thisExp.nextEntry()
# the Routine "End" was not non-slip safe, so reset the non-slip timer
routineTimer.reset()

# Flip one final time so any remaining win.callOnFlip() 
# and win.timeOnFlip() tasks get executed before quitting
win.flip()
####################################################################################
###END###
#####################################################################################
"""
9. Save data into Excel and .CSV formats and Tying up Loose Ends
""" 
# these shouldn't be strictly necessary (should auto-save)
thisExp.saveAsWideText(psypy_filename+'.csv', delim='auto')
thisExp.saveAsPickle(psypy_filename)
logging.flush()
# make sure everything is closed down
message = visual.TextStim(win, text=end_msg, anchorHoriz='center')
message.draw()
if biopac_exists == 1:
    biopac.close()  # Close the labjack U3 device to end communication with the Biopac MP150
thisExp.abort()  # or data files will save again on exit
win.close()  # close the window
core.quit()
"""
End of Experiment
"""