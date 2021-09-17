


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
sub-XX_task-Nback_run-X_events.tsv

42x trials per file with the following

headers:
onset   duration    trial_type  body_site
3124
Troubleshooting Tips:
If you get window-related errors, make sure to downgrade pyglet to 1.4.1:
pip uninstall pyglet
pip install pyglet==1.4.1

0a. Import Libraries
"""

from __future__ import absolute_import, division

from psychopy import locale_setup
from psychopy import prefs
prefs.hardware['audioLib'] = ['PTB']
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

# For Autoresponding:
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
task_ID=4
hyperalignment_intro = 212
kungfury=213
inscapes=214
resting_state=215
between_run_msg=45

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
    biopac.setData(biopac, byte=0)

"""
1. Experimental Parameters
Paths, etc.
"""
# Paths
# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)
main_dir = _thisDir
stimuli_dir = main_dir + os.sep + "stimuli"
video_dir = main_dir + os.sep + "stimuli" + os.sep + "videos"

"""
2. Start Experimental Dialog Boxes
"""
# Upload participant file: Browse for file
# Store info about the experiment session
psychopyVersion = '2020.2.10'
expName = 'Hyperalignment'  # from the Builder filename that created this script
expInfo = {
'subject number': '1', 
'gender': 'm',
'session': '1',
'handedness': 'r', 
'scanner': 'MS'
}

dlg = gui.DlgFromDict(title="WASABI Hyperalignment", dictionary=expInfo, sortKeys=False) 
if dlg.OK == False:
    core.quit()  # user pressed cancel
expInfo['date'] = data.getDateStr()  # add a simple timestamp
expInfo['expName'] = expName
expInfo['psychopyVersion'] = psychopyVersion

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
4. Prepare Experimental Dictionaries for Movies
"""
movieOrder = [OrderedDict([('runSeq',
            [OrderedDict([('moviefile', os.path.join(video_dir,'kungfury.mp4'))]),
            OrderedDict([('moviefile', os.path.join(video_dir,'01_Inscapes_NoScannerSound_h264.wmv'))])
            ] 
        )])
        ]
movie_code = [kungfury, inscapes]

restingstate_time = 420     # 7 minutes

"""
5. Prepare files to write
"""
sub_dir = os.path.join(_thisDir, 'data', 'sub-%05d' % (int(expInfo['subject number'])), 'ses-%02d' % (int(expInfo['session'])))
if not os.path.exists(sub_dir):
    os.makedirs(sub_dir)
psypy_filename = sub_dir + os.sep + u'sub-%05d_ses-%02d_task-%s_%s' % (int(expInfo['subject number']), int(expInfo['session']), expName, expInfo['date'])

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

# # Create python lists to later concatenate or convert into pandas dataframes
# hyperalign_bids_trial = []
# hyperalign_bids = []
"""
6. Initialize Trial-level Components
"""
# General Instructional Text
start_msg = 'Please wait. \nThe scan will begin shortly. Please do not move your head. \n Experimenter press [s] to continue.'
in_between_run_msg = 'Thank you.\n Please wait for the next scan to start \n Remember to please not move your head. \n Experimenter press [e] to continue.'
end_msg = 'Thank you for your participation. Please wait for the Experimenter.'

# create a default keyboard (e.g. to check for escape)
defaultKeyboard = keyboard.Keyboard()

# Initialize components for Routine "Introduction"
IntroductionClock = core.Clock()
Begin = visual.TextStim(win=win, name='Begin',
    text='This part of the study, you will be watching several movies. \nIt is important that you watch all the way through and you do not move your head. \nRelax, and please wait for the experimenter to press [Space].',
    font='Arial',
    pos=(0, 0), height=0.05, wrapWidth=None, ori=0, 
    color='white', colorSpace='rgb', opacity=1, 
    languageStyle='LTR',
    depth=0.0, 
    anchorHoriz='center')
BeginTask = keyboard.Keyboard()

######################
# Movie Components
######################
# Initialize components for Routine "Movie"
MovieClock = core.Clock()

# video_file = os.path.join(video_dir, 'kungfury.mp4')
# inscapes_file = os.path.join(video_dir, '01_Inscapes_NoScannerSound_h264.wmv')

# Preload Movies
movie1 = visual.MovieStim3(
    win=win, name='movie',
    noAudio = False,
    filename=movieOrder[0]['runSeq'][0]['moviefile'],
    # filename='C:\\Users\\Michael\\Dropbox (Dartmouth College)\\CANLab Projects\\WASABI\\Paradigms\\WASABI_Main\\hyperalignment\\videos\\practice_videos\\design\\Duck plays dead CUT.mp4',
    ori=0, pos=(0, 0), opacity=1,
    loop=False,
    depth=-1.0
    )
