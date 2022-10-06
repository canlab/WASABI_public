# === IMENSA PROJECT === 
# using ntp module. add actual time stamp and ntp time using server time. Used 4/12~

""" 
0. General SETUP 
"""
# === 0a. Import Libraries ===
from __future__ import absolute_import, division
import numpy as np  # whole numpy lib is available, prepend 'np.'
from numpy import (sin, cos, tan, log, log10, pi, sqrt, deg2rad, rad2deg, eye, average, std, linspace, asarray)
from numpy.random import random, randint, normal, shuffle
import pandas as pd
import random as rd
from builtins import str, range
import os, sys, time, ntplib
import collections
try:    from collections import OrderedDict
except ImportError:    OrderedDict=dict

from psychopy import locale_setup, sound, gui, visual, core, data, event, logging, clock, prefs
prefs.hardware['audioLib'] = ['PTB']
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED, STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)
from psychopy.hardware import keyboard


# === 0b. Constants and Togglers ===
debug = 0
autorespond = 0
biopac_exists = 1
restart = [1, 1, 1]


__author__ = "Byeol Kim"
__version__ = "0.3"
__computer__ = "neurofeedback PC"
__email__ = "byeol.kim.gr@dartmouth.edu"


# === 0c. Autoresponding setup ===
class simKeys:
    ''' an object to simulate key presses
    keyList: a list of keys to watch / name: randomly selected from keyList
    rtRange: [min RT, max RT] where min and max RT are sepecified in ms '''
    def __init__(self, keyList, rtRange):
        self.name=np.random.choice(keyList)
        self.rt = np.random.choice(np.linspace(rtRange[0], rtRange[1])/1000)
thisSimKey=simKeys(keyList=['space'], rtRange=[200,1000])


# === 0d. Biopac setup ===
if biopac_exists:
    ### Initialize LabJack U3 Device, which is connected to the Biopac MP150 psychophysiological amplifier data acquisition device. This involves importing the labjack U3 Parallelport to USB library.
    ### U3 Troubleshooting:
    ### Check to see if u3 was imported correctly with: help('u3')
    ### Check to see if u3 is calibrated correctly with: cal_data = biopac.getCalibrationData()
    ### Check to see the data at the FIO, EIO, and CIO ports: biopac.getFeedback(u3.PortStateWrite(State = [0, 0, 0]))
    try:
        from psychopy.hardware.labjacks import U3
        # from labjack import u3
    except ImportError:
        import u3
    ### Function defining setData to use the FIOports (address 6000)
    def biopacSetData(self, byte, endian='big', address=6000): 
        if endian=='big':
            byteStr = '{0:08b}'.format(byte)[-1::-1]
        else:
            byteStr = '{0:08b}'.format(byte)
        [self.writeRegister(address+pin, int(entry)) for (pin, entry) in enumerate(byteStr)]

    biopac = U3()
    biopac.setData = biopacSetData
    ### Set all FIO bits to digital output and set to low (i.e. “0")
    ### The list in square brackets represent what’s desired for the FIO, EIO, CIO ports. We will only change the FIO port's state.
    biopac.configIO(FIOAnalog=0, EIOAnalog=0)
    biopac.setData(biopac, byte=0)

# === 0e. Experimental Dialog Boxes and expInfo ===
expName = 'movie'
expInfo = {'subject number': '0', 'visit': '1', 'condition': 'p'}
if not debug:
    dlg = gui.DlgFromDict(title="IMENSA study movie run", dictionary=expInfo, sortKeys=False) 
    if not dlg.OK: 
        core.quit()  # user pressed cancel
expInfo['date'] = data.getDateStr()  # add a timestamp '2021_Dec_27_1947'
expInfo['expName'] = expName

