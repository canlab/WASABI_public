# -*- coding: utf-8 -*-
"""
This experim
ent was initialized using PsychoPy3 Experiment Builder (v2020.2.5),
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

The paradigm will generate 3x of these files of name:
sub-XXXX_task-movemap_run-XX_events.tsv

40 rows of trials per file will be defined by the following headers:
onset   duration  condition

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
#     For instance, the following code would send a value of 15 by setting the first 4 bits to “1": biopac.setData(biopac, 15)
#     Toggling each of the FIO 8 channels directly: biopac.setFIOState(fioNum = 0:7, state=1)

# biopac channels EDIT
task_ID=6
task_start=7

run_start=9

movemapping_intro=155
movement_instruction=156

leftface_cue=157
rightface_cue=158
leftarm_cue=159
rightarm_cue=160
leftleg_cue=161
rightleg_cue=162
chest_cue=163
abdomen_cue=164

leftface_move=165
rightface_move=166
leftarm_move=167
rightarm_move=168
leftleg_move=169
rightleg_move=170
chest_move=171
abdomen_move=172

rest=173
between_run_msg = 174
end=175

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

"""
1. Experimental Parameters
Clocks, paths, etc.
"""
# Clocks
globalClock = core.Clock()              # to track the time since experiment started
routineTimer = core.CountdownTimer()    # to track time remaining of each (non-slip) routine 

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
psychopyVersion = '2020.2.5'
expInfo = {
'subject number': '', 
'gender': '',
'session': '',
'handedness': '', 
'scanner': ''
}

if debug==1:
    expInfo = {
        'subject number': '999', 
        'gender': 'm',
        'session': '99',
        'handedness': 'r', 
        'scanner': 'TEST'
    }

else:
    dlg = gui.DlgFromDict(title="WASABI Movement-Map Scan", dictionary=expInfo, sortKeys=False)
    if dlg.OK == False:
        core.quit()  # user pressed cancel

expInfo['date'] = data.getDateStr()  # add a simple timestamp
expInfo['psychopyVersion'] = psychopyVersion
expName = 'movemap'
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
4. Prepare Experimental Dictionaries for Body-Site Cues
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
                          "Abdomen": os.sep.join([stimuli_dir,"cue","Abdomen.png"]),
                          "Rest": None
                        }
bodysite_word2cuecode = {"Left Face": leftface_cue, 
                        "Right Face": rightface_cue, 
                        "Left Arm": leftarm_cue, 
                        "Right Arm": rightarm_cue, 
                        "Left Leg": leftleg_cue, 
                        "Right Leg": rightleg_cue, 
                        "Chest": chest_cue,
                        "Abdomen": abdomen_cue
                        }
bodysite_word2movecode = {"Left Face": leftface_move, 
                        "Right Face": rightface_move, 
                        "Left Arm": leftarm_move, 
                        "Right Arm": rightarm_move, 
                        "Left Leg": leftleg_move, 
                        "Right Leg": rightleg_move, 
                        "Chest": chest_move,
                        "Abdomen": abdomen_move 
                        }

"""
5. Stratified Randomization for Conditions in Each Run
    2 Repetitions of each body-site movement and 8 trials of rest per run
    Rest trials should not be back to back, and should occur every 1 - 3 movement trials.
