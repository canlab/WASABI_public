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

No data for analysis is written, although timestamps are recorded in Biopac Acqknowledge for psychophysiological analysis.

0a. Import Libraries
"""

from __future__ import absolute_import, division

from psychopy import locale_setup
from psychopy import prefs
from psychopy import sound, gui, visual, core, data, event, logging, clock
# Troubleshooting Tips:
# If you get window-related errors, make sure to downgrade pyglet to 1.4.1:
# pip uninstall pyglet
# pip install pyglet==1.4.1
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

T1_time = 258      # should be 258 seconds

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
rest_t1=47

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
"""
2. Start Experimental Dialog Boxes
"""
# Upload participant file: Browse for file
# Store info about the experiment session
psychopyVersion = '2020.2.10'
expName = 'WASABI Nback'  # from the Builder filename that created this script
if debug == 1:
    expInfo = {
    'subject number': '1', 
    'gender': 'm',
    'session': '1',
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

dlg = gui.DlgFromDict(title="WASABI Task-T1 Test", dictionary=expInfo, sortKeys=False) 
if dlg.OK == False:
    core.quit()  # user pressed cancel
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
psypy_filename = _thisDir + os.sep + u'data/%05d_%s_%s' % (int(expInfo['subject number']), expName, expInfo['date'])

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

"""
5. Initialize Trial-level Components
"""
# General Instructional Text
start_msg = 'Please wait. \nThe scan will begin shortly. \n Experimenter press [s] to continue.'
# in_between_run_msg = 'Thank you.\n Please wait for the next scan to start \n Experimenter press [e] to continue.'
end_msg = 'Thank you for your participation'

# create a default keyboard (e.g. to check for escape)
defaultKeyboard = keyboard.Keyboard()
######################
# Rest T1 Components
######################
# Initialize components for Routine "RestT1"
RestT1Clock = core.Clock()
# fix_cross = visual.TextStim(win = win, text = '+', color = [1,1,1], height = 0.3)
fixation_1 = visual.TextStim(win=win, name='fixation_2',
    text='+',
    font='Arial',
    pos=(0, 0), height=0.05, wrapWidth=None, ori=0, 
    color='white', colorSpace='rgb', opacity=1, 
    languageStyle='LTR',
    depth=-2.0)

# Create some handy timers
globalClock = core.Clock()  # to track the time since experiment started
routineTimer = core.CountdownTimer()  # to track time remaining of each (non-slip) routine 

if biopac_exists:
    biopac.setData(biopac, task_ID) # Start demarcation of the T1 task in Biopac Acqknowledge
    biopac.setData(biopac, 0) # Start demarcation of the T1 task in Biopac Acqknowledge

win.mouseVisible = False

""" 
7. Rest T1 Phase
"""
# set up handler to look after randomisation of conditions etc
RestT1Loop = data.TrialHandler(nReps=RestT1, method='random', 
    extraInfo=expInfo, originPath=-1,
    trialList=[None],
    seed=None, name='RestT1Loop')
thisExp.addLoop(RestT1Loop)  # add the loop to the experiment
thisRestT1Loop = RestT1Loop.trialList[0]  # so we can initialise stimuli with some values
# abbreviate parameter names if possible (e.g. rgb = thisRestT1Loop.rgb)
if thisRestT1Loop != None:
    for paramName in thisRestT1Loop:
        exec('{} = thisRestT1Loop[paramName]'.format(paramName))

for thisRestT1Loop in RestT1Loop:
    currentLoop = RestT1Loop
    # abbreviate parameter names if possible (e.g. rgb = thisRestT1Loop.rgb)
    if thisRestT1Loop != None:
        for paramName in thisRestT1Loop:
            exec('{} = thisRestT1Loop[paramName]'.format(paramName))
    
    start = visual.TextStim(win, text=start_msg, height=.05, color=win.rgb + 0.5)
    start.draw()  # Automatically draw every frame
    win.flip()
    if autorespond != 1:
        # Trigger
        event.waitKeys(keyList = 's') # experimenter start key - safe key before fMRI trigger
    routineTimer.reset()

    # ------Prepare to start Routine "RestT1"-------
    continueRoutine = True
    routineTimer.add(T1_time)
    # update component parameters for each repeat
    # keep track of which components have finished
    RestT1Components = [fixation_1]
    for thisComponent in RestT1Components:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    RestT1Clock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    frameN = -1
    
    # -------Run Routine "RestT1"-------
    while continueRoutine and routineTimer.getTime() > 0:
        # get current time
        t = RestT1Clock.getTime()
        tThisFlip = win.getFutureFlipTime(clock=RestT1Clock)
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
                win.callOnFlip(biopac.setData, biopac, rest_t1)
            fixation_1.setAutoDraw(True)
        if fixation_1.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > fixation_1.tStartRefresh + T1_time-frameTolerance:
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
        for thisComponent in RestT1Components:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # -------Ending Routine "RestT1"-------
    if biopac_exists:
        biopac.setData(biopac, 0)
    for thisComponent in RestT1Components:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    RestT1Loop.addData('fixation_1.started', fixation_1.tStartRefresh)
    RestT1Loop.addData('fixation_1.stopped', fixation_1.tStopRefresh)
    thisExp.nextEntry()

# completed RestT1 repeats of 'RestT1Loop'

"""
9. Save data into Excel and .CSV formats and Tying up Loose Ends
""" 
# these shouldn't be strictly necessary (should auto-save)
thisExp.saveAsWideText(psypy_filename+'.csv', delim='auto')
thisExp.saveAsPickle(psypy_filename)
logging.flush()
# make sure everything is closed down
message = visual.TextStim(win, text=end_msg, height=0.05, units='height')
message.draw()
win.flip()
if biopac_exists == 1:
    biopac.close()  # Close the labjack U3 device to end communication with the Biopac MP150
core.wait(5)
thisExp.abort()  # or data files will save again on exit
win.close()  # close the window
core.quit()

"""
End of Experiment
"""