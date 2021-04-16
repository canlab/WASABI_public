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
biopac_exists = 0

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
task_ID=2
intro=46
rest_t1=47
nback_instructions=48
nback_fixation=49
nback_trial_start=50
in_between_run_msg=51
nback_hit=52
nback_miss=53
end=54

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

######################
# N-Back Task Components
######################
# Initialize components for Routine "NbackInstructions"
NbackInstructionsClock = core.Clock()
NbackInstructions = visual.TextStim(win=win, name='Nbackinstructions',
    text='In this task you will be required to click the left mouse button whenever the square appears in the same position as on the position \n\ntwo trials before. \n\nFor example if the square appeared in left down corner on trial 1, you should [click] if the square appears in the left down corner on trial 3. \nPress [click] to continue.',
    font='Arial',
    pos=(0, 0), units='height', height=0.05, 
    color='white', colorSpace='rgb', opacity=1)
NbackStart = keyboard.Keyboard()

# Initialize components for Routine "Fixation"
FixationClock = core.Clock()
fixation_2 = visual.TextStim(win=win, name='fixation_2',
    text='+',
    font='Arial',
    pos=(0, 0), height=0.05, wrapWidth=None, ori=0, 
    color='white', colorSpace='rgb', opacity=1, 
    languageStyle='LTR',
    depth=-2.0)
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
response_2 = keyboard.Keyboard()

# Create some handy timers
globalClock = core.Clock()  # to track the time since experiment started
routineTimer = core.CountdownTimer()  # to track time remaining of each (non-slip) routine 

if biopac_exists:
    biopac.setData(biopac, task_ID) # Start demarcation of the T1 task in Biopac Acqknowledge
    biopac.setData(biopac, 0) # Start demarcation of the T1 task in Biopac Acqknowledge

"""
6. Start Experimental Loops
"""
# set up handler to look after randomisation of conditions etc
# Counterbalance between even and odd subject numbers to ensure comparable group ns
if (int(expInfo['subject number']) % 2) != 0: 
    order = [OrderedDict([('RestT1', 1), ('TaskT1', 0)]),
            OrderedDict([('RestT1', 0), ('TaskT1', 1)])] 
    order_no = 1
    nback_bids_trial.append(order_no)
else:
    order = [OrderedDict([('RestT1', 0), ('TaskT1', 1)]),
            OrderedDict([('RestT1', 1), ('TaskT1', 0)])]
    order_no = 2
    nback_bids_trial.append(order_no)
counterbalancer = data.TrialHandler(nReps=1, method='sequential', 
    extraInfo=expInfo, originPath=-1,
    trialList=order,
    seed=None, name='counterbalancer')
thisExp.addLoop(counterbalancer)  # add the loop to the experiment
thisCounterbalancer = counterbalancer.trialList[0]  # so we can initialise stimuli with some values
# abbreviate parameter names if possible (e.g. rgb = thisCounterbalancer.rgb)
if thisCounterbalancer != None:
    for paramName in thisCounterbalancer:
        exec('{} = thisCounterbalancer[paramName]'.format(paramName))