# === 0f. Window setup ===
""" DBIC uses a Panasonic DW750 Projector with a native resolution of 1920x1200 (16:10), but it is configured at 1920x1080 (16:9) at DBIC. Configure a black window with a 16:9 aspect ratio during development (1280x720) and production (1920x1080)"""
if debug:
    win = visual.Window(size=[1280, 720], fullscr=False, 
    ### fullscr = False for testing, True for running participants
    screen=0,   # Change this to the appropriate display 
    winType='pyglet', allowGUI=True, allowStencil=True,
    monitor='testMonitor', color='black', colorSpace='rgb',
    blendMode='avg', useFBO=True, units='height')
else:
    win = visual.Window(size=[1920, 1080], fullscr=True, 
    screen=4,   # Change this to the appropriate fMRI projector 
    winType='pyglet', allowGUI=True, allowStencil=True,
    monitor='testMonitor', color='black', colorSpace='rgb',
    blendMode='avg', useFBO=True, units='height')
frameTolerance = 0.001  # how close to onset before 'same' frame



""" 
1. Experimental Parameters (differ from experiments)
"""
# === 1a. Biopac parameters ===
### Relevant Biopac commands: To send a Biopac marker code to Acqknowledge, replace the FIO number with a value between 0-255(dec), or an 8-bit word(bin). For instance, the following code would send a value of 15 by setting the first 4 bits to “1": biopac.getFeedback(u3.PortStateWrite(State = [15, 0, 0])). Toggling each of the FIO 8 channels directly: biopac.setFIOState(fioNum = 0:7, state=1). Another command that may work: biopac.setData(byte)
on_ID=1
movie_ID=7
view_trial_ID = 23
rating_trial_ID = 39
resting_ID = 5

# === 1b. Directory setup ===
_thisDir = os.path.dirname(os.path.abspath(__file__)) 
os.chdir(_thisDir)
main_dir = _thisDir
stimuli_dir = 'C:\\Users\\Dartmouth\\Documents\\imensa\\stimuli'
video_dir = stimuli_dir + os.sep + "main_video"
sub_dir = os.path.join(main_dir, 'scan_data', 'sub%03d' % (int(expInfo['subject number'])), 'sess%01d_%s' % (int(expInfo['visit']), expInfo['condition']))
if not os.path.exists(sub_dir):
    os.makedirs(sub_dir)
psypy_filename = sub_dir + os.sep + u'imensa_sub%03d_sess%01d_%s_%s' % (int(expInfo['subject number']), int(expInfo['visit']), expName, expInfo['date'])


# === 1c. ExperimentHandler ===
### ExperimentHandler isn't essential but helps with data saving
thisExp = data.ExperimentHandler(name=expName, version='', extraInfo=expInfo, 
    runtimeInfo=None, savePickle=True, saveWideText=True, dataFileName=psypy_filename)


# === 1d. Log for detail verbose info ===
logFile = logging.LogFile(psypy_filename+'.log', level=logging.EXP)
logging.console.setLevel(logging.WARNING)  # this outputs to the screen, not a file
endExpNow = False   # flag for 'escape' or other condition => quit the exp


""" 
2. Stimuli preparation
"""


# === 2a. Movie ===
### make elements and OrderedDict of movie directories
if expInfo['condition'] == 'p':
    condition = 'pos'
if expInfo['condition'] == 'n':
    condition = 'neg'
movie_by_run = []
movie_dict = []
num_stim = 3
num_run = 3

for run_i in range(num_run):
    movie_by_run.append([])
    movie_dict.append([])
    for trial_i in range(num_stim):
        movie_by_run[run_i].append(OrderedDict(([('file',condition+'-'+str(run_i*num_stim+trial_i+1))])))
    movie_dict[run_i]= OrderedDict([('run', movie_by_run[run_i])])


# === 2b. Rating parameters ===
stim_size = .5
ratingScaleHeight=.05
rating_pos_y = -0.2
slider_half_size = 0.4
TIME_INTERVAL = 0.005   # Speed at which slider ratings udpate