movie2 = visual.MovieStim3(
    win=win, name='movie',
    noAudio = False,
    filename=movieOrder[0]['runSeq'][1]['moviefile'],
    # filename='C:\\Users\\Michael\\Dropbox (Dartmouth College)\\CANLab Projects\\WASABI\\Paradigms\\WASABI_Main\\hyperalignment\\videos\\practice_videos\\design\\Duck plays dead CUT.mp4',
    ori=0, pos=(0, 0), opacity=1,
    loop=False,
    depth=-1.0
    )

# mov = visual.VlcMovieStim(win, videopath,
#     size=640,
#     # pos specifies the /center/ of the movie stim location
#     pos=[0, 100],
#     flipVert=False, flipHoriz=False,
#     loop=False)

movies = [movie1, movie2]

RestingStateClock = core.Clock()
fix_cross = visual.TextStim(win = win, text = '+', color = [1,1,1], height = 0.3)

# Create some handy timers
globalClock = core.Clock()  # to track the time since experiment started
routineTimer = core.CountdownTimer()  # to track time remaining of each (non-slip) routine

# Turn the mouse cursor off during the duration of the scan
win.mouseVisible = False

"""
7. Start Experimental Loops
    runLoop (prepare the movie order for the run)
    trialLoop (prepare the movie for each trial)
"""
# Start demarcation of the bodymap task in Biopac Acqknowledge
if biopac_exists:
    biopac.setData(biopac, 0)     
    biopac.setData(biopac, task_ID) 

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
        win.callOnFlip(print, "Cueing Biopac Channel: " + str(hyperalignment_intro))
        if biopac_exists == 1:
            win.callOnFlip(biopac.setData, biopac, 0)
            win.callOnFlip(biopac.setData, biopac, hyperalignment_intro)
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
print("CueOff Channel: " + str(hyperalignment_intro))
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
8a. Main Run Loop
"""
runLoop = data.TrialHandler(nReps=1, method='sequential', 
    extraInfo=expInfo, originPath=-1,
    trialList=movieOrder,
    seed=None, name='runLoop')

thisExp.addLoop(runLoop)  # add the loop to the experiment
thisRunLoop = runLoop.trialList[0]  # so we can initialise stimuli with some values
# abbreviate parameter names if possible (e.g. rgb = thisRunLoop.rgb)
if thisRunLoop != None:
    for paramName in thisRunLoop:
        exec('{} = thisRunLoop[paramName]'.format(paramName))

for thisRunLoop in runLoop:
    currentLoop = runLoop
    # abbreviate parameter names if possible (e.g. rgb = thisRunLoop.rgb)
    if thisRunLoop != None:
        for paramName in thisRunLoop:
            exec('{} = thisRunLoop[paramName]'.format(paramName))
    
#     """ 
#     8c. Play Movies
#     """
#     # set up handler to look after randomisation of conditions etc
#     trialLoop = data.TrialHandler(nReps=1, method='sequential', 
#         extraInfo=expInfo, originPath=-1,
#         trialList=runLoop.trialList[runLoop.thisIndex]['runSeq'],
#         seed=None, name='trialLoop')

#     thisExp.addLoop(trialLoop)  # add the loop to the experiment
#     thisTrialLoop = trialLoop.trialList[0]  # so we can initialise stimuli with some values
#     # abbreviate parameter names if possible (e.g. rgb = thisTrialLoop.rgb)
#     if thisTrialLoop != None:
#         for paramName in thisTrialLoop:
#             exec('{} = thisTrialLoop[paramName]'.format(paramName))
    
#     for thisTrialLoop in trialLoop:
#         currentLoop = trialLoop
#         # abbreviate parameter names if possible (e.g. rgb = thisTrialLoop.rgb)
#         if thisTrialLoop != None:
#             for paramName in thisTrialLoop:
#                 exec('{} = thisTrialLoop[paramName]'.format(paramName))
        
#         """
#         8b. Prepare the scanner trigger, set clock(s), and wait for dummy scans
#         """
#         ###############################################################################################
#         # Experimenter fMRI Start Instruction ____________________________________________________
#         ###############################################################################################
#         start = visual.TextStim(win, text=start_msg, height=.05, color=win.rgb + 0.5)
#         start.draw()  # Automatically draw every frame
#         win.flip()
#         fmriStart = globalClock.getTime()

#         if autorespond != 1:
#             # Trigger
#             event.waitKeys(keyList = 's') # experimenter start key - safe key before fMRI trigger
#             event.waitKeys(keyList='5')   # fMRI trigger
#             fmriStart = globalClock.getTime()
#             TR = 0.46
#             core.wait(TR*6)         # Wait 6 TRs, Dummy Scans