"""
nruns = 3

bodySites = ["Left Face", "Right Face", "Left Arm", "Right Arm", "Left Leg", "Right Leg", "Chest", "Abdomen"]
restArray = ["Rest","Rest","Rest","Rest"]

def generate_run_order(siteList, restList):
    conditions = []
    siteList1 = siteList.copy()
    siteList2 = siteList.copy()
    restList1 = restList.copy()
    restList2 = restList.copy()
    random.shuffle(siteList1)
    random.shuffle(siteList2)
    while siteList1:
        for i in range(random.randint(1,3)):
            conditions.append(siteList1.pop())
            if not siteList1:
                break
        if restList1:
            conditions.append(restList1.pop())
    while siteList2:
        for i in range(random.randint(1,3)):
            conditions.append(siteList2.pop())
            if not siteList2:
                break
        if restList2:
            conditions.append(restList2.pop())
    return conditions

runList = []
for run in range(nruns):
    runList.append(generate_run_order(bodySites, restArray))

expInfo['runList'] = str(runList)

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
in_between_run_msg = 'Thank you.\n Please wait for the next run to start. \n Experimenter press [e] to continue.'
end_msg = 'This is the end of the experiment. \nPlease wait for instructions from the experimenter'

cueTime = 1.5
moveTrialTime = 16.5
trialTime = cueTime + moveTrialTime # 18 seconds
restTime = trialTime # 18 seconds

if debug == 1:
    cueTime = 1
    moveTrialTime = 1
    trialTime = 2
    restTime = 2

#############
# Movement Mapping Components
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

# Initialize components for Routine "MovementInstruction"
MovementInstructionClock = core.Clock()
MovementInstructionRead = keyboard.Keyboard()
# Create experimenter instructions
MovementInstructionText = visual.TextStim(win, name='MovementInstructionText', 
    text="During this scan, you will occasionally see picture cues of a body part. Without moving your head, move only that body part in the way that you were instructed earlier once per second: \n\nLeft and Right Cheek Raises\nLeft and Right Forearm Flexes\nLeft and Right Calf Flexes\nChest Puff Expansions\nAbdomen Squeezes\n\nKeep moving while the fixation cross is green and stop moving when it is red.\n\nExperimenter press [space] to continue.",
    font = 'Arial',
    pos=(0, 0), height=0.06, wrapWidth=1.5, ori=0,      # Edit wrapWidth for the 1920 full screen
    color='white', colorSpace='rgb', opacity=1, 
    languageStyle='LTR',
    depth=0.0, 
    anchorHoriz='center')
MovementInstructionText.size=(1,1)

# Initialize components for Routine "MovementTrial"
# 9 Conditions: "Left Face", "Right Face", "Left Arm", "Right Arm", "Left Leg", "Right Leg", "Chest", "Abdomen", "Rest"
MovementTrialClock = core.Clock()
image_shortinstr = "Move the designated body part when the cross is green, and stop when the cross turns red."
MovementTrialText = visual.TextStim(win, name='MovementTrialText', 
    text=image_shortinstr,
    font = 'Arial',
    pos=(0, -0.3), height=0.05, wrapWidth=None, ori=0, 
    color='white', colorSpace='rgb', opacity=1, 
    languageStyle='LTR',
    depth=0.0,
    anchorHoriz='center')
BodySiteCue = visual.ImageStim(
    win=win,
    name='BodySiteCue', 
    mask=None,
    ori=0, pos=(0, 0), size=(300, 300), units="pix",
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=512, interpolate=True, depth=0.0)
fix_cross = visual.TextStim(win = win, text = '+', color = [1,1,1], height = 0.3, anchorHoriz='center')

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
8. Start Experimental Loop
"""
# Start demarcation of the movemap task in Biopac Acqknowledge
if biopac_exists:
    biopac.setData(biopac, 0)     
    biopac.setData(biopac, task_ID) 