### cue and rating bar
cue_type = ['warm', 'joyful', 'inspired', 'sad', 'disgusted', 'ashamed', 'horrified']
cum_num = len(cue_type)
cue_list = []
IntensityAnchors = []
for cue_i in range(cum_num):
    cue_list.append(os.path.join(stimuli_dir, "cue", (cue_type[cue_i]+'.png')))
    tmp = visual.ImageStim(win, image=cue_list[cue_i], name='intensityAnchors', 
        size=[np.array([4, 9/4])*stim_size], texRes=512, interpolate=True)
    IntensityAnchors.append(tmp)

Rating = visual.Rect(win, height=ratingScaleHeight, fillColor='orange', lineColor='black')
Rating_bar = visual.Rect(win, height=ratingScaleHeight, width=slider_half_size*2, pos=[0, rating_pos_y], fillColor='white', lineColor='black')
IntensityMouse = event.Mouse(win=win)


# === 2c. Instructional TextStim ===
begin_msg = 'We will start three long video runs of 12 mins each. You will be watching a series of documentary video clips and will be asked to respond 7 questions regarding to the previous clip within 6 seconds each. \nIt is important that you watch all the way through and you do not move your head. \nRelax, and please wait for the experimenter to press [Space].'
restart_msg = 'Do you want to skip this run? [y/n]'
wait_trigger_msg = 'Please wait. The scan will begin shortly.\nPlease do not move your head. \n Experimenter press [s] to continue.'
in_between_run_msg = 'Thank you.\n Please wait for the next scan to start \n Remember to please not move your head. \n Experimenter press [e] to continue.'
resting_msg = 'Start a 10 min resting run.\nYou can take a rest but please do not move your head and do not close your eyes. \n Experimenter press [s] to continue.'
end_msg = 'Thank you for your participation.\nPlease wait for the experimenter.'

Begin = visual.TextStim(win, name='Begin', text=begin_msg, font='Arial', 
    pos=(0, 0), height=0.05, wrapWidth=None, ori=0, color='white', colorSpace='rgb', 
    opacity=1, languageStyle='LTR', depth=0.0, anchorHoriz='center')
wait_trigger_stim_1 = visual.TextStim(win, text=wait_trigger_msg, height=.05, color='white')
wait_trigger_stim_2 = visual.TextStim(win, text=wait_trigger_msg, height=.05, color=[0.1, 0.1, 0.1])
in_between_run_stim = visual.TextStim(win, text=in_between_run_msg, height=0.05)
resting_msg_stim = visual.TextStim(win, text=resting_msg, height=0.05)
fixation = visual.TextStim(win, text = '+', color = [1,1,1], height = 0.3)
end_stim = visual.TextStim(win, text=end_msg, height=0.05)


# === 2c. Keyboard and Clocks ===
defaultKeyboard = keyboard.Keyboard()   # to check for escape
Begin_resp = keyboard.Keyboard()

### ticktock
globalClock = core.Clock()              # to track the time since experiment started
routineTimer = core.CountdownTimer()    # to track time remaining of each (non-slip) routine
IntroductionClock = core.Clock()
MovieClock = core.Clock()
RatingClock = core.Clock()
RestingStateClock = core.Clock()
ntp_c = ntplib.NTPClient()

ratingTime = 6              # Rating Time limit in seconds
restingstate_time = 575     # 10 minutes
dummy_scan = 10
if debug:
    restingstate_time = 5
    dummy_scan = 2

"""
3. Start Experimental Loops
    runLoop (prepare the movie order for the run)
    trialLoop (prepare the movie for each trial)
"""

if biopac_exists:
    biopac.setData(biopac, 0)     
    biopac.setData(biopac, on_ID) 

### ------Prepare to start Routine "Introduction"-------
continueRoutine = True
Begin_resp.keys = []
Begin_resp.rt = []
_Begin_resp_allKeys = []
win.mouseVisible = False                        # Turn the mouse cursor off

IntroductionComponents = [Begin, Begin_resp]
for thisComponent in IntroductionComponents:    
    thisComponent.tStartRefresh = None
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED

### reset timers
dur = 0
_timeToFirstFrame = win.getFutureFlipTime(clock="now")
IntroductionClock.reset(-_timeToFirstFrame)     # t0 is time of first possible flip
Begin.tStart = globalClock.getTime()

### -------Run Routine "Introduction"-------
while continueRoutine:
    dur = IntroductionClock.getTime()
    tThisFlip = win.getFutureFlipTime(clock=IntroductionClock)
    tThisFlipGlobal = win.getFutureFlipTime(clock=None)
    
    # *Begin* updates
    if Begin.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        # keep track of start time/frame for later
        Begin.tStartRefresh = tThisFlipGlobal   # on global time
        win.timeOnFlip(Begin, 'tStartRefresh')  # time at next scr refresh
        Begin.setAutoDraw(True)
    
    # *Begin_resp* updates
    waitOnFlip = False
    if Begin_resp.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        # keep track of start time/frame for later
        Begin_resp.tStartRefresh = tThisFlipGlobal  # on global time
        win.timeOnFlip(Begin_resp, 'tStartRefresh') # time at next scr refresh
        Begin_resp.status = STARTED  # keyboard checking is just starting
        waitOnFlip = True
        win.callOnFlip(print, "Starting Introduction")
        win.callOnFlip(Begin_resp.clearEvents, eventType='keyboard')  # clear events on next screen flip
    if Begin_resp.status == STARTED and not waitOnFlip:
        theseKeys = Begin_resp.getKeys(keyList=['space'], waitRelease=False)
        _Begin_resp_allKeys.extend(theseKeys)
        if len(_Begin_resp_allKeys):
            Begin_resp.keys = _Begin_resp_allKeys[-1].name  # just the last key pressed
            Begin_resp.rt = _Begin_resp_allKeys[-1].rt
            # a response ends the routine
            continueRoutine = False
    
    # Autoresponder
    if dur >= thisSimKey.rt and autorespond == 1:
        _Begin_resp_allKeys.extend([thisSimKey])  

    # check for quit (typically the Esc key)
    if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
        core.quit()
    
    # check if all components have finished
    if not continueRoutine:     # a component has requested a forced-end of Routine
        break
    continueRoutine = False     # will revert to True if at least one component still running
    for thisComponent in IntroductionComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break       # at least one component has not yet finished
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

### -------Ending Routine "Introduction"-------
Begin.tStop = globalClock.getTime()
for thisComponent in IntroductionComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)
thisExp.addData('Begin.start', Begin.tStart)
thisExp.addData('Begin.stop', Begin.tStop)
thisExp.addData('Begin.duration', dur)
# check responses
if Begin_resp.keys in ['', [], None]:   # No response was made
    Begin_resp.keys = None
thisExp.addData('BeginTask.keys',Begin_resp.keys)
if Begin_resp.keys != None:             # we had a response
    thisExp.addData('BeginTask.rt', Begin_resp.rt)
thisExp.nextEntry()


"""
4. Main Run Loop 
"""
runLoop = data.TrialHandler(nReps=1, method='sequential', extraInfo=expInfo, 
    originPath=-1,trialList=movie_dict, seed=2, name='runLoop')
thisExp.addLoop(runLoop)                # add the loop to the experiment