#         # ------Prepare to start Routine "Movie"-------
#         continueRoutine = True
#         # update component parameters for each repeat
#         # movie = visual.MovieStim3(
#         #     win=win, name='movie',
#         #     noAudio = False,
#         #     filename=movieOrder[0]['runSeq'][trialLoop.thisTrialN]['moviefile'],
#         #     # filename='C:\\Users\\Michael\\Dropbox (Dartmouth College)\\CANLab Projects\\WASABI\\Paradigms\\WASABI_Main\\hyperalignment\\videos\\practice_videos\\design\\Duck plays dead CUT.mp4',
#         #     ori=0, pos=(0, 0), opacity=1,
#         #     loop=False,
#         #     depth=-1.0
#         #     )
#         movie = movies[trialLoop.thisTrialN]
#         # Start a new BIDS data collection array for each run
#         hyperalignment_bids_data = []
#         movie_duration = movie.duration
#         if debug==1:
#             movie_duration = 10     # debugging
#         routineTimer.reset()
#         routineTimer.add(movie_duration)

#         # keep track of which components have finished
#         MovieComponents = [movie]
#         for thisComponent in MovieComponents:
#             thisComponent.tStart = None
#             thisComponent.tStop = None
#             thisComponent.tStartRefresh = None
#             thisComponent.tStopRefresh = None
#             if hasattr(thisComponent, 'status'):
#                 thisComponent.status = NOT_STARTED
#         # reset timers
#         t = 0
#         _timeToFirstFrame = win.getFutureFlipTime(clock="now")
#         MovieClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
#         frameN = -1
        
#         # -------Run Routine "Movie"-------
#         onset = globalClock.getTime() - fmriStart 
#         while continueRoutine and routineTimer.getTime() > 0:
#             # get current time
#             t = MovieClock.getTime()
#             tThisFlip = win.getFutureFlipTime(clock=MovieClock)
#             tThisFlipGlobal = win.getFutureFlipTime(clock=None)
#             frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
#             # update/draw components on each frame
            
#             # *movie* updates
#             if movie.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
#                 # keep track of start time/frame for later
#                 movie.frameNStart = frameN  # exact frame index
#                 movie.tStart = t  # local t and not account for scr refresh
#                 movie.tStartRefresh = tThisFlipGlobal  # on global time
#                 win.timeOnFlip(movie, 'tStartRefresh')  # time at next scr refresh
#                 movie.setAutoDraw(True)
                
#                 win.callOnFlip(print, "Starting ", movieOrder[0]['runSeq'][trialLoop.thisTrialN]['moviefile'])
#                 win.callOnFlip(print, "Cue Biopac " + str(movie_code[trialLoop.thisTrialN]))
#                 if biopac_exists == 1:
#                     win.callOnFlip(biopac.setData, biopac, 0)
#                     win.callOnFlip(biopac.setData, biopac, movie_code[trialLoop.thisTrialN])
#             # if movie.status == STARTED:  # one frame should pass before updating params and completing
#                 # updating other components during *movie*
#                 # movie.setMovie(movieOrder[0]['runseq'][runLoop.thisTrialN+1]['moviefile'])
#                 if tThisFlipGlobal > movie.tStartRefresh + movie_duration-frameTolerance:
#                     # keep track of stop time/frame for later
#                     movie.tStop = t  # not accounting for scr refresh
#                     movie.frameNStop = frameN  # exact frame index
#                     win.timeOnFlip(movie, 'tStopRefresh')  # time at next scr refresh
#                     movie.setAutoDraw(False)
#             if movie.status == FINISHED:  # force-end the routine
#                 continueRoutine = False
            
#             # check for quit (typically the Esc key)
#             if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
#                 core.quit()
            
#             # check if all components have finished
#             if not continueRoutine:  # a component has requested a forced-end of Routine
#                 break
#             continueRoutine = False  # will revert to True if at least one component still running
#             for thisComponent in MovieComponents:
#                 if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
#                     continueRoutine = True
#                     break  # at least one component has not yet finished
            
#             # refresh the screen
#             if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
#                 win.flip()

#         # -------Ending Routine "Movie"-------
#         for thisComponent in MovieComponents:
#             if hasattr(thisComponent, "setAutoDraw"):
#                 thisComponent.setAutoDraw(False)
#         trialLoop.addData('movie.started', movie.tStartRefresh)
#         trialLoop.addData('movie.stopped', movie.tStopRefresh)
#         movie.stop()
#         hyperalignment_trial = []
#         hyperalignment_trial.extend((onset, t, movieOrder[0]['runSeq'][trialLoop.thisTrialN]['moviefile']))
#         hyperalignment_bids_data.append(hyperalignment_trial)