"""
8a. Movement Mapping Introduction
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
        win.callOnFlip(print, "Cueing Biopac Channel: " + str(movemapping_intro))
        if biopac_exists == 1:
            win.callOnFlip(biopac.setData, biopac, 0)
            win.callOnFlip(biopac.setData, biopac, movemapping_intro)
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
print("CueOff Channel: " + str(movemapping_intro))
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

"""
8c. Undergo the imagination instruction with the participant on the first run
"""
# ------Prepare to start Routine "MovementInstruction"-------
# Initialize trial stimuli
###########################################################################################
continueRoutine = True

# update component parameters for each repeat
MovementInstructionRead.keys = []
MovementInstructionRead.rt = []
_MovementInstructionRead_allKeys = []

# keep track of which components have finished
MovementInstructionComponents = [MovementInstructionText, MovementInstructionRead]
for thisComponent in MovementInstructionComponents:
    thisComponent.tStart = None
    thisComponent.tStop = None
    thisComponent.tStartRefresh = None
    thisComponent.tStopRefresh = None
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED
# reset timers
t = 0
_timeToFirstFrame = win.getFutureFlipTime(clock="now")
MovementInstructionClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
frameN = -1

# -------Run Routine "MovementInstruction"-------
while continueRoutine:
    # get current time
    t = MovementInstructionClock.getTime()
    tThisFlip = win.getFutureFlipTime(clock=MovementInstructionClock)
    tThisFlipGlobal = win.getFutureFlipTime(clock=None)
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame
    
    # *MovementInstructionText* updates
    if MovementInstructionText.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        # keep track of start time/frame for later
        MovementInstructionText.frameNStart = frameN  # exact frame index
        MovementInstructionText.tStart = t  # local t and not account for scr refresh
        MovementInstructionText.tStartRefresh = tThisFlipGlobal  # on global time
        win.timeOnFlip(MovementInstructionText, 'tStartRefresh')  # time at next scr refresh
        MovementInstructionText.setAutoDraw(True)
    
    # *MovementInstructionRead* updates
    waitOnFlip = False
    if MovementInstructionRead.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        # keep track of start time/frame for later
        MovementInstructionRead.frameNStart = frameN  # exact frame index
        MovementInstructionRead.tStart = t  # local t and not account for scr refresh
        MovementInstructionRead.tStartRefresh = tThisFlipGlobal  # on global time
        win.timeOnFlip(MovementInstructionRead, 'tStartRefresh')  # time at next scr refresh
        MovementInstructionRead.status = STARTED
        # keyboard checking is just starting
        waitOnFlip = True
        win.callOnFlip(print, "Showing Movement Instructions")
        win.callOnFlip(print, "Cue Biopac " + str(movement_instruction))
        if biopac_exists == 1:
            win.callOnFlip(biopac.setData, biopac, 0)
            win.callOnFlip(biopac.setData, biopac, movement_instruction)
        win.callOnFlip(MovementInstructionRead.clock.reset)  # t=0 on next screen flip
        win.callOnFlip(MovementInstructionRead.clearEvents, eventType='keyboard')  # clear events on next screen flip
    if MovementInstructionRead.status == STARTED and not waitOnFlip:
        theseKeys = MovementInstructionRead.getKeys(keyList=['space'], waitRelease=False)
        _MovementInstructionRead_allKeys.extend(theseKeys)
        if len(_MovementInstructionRead_allKeys):
            MovementInstructionRead.keys = _MovementInstructionRead_allKeys[-1].name  # just the last key pressed
            MovementInstructionRead.rt = _MovementInstructionRead_allKeys[-1].rt
            # a response ends the routine
            print("Starting mainloop")
            continueRoutine = False

    # Autoresponder
    if t >= thisSimKey.rt and autorespond == 1:
        _MovementInstructionRead_allKeys.extend([thisSimKey]) 

    # check for quit (typically the Esc key)
    if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
        core.quit()
    
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in MovementInstructionComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()
# -------Ending Routine "MovementInstruction"-------
# print("Cueing Biopac Channel " + str(task_start))
for thisComponent in MovementInstructionComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)
thisExp.addData('MovementInstructionText.started', MovementInstructionText.tStartRefresh)
# check responses
if MovementInstructionRead.keys in ['', [], None]:  # No response was made
    MovementInstructionRead.keys = None
thisExp.addData('MovementInstructionRead.keys',MovementInstructionRead.keys)
if MovementInstructionRead.keys != None:  # we had a response
    thisExp.addData('MovementInstructionRead.rt', MovementInstructionRead.rt)
thisExp.addData('MovementInstructionRead.started', MovementInstructionRead.tStartRefresh)
thisExp.addData('MovementInstructionRead.stopped', MovementInstructionRead.tStopRefresh)
# the Routine "MovementInstruction" was not non-slip safe, so reset the non-slip timer
routineTimer.reset()

"""
8d. Begin a run of 40 trials. 
    8 Conditions
    Trial Makeup:
    Cue - Green Fixation (movement) - Red Fixation (rest)