for thisrunLoop in runLoop:                     # Loop through each run.
    """
    4a. Run Loop Starts, waiting trigger from scanner
    """

    if restart[runLoop.thisTrialN]:

        wait_trigger_stim_1.draw()          # Automatically draw every frame
        win.flip()      
        bids_data = []  # Start a new BIDS data collection array for each run
        run_starttime = globalClock.getTime()

        if not autorespond:
            event.waitKeys(keyList = 's')   # experimenter start key
            wait_trigger_stim_2.draw()      
            win.flip()
            event.waitKeys(keyList='5')     # fMRI trigger
            win.fillColor = 'black'
            win.flip()
            run_starttime = globalClock.getTime()
            run_starttime_ntp = ntp_c.request('time.windows.com', version=3)
            if biopac_exists:
                biopac.setData(biopac, movie_ID) 
            core.wait(dummy_scan)                 # Wait 6 TRs, Dummy Scans


        # set up handler to look after randomisation of conditions etc
        runLoop.addData('run.start', run_starttime)
        runLoop.addData('run.start act', time.ctime(run_starttime_ntp.tx_time)[4:-5])
        runLoop.addData('run.start ntp', run_starttime_ntp.tx_time)

        trialLoop = data.TrialHandler(nReps=1, method='sequential', 
            trialList=runLoop.trialList[runLoop.thisTrialN]['run'],
            extraInfo=expInfo, originPath=-1, seed=None, name='trialLoop')
        thisExp.addLoop(trialLoop)          # add the loop to the experiment
        trialLoop_2 = []

        
        for thisTrialLoop in trialLoop:
            """
            4b. Movie Trial Loop Starts
            """      
            # ================================ MOVIE START ==================================
            # ------Prepare to start Routine "Movie"-------
            continueRoutine = True
            movie = visual.MovieStim3(filename=os.path.join(video_dir, 
            (runLoop.trialList[runLoop.thisTrialN]['run'][trialLoop.thisTrialN]['file']+'.mov')),
                win=win, name='movie', noAudio=False, depth=-1.0)
            movie_duration = movie.duration
            if debug:
                movie_duration = 2
            current_movie_name = movie_by_run[runLoop.thisTrialN][trialLoop.thisTrialN]['file']
            frameN = -1

            MovieComponents = [movie]
            for thisComponent in MovieComponents:
                thisComponent.tStartRefresh = None
                if hasattr(thisComponent, 'status'):
                    thisComponent.status = NOT_STARTED

            # reset timers
            dur = 0
            _timeToFirstFrame = win.getFutureFlipTime(clock="now")
            MovieClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
            routineTimer.reset()
            routineTimer.add(movie_duration)
            if biopac_exists:
                biopac.setData(biopac, view_trial_ID)
            movie.tStart = globalClock.getTime()
            onset = movie.tStart - run_starttime 
            

            # -------Run Routine "Movie"-------
            while continueRoutine and routineTimer.getTime() > 0:
                # get current time
                dur = MovieClock.getTime()
                tThisFlip = win.getFutureFlipTime(clock=MovieClock)
                tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                
                # *movie* updates
                if movie.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    movie.frameNStart = frameN  # exact frame index
                    movie.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(movie, 'tStartRefresh')  # time at next scr refresh
                    movie.setAutoDraw(True)  # start movie, movie.status is changed to STARTED 
                    
                    win.callOnFlip(print, "Starting Movie run_"+str(runLoop.thisTrialN+1)+" trial_"+str(trialLoop.thisTrialN+1), current_movie_name)
                    if tThisFlipGlobal > movie.tStartRefresh + movie_duration-frameTolerance:
                    #     # keep track of stop time/frame for later
                        movie.frameNStop = frameN  # exact frame index
                        movie.setAutoDraw(False)
                if movie.status == FINISHED:  # force-end the routine
                    continueRoutine = False
                
                # check for quit (typically the Esc key)
                if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
                    core.quit()
                
                # check if all components have finished
                if not continueRoutine:  # a component has requested a forced-end of Routine
                    break
                continueRoutine = False  # will revert to True if at least one component still running
                for thisComponent in MovieComponents:
                    if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                        continueRoutine = True
                        break  # at least one component has not yet finished
                
                # refresh the screen
                if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                    win.flip()

            # -------Ending Routine "Movie"-------
            movie.tStop = globalClock.getTime()
            for thisComponent in MovieComponents:
                if hasattr(thisComponent, "setAutoDraw"):
                    thisComponent.setAutoDraw(False)
            trialLoop.addData('movie.start', movie.tStart)
            trialLoop.addData('movie.stop', movie.tStop)
            trialLoop.addData('movie.duration', dur)
            movie.stop()
            bids_data.append((onset, dur, current_movie_name, 0))        
            # ================================ MOVIE END ==================================

            if biopac_exists:
                biopac.setData(biopac, rating_trial_ID)
            rating_part_start = globalClock.getTime()
            trialLoop_2 = data.TrialHandler(nReps=1, method='random', trialList=cue_type, extraInfo=expInfo, originPath=-1, seed=None, name='trialLoop_2')
            runLoop.addData('Rating part.start', rating_part_start)
            thisExp.addLoop(trialLoop_2)          # add the loop to the experiment
            

            for thisTrialLoop_2 in trialLoop_2: 
                """
                4c. Rating Trial Loop Starts
                """      
                # ============================== RATING START ==================================
                # ------Prepare to start Routine "Rating"-------
                continueRoutine = True
                IntensityMouse = event.Mouse(win=win, visible=False) # Re-initialize IntensityMouse
                Rating.startpoint = np.random.choice(101,1)[0] 
                IntensityMouse.setPos((Rating.startpoint/100*2*slider_half_size - slider_half_size,0))
                Rating.width = slider_half_size
                Rating.pos = [-slider_half_size/2, rating_pos_y]
                timeAtLastInterval = 0
                mouseX = 0
                oldMouseX = 0
                timeout = 0

                RatingComponents = [IntensityMouse, Rating, Rating_bar, IntensityAnchors[trialLoop_2.thisIndex]]
                for thisComponent in RatingComponents:
                    thisComponent.tStart = None
                    thisComponent.tStartRsefresh = None
                    thisComponent.tStopRefresh = None                
                    if hasattr(thisComponent, 'status'):
                        thisComponent.status = NOT_STARTED

                # reset timers
                t = 0
                _timeToFirstFrame = win.getFutureFlipTime(clock="now")  # very small, 0.00053
                RatingClock.reset(-_timeToFirstFrame)          # set clock as 0.00053
                Rating.tStart = globalClock.getTime()

                # -------Run Routine "Rating"-------
                while continueRoutine:
                    timeNow = globalClock.getTime()
                    if (timeNow - timeAtLastInterval) > TIME_INTERVAL:
                        mouseRel=IntensityMouse.getRel()
                        mouseX=oldMouseX + mouseRel[0]
                    Rating.pos = ((-slider_half_size + mouseX)/2, rating_pos_y)
                    Rating.width = abs((mouseX+slider_half_size))
                    if mouseX > slider_half_size:
                        mouseX = slider_half_size
                    if mouseX < -slider_half_size:
                        mouseX = -slider_half_size
                    timeAtLastInterval = timeNow
                    oldMouseX=mouseX
                    sliderValue = (mouseX + slider_half_size) / (slider_half_size*2) * 100

                    # get current time
                    t = RatingClock.getTime()
                    tThisFlip = win.getFutureFlipTime(clock=RatingClock)
                    tThisFlipGlobal = win.getFutureFlipTime(clock=None)

                    # *IntensityAnchors* updates
                    if IntensityAnchors[trialLoop_2.thisIndex].status == NOT_STARTED and t >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        IntensityAnchors[trialLoop_2.thisIndex].tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(IntensityAnchors[trialLoop_2.thisIndex], 'tStartRefresh')  # time at next scr refresh
                        IntensityAnchors[trialLoop_2.thisIndex].setAutoDraw(True)
                    if IntensityAnchors[trialLoop_2.thisIndex].status == STARTED:
                        # is it time to stop? (based on global clock, using actual start)
                        if tThisFlipGlobal > IntensityAnchors[trialLoop_2.thisIndex].tStartRefresh + ratingTime-frameTolerance:
                            # keep track of stop time/frame for later
                            win.timeOnFlip(IntensityAnchors[trialLoop_2.thisIndex], 'tStopRefresh')  # time at next scr refresh
                            IntensityAnchors[trialLoop_2.thisIndex].setAutoDraw(False)
                            timeout = 1


                    # *IntensityMouse* updates
                    if IntensityMouse.status == NOT_STARTED and t >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        IntensityMouse.tStart = t  # local t and not account for scr refresh
                        IntensityMouse.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(IntensityMouse, 'tStartRefresh')  # time at next scr refresh
                        IntensityMouse.status = STARTED
                        prevButtonState = IntensityMouse.getPressed()  # if button is down already this ISN'T a new click
                    if IntensityMouse.status == STARTED:  # only update if started and not finished!
                        if tThisFlipGlobal > IntensityMouse.tStartRefresh + ratingTime-frameTolerance:
                            # keep track of stop time/frame for later
                            IntensityMouse.status = FINISHED
                            timeout = 1
                        buttons = IntensityMouse.getPressed()
                        if buttons != prevButtonState:  # button state changed?
                            prevButtonState = buttons
                            if sum(buttons) > 0:  # state changed to a new click
                                # abort routine on response
                                continueRoutine = False
                    
                    # *Rating_bar* updates
                    if Rating_bar.status == NOT_STARTED and t >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        Rating_bar.tStart = t  # local t and not account for scr refresh
                        Rating_bar.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(Rating_bar, 'tStartRefresh')  # time at next scr refresh
                        Rating_bar.setAutoDraw(True)
                    if Rating_bar.status == STARTED:
                        # is it time to stop? (based on global clock, using actual start)
                        if tThisFlipGlobal > Rating_bar.tStartRefresh + ratingTime-frameTolerance:
                        # keep track of stop time/frame for later
                            win.timeOnFlip(Rating_bar, 'tStopRefresh')  # time at next scr refresh
                            Rating_bar.setAutoDraw(False)
                            timeout = 1


                    # *Rating* updates
                    if Rating.status == NOT_STARTED and t >= 0.0-frameTolerance:
                        # keep track of start time/frame for later
                        Rating.tStartRefresh = tThisFlipGlobal  # on global time
                        win.timeOnFlip(Rating, 'tStartRefresh')  # time at next scr refresh
                        Rating.setAutoDraw(True)
                    if Rating.status == STARTED:
                        # is it time to stop? (based on global clock, using actual start)
                        if tThisFlipGlobal > Rating.tStartRefresh + ratingTime-frameTolerance:
                            win.timeOnFlip(Rating, 'tStopRefresh')  # time at next scr refresh
                            Rating.setAutoDraw(False)
                            timeout = 1


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
                    for thisComponent in RatingComponents:
                        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                            continueRoutine = True
                            break  # at least one component has not yet finished

                    # refresh the screen
                    if continueRoutine:
                        win.flip()

                # -------Ending Routine "Rating"-------
                Rating.tStop = globalClock.getTime()
                for thisComponent in RatingComponents:
                    if hasattr(thisComponent, "setAutoDraw"):
                        thisComponent.setAutoDraw(False)
                # store data for thisExp (ExperimentHandler)
                thisExp.addData('rating.dimension',cue_type[trialLoop_2.thisIndex])
                thisExp.addData('rating.starting point', Rating.startpoint)
                thisExp.addData('rating.response', sliderValue)
                thisExp.addData('rating.rt', t)
                thisExp.addData('rating.timeout', timeout)
                thisExp.addData('rating.start', Rating.tStart)
                thisExp.addData('rating.stop', Rating.tStop)
                thisExp.nextEntry()
                bids_data.append((Rating.tStart, t, cue_type[trialLoop_2.thisIndex], sliderValue))
            
                # ============================== RATING END ==================================
            """
            4bc. Trial Loop Ends
            """
            
        ### Save Run File
        bids_run_filename = sub_dir + os.sep + u'imensa_sub%03d_sess%01d_%s_run%01d.tsv' % (int(expInfo['subject number']), int(expInfo['visit']), expName, int(runLoop.thisTrialN+1))
        bids_data = pd.DataFrame(bids_data, columns = ['onset','duration','condition','rating'])
        bids_data.to_csv(bids_run_filename, sep="\t")
        run_endtime = globalClock.getTime()
        run_endtime_ntp = ntp_c.request('time.windows.com', version=3)
        if biopac_exists:
            win.callOnFlip(biopac.setData, biopac, 0)
        runLoop.addData('run.end', run_endtime)
        runLoop.addData('run.end act', time.ctime(run_endtime_ntp.tx_time)[4:-5])
        runLoop.addData('run.end ntp', run_endtime_ntp.tx_time)
        thisExp.nextEntry()

        ### Wait for Experimenter instructions to begin next run
        in_between_run_stim.draw()
        win.callOnFlip(print, "Awaiting experimenter to start next run...")
        win.flip()

        # Autoresponder
        if not autorespond:
            event.waitKeys(keyList = 'e')

    ### End of one run 