#         # the Routine "Movie" was not non-slip safe, so reset the non-slip timer
#         routineTimer.reset()
#         thisExp.nextEntry()

#         """
#         9. Save Run File
#         """
#         bids_run_filename = sub_dir + os.sep + u'sub-%05d_ses-%02d_task-%s_run-%s_events.tsv' % (int(expInfo['subject number']), int(expInfo['session']), expName, str(trialLoop.thisTrialN+1))
#         hyperalignment_bids_data = pd.DataFrame(hyperalignment_bids_data, columns = ['onset','duration','condition'])
#         hyperalignment_bids_data.to_csv(bids_run_filename, sep="\t")

#         """
#         8d. End of a Movie, Wait for Experimenter instructions to begin next run
#         """   
#         message = visual.TextStim(win, text=in_between_run_msg, height=0.05)
#         message.draw()
#         win.callOnFlip(print, "Awaiting Experimenter to start next run...")
#         if biopac_exists == 1:
#             win.callOnFlip(biopac.setData, biopac, 0)
#             win.callOnFlip(biopac.setData, biopac, between_run_msg)
#         win.flip()
#         # Autoresponder
#         if autorespond != 1:
#             event.waitKeys(keyList = 'e')
#         routineTimer.reset()
#     # completed Movie repeats of 'trialLoop'
    
# # completed 1 repeats of 'runLoop'

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

hyperalignment_bids_data = []
"""
8f. Resting State
"""
# ------Prepare to start Routine "RestingState"-------
continueRoutine = True
routineTimer.reset()
if debug == 1:
    restingstate_time=10 

routineTimer.add(restingstate_time)
# update component parameters for each repeat
# keep track of which components have finished
RestingStateComponents = [fix_cross]
for thisComponent in RestingStateComponents:
    thisComponent.tStart = None
    thisComponent.tStop = None
    thisComponent.tStartRefresh = None
    thisComponent.tStopRefresh = None
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED
# reset timers
t = 0
_timeToFirstFrame = win.getFutureFlipTime(clock="now")
RestingStateClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
frameN = -1

# -------Run Routine "RestingState"-------
onset = globalClock.getTime() - fmriStart 
while continueRoutine and routineTimer.getTime() > 0:
    # get current time
    t = RestingStateClock.getTime()
    tThisFlip = win.getFutureFlipTime(clock=RestingStateClock)
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
        if biopac_exists:
            win.callOnFlip(biopac.setData, biopac, 0)
            win.callOnFlip(biopac.setData, biopac, resting_state)
        fix_cross.setAutoDraw(True)
    if fix_cross.status == STARTED:
        # is it time to stop? (based on global clock, using actual start)
        if tThisFlipGlobal > fix_cross.tStartRefresh + restingstate_time-frameTolerance:
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
    for thisComponent in RestingStateComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

# -------Ending Routine "RestingState"-------
if biopac_exists:
    biopac.setData(biopac, 0)
for thisComponent in RestingStateComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)
thisExp.addData('fix_cross.started', fix_cross.tStartRefresh)
thisExp.addData('fix_cross.stopped', fix_cross.tStopRefresh)
hyperalignment_trial = []
hyperalignment_trial.extend((onset, t, "RestingState"))
hyperalignment_bids_data.append(hyperalignment_trial)

thisExp.nextEntry()
routineTimer.reset()

# Flip one final time so any remaining win.callOnFlip() 
# and win.timeOnFlip() tasks get executed before quitting
win.flip()

"""
9. Save data into BIDS .TSV, Excel and .CSV formats and Tying up Loose Ends
""" 
bids_run_filename = sub_dir + os.sep + u'sub-%05d_ses-%02d_task-%s_run-%s_events.tsv' % (int(expInfo['subject number']), int(expInfo['session']), expName, '3')
hyperalignment_bids_data = pd.DataFrame(hyperalignment_bids_data, columns = ['onset','duration','condition'])
hyperalignment_bids_data.to_csv(bids_run_filename, sep="\t")

# these shouldn't be strictly necessary (should auto-save)
thisExp.saveAsWideText(psypy_filename+'.csv', delim='auto')
thisExp.saveAsPickle(psypy_filename)
logging.flush()
# make sure everything is closed down
message = visual.TextStim(win, text=end_msg)
message.draw()
if biopac_exists == 1:
    biopac.close()  # Close the labjack U3 device to end communication with the Biopac MP150
thisExp.abort()  # or data files will save again on exit
win.close()  # close the window
core.quit()

"""
End of Experiment
"""