"""
for run in range(len(runList)):
    """
    8e. Prepare the scanner trigger, set clock(s), and wait for dummy scans
    """
    ###############################################################################################
    # Experimenter fMRI Start Instruction ____________________________________________________
    ###############################################################################################
    start = visual.TextStim(win, text=start_msg, height=.05, color=win.rgb + 0.5)
    start.draw()  # Automatically draw every frame
    win.flip()
    fmriStart = globalClock.getTime()

    if autorespond != 1:
        # Trigger
        event.waitKeys(keyList = 's') # experimenter start key - safe key before fMRI trigger
        event.waitKeys(keyList='5')   # fMRI trigger
        fmriStart = globalClock.getTime()
        TR = 0.46
        core.wait(TR*6)         # Wait 6 TRs, Dummy Scans

    print("Starting run " + str(run+1))
    print("Cue Biopac Channel " + str(run_start))
    if biopac_exists == 1:
        biopac.setData(biopac, 0)
        biopac.setData(biopac, run_start)
    routineTimer.reset()
    # Start a new BIDS data collection array for each run
    movemap_bids_data = []
    movemapOrder = []

    for thisTrial in runList[run]:
        movemapOrder.append(thisTrial)  # Append the current trial type to movemapOrder

        if thisTrial != "Rest":
            print("Starting Movement Trial")
            BodySiteCue.image = bodysite_word2img[thisTrial]
            BodySiteCue.pos = (0,0)
            if thisTrial == "Left Face":
                MovementTrialText.text="Begin raising your left cheek."
            if thisTrial == "Right Face":
                MovementTrialText.text="Begin raising your right cheek."
            if thisTrial == "Left Arm":
                MovementTrialText.text="Begin flexing your left forearm." 
            if thisTrial == "Right Arm":
                MovementTrialText.text="Begin flexing your right forearm."
            if thisTrial == "Left Leg":
                MovementTrialText.text="Begin flexing your left calf."
            if thisTrial == "Right Leg":
                MovementTrialText.text="Begin flexing your right calf."
            if thisTrial == "Chest":
                MovementTrialText.text="Begin puffing then relaxing your chest."
            if thisTrial == "Abdomen":
                MovementTrialText.text="Begin squeezing then relaxing your abdomen."
            BiopacCueChannel = bodysite_word2cuecode[thisTrial]
            BiopacMoveChannel = bodysite_word2movecode[thisTrial]
            fix_cross.color = "green"
            conditionData = thisTrial

            # ------Prepare to start Routine "MovementTrial"-------
            continueRoutine = True
            routineTimer.reset()
            routineTimer.add(trialTime)
            # update component parameters for each repeat
            # keep track of which components have finished
            MovementTrialComponents = [MovementTrialText, BodySiteCue, fix_cross]
            for thisComponent in MovementTrialComponents:
                thisComponent.tStart = None
                thisComponent.tStop = None
                thisComponent.tStartRefresh = None
                thisComponent.tStopRefresh = None
                if hasattr(thisComponent, 'status'):
                    thisComponent.status = NOT_STARTED
            # reset timers
            t = 0
            _timeToFirstFrame = win.getFutureFlipTime(clock="now")
            MovementTrialClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
            frameN = -1
            # -------Run Routine "MovementTrial"-------
            onset = globalClock.getTime() - fmriStart
            while continueRoutine and routineTimer.getTime() > 0:
                # get current time
                t = MovementTrialClock.getTime()
                tThisFlip = win.getFutureFlipTime(clock=MovementTrialClock)
                tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                # update/draw components on each frame
            
                # *BodySiteCue* updates  
                if BodySiteCue.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    BodySiteCue.frameNStart = frameN  # exact frame index
                    BodySiteCue.tStart = t  # local t and not account for scr refresh
                    BodySiteCue.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(BodySiteCue, 'tStartRefresh')  # time at next scr refresh
                    win.callOnFlip(print, "Starting cue phase for", thisTrial)
                    if biopac_exists == 1:
                        win.callOnFlip(biopac.setData, biopac, 0)
                        win.callOnFlip(biopac.setData, biopac, BiopacCueChannel)
                    BodySiteCue.setAutoDraw(True)
                if BodySiteCue.status == STARTED:
                    # is it time to stop? (based on global clock, using actual start)
                    if tThisFlipGlobal > BodySiteCue.tStartRefresh + cueTime-frameTolerance:
                        # keep track of stop time/frame for later
                        BodySiteCue.tStop = t  # not accounting for scr refresh
                        BodySiteCue.frameNStop = frameN  # exact frame index
                        win.timeOnFlip(BodySiteCue, 'tStopRefresh')  # time at next scr refresh
                        BodySiteCue.setAutoDraw(False)

                # *MovementTrialText* updates
                if MovementTrialText.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    MovementTrialText.frameNStart = frameN  # exact frame index
                    MovementTrialText.tStart = t  # local t and not account for scr refresh
                    MovementTrialText.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(MovementTrialText, 'tStartRefresh')  # time at next scr refresh
                    MovementTrialText.setAutoDraw(True)
                if MovementTrialText.status == STARTED:
                        # is it time to stop? (based on global clock, using actual start)
                    if tThisFlipGlobal > MovementTrialText.tStartRefresh + cueTime-frameTolerance:
                        # keep track of stop time/frame for later
                        MovementTrialText.tStop = t  # not accounting for scr refresh
                        MovementTrialText.frameNStop = frameN  # exact frame index
                        win.timeOnFlip(MovementTrialText, 'tStopRefresh')  # time at next scr refresh
                        MovementTrialText.setAutoDraw(False)
                
                # *fix_cross* updates
                if fix_cross.status == NOT_STARTED and tThisFlip >= cueTime-frameTolerance:
                    # keep track of start time/frame for later
                    fix_cross.frameNStart = frameN  # exact frame index
                    fix_cross.tStart = t  # local t and not account for scr refresh
                    fix_cross.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(fix_cross, 'tStartRefresh')  # time at next scr refresh
                    win.callOnFlip(print, "Starting movement phase for", thisTrial)
                    if biopac_exists == 1:
                        win.callOnFlip(biopac.setData, biopac, 0)
                        win.callOnFlip(biopac.setData, biopac, BiopacMoveChannel)
                    fix_cross.setAutoDraw(True)
                if fix_cross.status == STARTED:
                    if tThisFlipGlobal > fix_cross.tStartRefresh + moveTrialTime-frameTolerance:
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
                for thisComponent in MovementTrialComponents:
                    if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                        continueRoutine = True
                        break  # at least one component has not yet finished
                # refresh the screen
                if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                    win.flip()

            # -------Ending Routine "MovementTrial"-------
            for thisComponent in MovementTrialComponents:
                if hasattr(thisComponent, "setAutoDraw"):
                    thisComponent.setAutoDraw(False)
            thisExp.addData('BodySiteCue.started', BodySiteCue.tStartRefresh)
            thisExp.addData('BodySiteCue.stopped', BodySiteCue.tStopRefresh)
            thisExp.addData('fix_cross.started', fix_cross.tStartRefresh)
            thisExp.addData('fix_cross.stopped', fix_cross.tStopRefresh)
            cue_duration = fix_cross.tStartRefresh-BodySiteCue.tStartRefresh
            trial_duration = t - cue_duration
            movemap_trial = []
            movemap_trial.extend((onset, cue_duration, "cue", conditionData))
            movemap_bids_data.append(movemap_trial)
            movemap_trial = []
            movemap_trial.extend((onset+cue_duration, trial_duration, "movement", conditionData))
            movemap_bids_data.append(movemap_trial)
            routineTimer.reset()
        else:
            print("Starting Rest Trial")
            fix_cross.color = "red"
            conditionData = thisTrial

            # ------Prepare to start Routine "RestTrial"-------
            continueRoutine = True
            routineTimer.reset()
            routineTimer.add(trialTime)
            # update component parameters for each repeat
            # keep track of which components have finished
            MovementTrialComponents = [fix_cross]
            for thisComponent in MovementTrialComponents:
                thisComponent.tStart = None
                thisComponent.tStop = None
                thisComponent.tStartRefresh = None
                thisComponent.tStopRefresh = None
                if hasattr(thisComponent, 'status'):
                    thisComponent.status = NOT_STARTED
            # reset timers
            t = 0
            _timeToFirstFrame = win.getFutureFlipTime(clock="now")
            MovementTrialClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
            frameN = -1
            # -------Run Routine "RestTrial"-------
            onset = globalClock.getTime() - fmriStart
            while continueRoutine and routineTimer.getTime() > 0:
                # get current time
                t = MovementTrialClock.getTime()
                tThisFlip = win.getFutureFlipTime(clock=MovementTrialClock)
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
                    win.callOnFlip(print, "Starting", thisTrial)
                    if biopac_exists == 1:
                        win.callOnFlip(biopac.setData, biopac, 0)
                        win.callOnFlip(biopac.setData, biopac, rest)
                    fix_cross.setAutoDraw(True)
                if fix_cross.status == STARTED:
                    if tThisFlipGlobal > fix_cross.tStartRefresh + trialTime-frameTolerance:
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
                for thisComponent in MovementTrialComponents:
                    if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                        continueRoutine = True
                        break  # at least one component has not yet finished
                # refresh the screen
                if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                    win.flip()

            # -------Ending Routine "RestTrial"-------
            for thisComponent in MovementTrialComponents:
                if hasattr(thisComponent, "setAutoDraw"):
                    thisComponent.setAutoDraw(False)
            thisExp.addData('fix_cross.started', fix_cross.tStartRefresh)
            thisExp.addData('fix_cross.stopped', fix_cross.tStopRefresh)
            movemap_trial = []
            movemap_trial.extend((onset, t, "rest", conditionData))
            movemap_bids_data.append(movemap_trial)
            routineTimer.reset()

        # completed 24 repeats of 'thisTrial'
    """
    9. Save Run File
    """
    # file_savename = os.sep.join([main_dir, 'data', session_info['session_id'], 'practice.csv'])
    # Data file name stem = absolute path + name; later add .psyexp, .csv, .log, etc
    # each _%s refers to the respective field in the parentheses
    ## This needs to be at the end of the run
    movemap_bids_data.append(["Condition Order: ", movemapOrder])
    bids_run_filename = sub_dir + os.sep + u'sub-%05d_ses-%02d_task-%s_run-%s_events.tsv' % (int(expInfo['subject number']), int(expInfo['session']), expName, str(run+1))
    movemap_bids_data = pd.DataFrame(movemap_bids_data, columns = ['onset','duration','phase','condition'])
    movemap_bids_data.to_csv(bids_run_filename, sep="\t")

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