for thisCounterbalancer in counterbalancer:
    currentLoop = counterbalancer
    # abbreviate parameter names if possible (e.g. rgb = thisCounterbalancer.rgb)
    if thisCounterbalancer != None:
        for paramName in thisCounterbalancer:
            exec('{} = thisCounterbalancer[paramName]'.format(paramName))
    """ 
    7. Rest T1 Phase
    """
    start = visual.TextStim(win, text=start_msg, height=.05, color=win.rgb + 0.5)
    start.draw()  # Automatically draw every frame
    win.flip()
    if autorespond != 1:
        # Trigger
        event.waitKeys(keyList = 's') # experimenter start key - safe key before fMRI trigger

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
        
        # ------Prepare to start Routine "RestT1"-------
        continueRoutine = True
        routineTimer.add(258)
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
                if tThisFlipGlobal > fixation_1.tStartRefresh + 258-frameTolerance:
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
        
        """
        6. End of Run, Wait for Experimenter instructions to begin next run
        """   
        message = visual.TextStim(win, text=in_between_run_msg, height=0.05, units='height')
        message.draw()
        win.callOnFlip(print, "Awaiting Experimenter to start next run...\nPress [e] to continue.")
        win.flip()
        # Autoresponder
        if autorespond != 1:
            event.waitKeys(keyList = 'e')
    # completed RestT1 repeats of 'RestT1Loop'
    """ 
    7. Task T1 Phase
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
       
        """ 
        7i. N-back Working Memory Induction Introduction
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
        7ii. Working Memory N-Back Fixation Cross
        """
        start = visual.TextStim(win, text=start_msg, height=.05, color=win.rgb + 0.5)
        start.draw()  # Automatically draw every frame
        win.flip()
        if autorespond != 1:
            # Trigger
            event.waitKeys(keyList = 's') # experimenter start key - safe key before fMRI trigger

        # ------Prepare to start Routine "Fixation"-------
        continueRoutine = True
        routineTimer.add(1.000000)
        # update component parameters for each repeat
        # keep track of which components have finished
        FixationComponents = [fixation_2]
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
            
            # *fixation_2* updates
            if fixation_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                fixation_2.frameNStart = frameN  # exact frame index
                fixation_2.tStart = t  # local t and not account for scr refresh
                fixation_2.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(fixation_2, 'tStartRefresh')  # time at next scr refresh
                if biopac_exists:
                    win.callOnFlip(biopac.setData, biopac, nback_fixation)
                fixation_2.setAutoDraw(True)
            if fixation_2.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > fixation_2.tStartRefresh + 1.0-frameTolerance:
                    # keep track of stop time/frame for later
                    fixation_2.tStop = t  # not accounting for scr refresh
                    fixation_2.frameNStop = frameN  # exact frame index
                    win.timeOnFlip(fixation_2, 'tStopRefresh')  # time at next scr refresh
                    fixation_2.setAutoDraw(False)
            
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
            biopac.setData(biopac, 0)
        for thisComponent in FixationComponents:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        thisExp.addData('fixation_2.started', fixation_2.tStartRefresh)
        thisExp.addData('fixation_2.stopped', fixation_2.tStopRefresh)

        # set up handler to look after randomisation of conditions etc
        Nback2 = os.sep.join([_thisDir,"N-back-2.xlsx"])
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
        7iii. Working Memory N-Back Main Loop
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
            response_2.keys = []
            response_2.rt = []
            _response_2_allKeys = []
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
                
                # *grid_lines_2* updates
                if grid_lines_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    grid_lines_2.frameNStart = frameN  # exact frame index
                    grid_lines_2.tStart = t  # local t and not account for scr refresh
                    grid_lines_2.tStartRefresh = tThisFlipGlobal  # on global time
                    if biopac_exists:
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
                
                # *response_2* updates
                waitOnFlip = False
                if response_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    response_2.frameNStart = frameN  # exact frame index
                    response_2.tStart = t  # local t and not account for scr refresh
                    response_2.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(response_2, 'tStartRefresh')  # time at next scr refresh
                    response_2.status = STARTED
                    # keyboard checking is just starting
                    waitOnFlip = True
                    win.callOnFlip(response_2.clock.reset)  # t=0 on next screen flip
                    win.callOnFlip(response_2.clearEvents, eventType='keyboard')  # clear events on next screen flip
                if response_2.status == STARTED:
                    # is it time to stop? (based on global clock, using actual start)
                    if tThisFlipGlobal > response_2.tStartRefresh + 2-frameTolerance:
                        # keep track of stop time/frame for later
                        response_2.tStop = t  # not accounting for scr refresh
                        response_2.frameNStop = frameN  # exact frame index
                        win.timeOnFlip(response_2, 'tStopRefresh')  # time at next scr refresh
                        response_2.status = FINISHED
                if response_2.status == STARTED and not waitOnFlip:
                    theseKeys = response_2.getKeys(keyList=['space'], waitRelease=False)
                    _response_2_allKeys.extend(theseKeys)
                    if len(_response_2_allKeys):
                        response_2.keys = _response_2_allKeys[-1].name  # just the last key pressed
                        response_2.rt = _response_2_allKeys[-1].rt
                        # was this correct?
                        if (response_2.keys == str(corrAns)) or (response_2.keys == corrAns):
                            response_2.corr = 1
                            if biopac_exists:
                                biopac.setData(biopac, nback_hit)
                        else:
                            response_2.corr = 0
                            if biopac_exists:
                                biopac.setData(biopac, nback_miss)
                
                # Autoresponder
                if t >= thisSimKey.rt and autorespond == 1:
                    _response_2_allKeys.extend([thisSimKey])

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
            trials_2.addData('grid_lines_2.started', grid_lines_2.tStartRefresh)
            trials_2.addData('grid_lines_2.stopped', grid_lines_2.tStopRefresh)
            trials_2.addData('target_square_2.started', target_square_2.tStartRefresh)
            trials_2.addData('target_square_2.stopped', target_square_2.tStopRefresh)
            trials_2.addData('fixation_3.started', fixation_3.tStartRefresh)
            trials_2.addData('fixation_3.stopped', fixation_3.tStopRefresh)
            # check responses
            if response_2.keys in ['', [], None]:  # No response was made
                response_2.keys = None
                # was no response the correct answer?!
                if str(corrAns).lower() == 'none':
                    response_2.corr = 1;  # correct non-response
                else:
                    response_2.corr = 0;  # failed to respond (incorrectly)
            # store data for trials_2 (TrialHandler)
            trials_2.addData('response_2.keys',response_2.keys)
            trials_2.addData('response_2.corr', response_2.corr)
            if response_2.keys != None:  # we had a response
                trials_2.addData('response_2.rt', response_2.rt)
            trials_2.addData('response_2.started', response_2.tStartRefresh)
            trials_2.addData('response_2.stopped', response_2.tStopRefresh)
            nback_bids_trial = []
            nback_bids_trial.extend((order_no, grid_lines_2.tStartRefresh, 2, response_2.rt, response_2.corr))
            nback_bids.append(nback_bids_trial)

            thisExp.nextEntry()
            
        # completed 1 repeats of 'trials_2' 

        """
        8. End of Run, Wait for Experimenter instructions to begin next run
        """   
        message = visual.TextStim(win, text=in_between_run_msg, height=0.05, units='height')
        message.draw()
        win.callOnFlip(print, "Awaiting Experimenter to start next run...\nPress [e] to continue")
        if biopac_exists:
            win.callOnFlip(biopac.setData, biopac,in_between_run_msg)
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
    biopac.setData(biopac,end)
    biopac.setData(biopac,0)
nback_bids_data = pd.DataFrame(nback_bids, columns = ['order', 'onset', 'duration', 'rt', 'correct'])

sub_dir = os.path.join(_thisDir, 'data', 'sub-%05d' % (int(expInfo['subject number'])), 'ses-%02d' % (int(expInfo['session'])))
if not os.path.exists(sub_dir):
    os.makedirs(sub_dir)
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