"""
4a. Run Loop Ends
"""


"""
5. Resting State Run
"""
resting_msg_stim.draw()  
win.flip()
run_starttime = globalClock.getTime()
if autorespond != 1:
    event.waitKeys(keyList = 's')   # experimenter start key
    wait_trigger_stim_2.draw() 
    win.flip()
    event.waitKeys(keyList = '5')   # fMRI trigger
    win.fillColor = 'gray'
    win.flip()
    run_starttime = globalClock.getTime()
    if biopac_exists:
        biopac.setData(biopac, resting_ID) 
    core.wait(dummy_scan)                 # Wait 6 TRs, Dummy Scans



### ------Prepare to start Routine "RestingState"-------
continueRoutine = True
RestingStateComponents = [fixation]
for thisComponent in RestingStateComponents:
    thisComponent.tStartRefresh = None
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED

# reset timers
t = 0
_timeToFirstFrame = win.getFutureFlipTime(clock="now")
RestingStateClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
routineTimer.reset()
routineTimer.add(restingstate_time)
fixation.tStart = globalClock.getTime()
onset = fixation.tStart - run_starttime 

### -------Run Routine "RestingState"-------
while continueRoutine and routineTimer.getTime() > 0:
    # get current time
    t = RestingStateClock.getTime()
    tThisFlip = win.getFutureFlipTime(clock=RestingStateClock)
    tThisFlipGlobal = win.getFutureFlipTime(clock=None)
    
    if fixation.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
        fixation.tStartRefresh = tThisFlipGlobal  
        win.timeOnFlip(fixation, 'tStartRefresh') 
        fixation.setAutoDraw(True)
    if fixation.status == STARTED:
        if tThisFlipGlobal > fixation.tStartRefresh + restingstate_time-frameTolerance:
            fixation.setAutoDraw(False)
    
    if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
        core.quit()
    
    if not continueRoutine:  
        break
    continueRoutine = False  
    for thisComponent in RestingStateComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  
    
    if continueRoutine: 
        win.flip()

# -------Ending Routine "RestingState"-------
fixation.tStop = globalClock.getTime()
if biopac_exists:
    biopac.setData(biopac, 0)
for thisComponent in RestingStateComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)

thisExp.addData('run.started', run_starttime)
# run_endtime = globalClock.getTime()
thisExp.addData('resting.started', fixation.tStart)
thisExp.addData('resting.stopped', fixation.tStop)
thisExp.addData('resting.t', t)
# thisExp.addData('run.ended', run_endtime)
thisExp.nextEntry()


"""
5. Save data into BIDS .TSV, Excel and .CSV formats and Tying up Loose Ends
""" 
end_stim.draw()
win.flip()

# these shouldn't be strictly necessary (should auto-save)
thisExp.saveAsWideText(psypy_filename+'.csv', delim='auto')
thisExp.saveAsPickle(psypy_filename)
# make sure everything is closed down
if biopac_exists:
    biopac.close()  # Close the labjack U3 device to end communication with the Biopac MP150

logging.flush()
core.wait(5)
thisExp.abort()  # or data files will save again on exit
win.close()  # close the window
core.quit()

"""
End of Experiment
"""