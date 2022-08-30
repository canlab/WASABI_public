#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
###
# CANLab WASABI PsychoPy Utilities Beta 0.0.1


# Michael Sun
###

Troubleshooting Tips:
If you get window-related errors, make sure to downgrade pyglet to 1.4.1:
pip uninstall pyglet
pip install pyglet==1.4.1

0a. Import Libraries
"""

from __future__ import absolute_import, division

from psychopy import locale_setup
from psychopy import prefs
prefs.hardware['audioLib'] = ['PTB'] # Set a preferred audio library to PsychToolBox (best), so psychopy doesn't yell at you.
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


# Some good defaults
if not frameTolerance:
    frameTolerance = 0.001  # how close to onset before 'same' frame
if not start_msg:
    start_msg = 'Please wait. \nThe scan will begin shortly. \n Experimenter press [s] to continue.'
if not s_text:
    s_text='[s]-press confirmed.'
if not in_between_run_msg:
    in_between_run_msg = 'Thank you.\n Please wait for the next scan to start \n Experimenter press [e] to continue.'
if not end_msg:
    end_msg = 'Please wait for instructions from the experimenter'


# All functions should write to a key-value dictionary that will later be output as a bids_dataset
# at least write out onset, duration, and condition. All other key-value pairs can be written out elsewhere.


def subjectInfoBox(name, expInfo):
    """
    Show a dialog box asking for subject information with [OK] and [Cancel] buttons.
    name: String name of the dialog box being shown. e.g., "Instructions".
    str: String with the message you want shown, centered.
    expInfo: dictionary of keys, indicating the information you want to collect.

    returns expInfo: The resulting key-value dictionary for use in the rest of your study.
    """
    if expInfo=={}:
        expInfo = {
            'DBIC Number': '',
            'gender': '',
            'session': '',
            'handedness': '', 
            'scanner': ''
        }
    dlg = gui.DlgFromDict(title=name, dictionary=expInfo, sortKeys=False)

    if dlg.OK == False:
        core.quit()  # user pressed cancel

    expInfo['date'] = data.getDateStr()  # add a simple timestamp

    return expInfo


def setupWindow(res=[1920, 1080], bg=[-1,-1,-1], showMouse=False):
    """
    Requires an expInfo dictionary

    Sets up the window object that you will use to flip and display stimuli to your subject.
    res: [width, height] list of one's display resolution. Defaults to [1920, 1080] for full high-definition (FHD).
    bg: [r,g,b] list of the background color. Defaults to -1,-1,-1 for black.
    mouseVisible: Keeps the mouse invisible during the duration of the study.

    returns win: The resulting visual.Window object.
    """
    if debug == 1: 
        win = visual.Window(
                size=[1280, 720], fullscr=False, 
                screen=0,   # Change this to the appropriate display 
                winType='pyglet', allowGUI=True, allowStencil=False,
                monitor='testMonitor', color=bg, colorSpace='rgb',
                blendMode='avg', useFBO=True, 
                units='height')
    else: 
        win = visual.Window(
                size=res, fullscr=True, 
                screen=-1,   # Change this to the appropriate fMRI projector 
                winType='pyglet', allowGUI=True, allowStencil=False,
                monitor='testMonitor', color=bg, colorSpace='rgb',
                blendMode='avg', useFBO=True, 
                units='height')
    # store frame rate of monitor if we can measure it
    expInfo['frameRate'] = win.getActualFrameRate()
    if expInfo['frameRate'] != None:
        frameDur = 1.0 / round(expInfo['frameRate'])
    else:
        frameDur = 1.0 / 60.0  # could not measure, so guess

    win.mouseVisible = showMouse # Make the mouse invisible for the remainder of the experiment

    return win


def showText(name, str, fontSize=.05, t=5, advanceKey='space'):
    """
    Requires win

    Show some text, press a key to advance or wait t seconds. Returns nothing. You're responsible for your own word-wrapping!
    name: String name of the textblock being shown. e.g., "Instructions".
    str: String with the message you want shown, centered.
    fontSize: Defaults to a medium font size of .05. Font size in psychopy height.
    advanceKey: a string indicating the keyword for keyboard stroke to advance. e.g., 'space'
    """
    if name=="":
        name="TextDisplay"
    if str=="":
        str='Welcome to the scan\nPlease read the following instructions \nvery carefully.\n\n\n\nExperimenter press [Space] to continue.'

    # Initialize components for Routine "Text"
    TextClock = core.Clock()
    Text = visual.TextStim(win=win, name=name,
        text=str,
        font='Arial', wrapWidth=1.75,
        pos=(0, 0.0), units='height', height=fontSize, 
        color='white', colorSpace='rgb', opacity=1)  
    
    Text.draw()
    win.flip()
    continueRoutine=True
    while continueRoutine == True:
        if advanceKey in event.getKeys(keyList = advanceKey):
            continueRoutine = False
    return

def showText(name, str, fontSize=.05, t=5, advanceKey='space', biopacCode):
    """
    Requires win, biopac_exists, fmriStart

    Show some text, press a key to advance or wait t seconds. Returns nothing. You're responsible for your own word-wrapping!
    name: String name of the textblock being shown. e.g., "Instructions".
    str: String with the message you want shown, centered.
    fontSize: Defaults to a medium font size of .05. Font size in psychopy height.
    t: A numeric indicating how many seconds to leave the text on the screen. e.g., 5
    """
    if name=="":
        name="TextDisplay"
    if str=="":
        str='Welcome to the scan\nPlease read the following instructions \nvery carefully.\n\n\n\nExperimenter press [Space] to continue.'

    # Initialize components for Routine "Text"
    TextClock = core.Clock()
    Text = visual.TextStim(win=win, name=name,
        text=str,
        font='Arial', wrapWidth=1.75,
        pos=(0, 0.0), units='height', height=fontSize, 
        color='white', colorSpace='rgb', opacity=1)  
    
    Text.draw()
    if biopac_exists:
        biopac.setData(biopac, 0)
        biopac.setData(biopac, biopacCode)
        onset = globalClock.getTime() - fmriStart
    win.flip()
    continueRoutine=True
    timer = core.CountdownTimer()
    timer.add(t)   
    while continueRoutine == True or timer.getTime() > 0:
        if advanceKey in event.getKeys(keyList = advanceKey):
            continueRoutine = False
        else:
            continue
    
    routineTimer.reset()
    return (onset, globalClock.getTime() - fmriStart - onset, None, bodySites[runs], temperature, InstructionCondition, None) # a list to extend the trialdata, 


def showImg(name, imgPath, position=[0,0]):
    return

def showFixation(name, ['big', 'small'], size=0.05, pos=(0, 0), col='white', t=5, biopacCode):
    """
    Requires win, 
    
    Create a fixation cross period, set the position, size, color, and time to offset.


    """
    showText('+')

    # Initialize components for Routine "Fixation"
    FixationClock = core.Clock()
    fixation = visual.TextStim(win=win, name='fixation',
        text='+',
        font='Arial',
        pos=(0, 0), height=size, wrapWidth=None, ori=0, 
        color=col, colorSpace='rgb', opacity=1, 
        languageStyle='LTR',
        depth=-2.0)

    # ------Prepare to start Routine "Fixation"-------
    continueRoutine = True
    routineTimer.add(time)
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
            # if biopac_exists:
            #     win.callOnFlip(biopac.setData, biopac, 0)
            #     win.callOnFlip(biopac.setData, biopac, medmap_fixation)
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

    bids_trial = []
    bids_trial.extend((onset, t, ConditionName))

    return bids_trial

def showTextAndImg(textname, str, strcolor='white', fontSize=.05, strpos=(0, .5), imgname, imgPath, imgsize=(.40,.40), imgpos=(0, .2), biopacCode, advanceKey=['space']):
    """
    Requires: win, routineTimer, thisSimKey, autorespond, endExpNow, defaultKeyboard, thisExp, biopac_exists, biopac
    
    
    """

    ## Intialize the Objects
    TextImageClock = core.Clock()
    TextImageKB = keyboard.Keyboard()
    Text = visual.TextStim(win, name='Text', 
        text=textname,
        font = 'Arial',
        pos=strpos, height=fontSize, wrapWidth=1.6, ori=0, 
        color=strcolor, colorSpace='rgb', opacity=1, 
        languageStyle='LTR',
        depth=0.0, 
        anchorHoriz='center')
    Img = visual.ImageStim(
        win=win,
        name=imgname,
        image=imgPath,
        mask=None,
        ori=0, 
        pos=imgpos, 
        size=imgsize,
        color=[1,1,1], colorSpace='rgb', opacity=1,
        flipHoriz=False, flipVert=False,
        texRes=512, interpolate=True, depth=0.0)
    ##
    
    # ------Prepare to start Routine "TextImage"-------
    routineTimer.reset()

    continueRoutine = True
    # update component parameters for each repeat
    TextImageKB.keys = []
    TextImageKB.rt = []
    _TextImageKB_allKeys = []
    # Update instructions and cues based on current run's body-sites:
  
    # keep track of which components have finished
    TextImageComponents = [Text, Img, TextImageKB]

    for thisComponent in TextImageComponents:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    TextImageClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    frameN = -1

    # -------Run Routine "TextImageClock"-------
    while continueRoutine:
        # get current time
        t = TextImageClock.getTime()
        tThisFlip = win.getFutureFlipTime(clock=TextImageClock)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *Text* updates
        if Text.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            Text.frameNStart = frameN  # exact frame index
            Text.tStart = t  # local t and not account for scr refresh
            Text.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(Text, 'tStartRefresh')  # time at next scr refresh
            Text.setAutoDraw(True)

        # *BodySiteImg* updates
        if Img.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            Img.frameNStart = frameN  # exact frame index
            Img.tStart = t  # local t and not account for scr refresh
            Img.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(Img, 'tStartRefresh')  # time at next scr refresh
            Img.setAutoDraw(True)
        
        # *BodySiteInstructionRead* updates
        waitOnFlip = False
        if TextImageKB.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            TextImageKB.frameNStart = frameN  # exact frame index
            TextImageKB.tStart = t  # local t and not account for scr refresh
            TextImageKB.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(TextImageKB, 'tStartRefresh')  # time at next scr refresh
            TextImageKB.status = STARTED
            # keyboard checking is just starting
            waitOnFlip = True
            win.callOnFlip(print, "Cueing Off All Biopac Channels")            
            win.callOnFlip(print, "Showing BodySite Instructions")
            win.callOnFlip(print, "Cueing Biopac Channel: " + str(biopacCode))
            if biopac_exists == 1:
                win.callOnFlip(biopac.setData, biopac, 0)
                win.callOnFlip(biopac.setData, biopac, biopacCode)
            win.callOnFlip(TextImageKB.clock.reset)  # t=0 on next screen flip
            win.callOnFlip(TextImageKB.clearEvents, eventType='keyboard')  # clear events on next screen flip
        if TextImageKB.status == STARTED and not waitOnFlip:
            theseKeys = TextImageKB.getKeys(keyList=advanceKey, waitRelease=False)
            _TextImageKB_allKeys.extend(theseKeys)
            if len(_TextImageKB_allKeys):
                TextImageKB.keys = _TextImageKB_allKeys[-1].name  # just the last key pressed
                TextImageKB.rt = _TextImageKB_allKeys[-1].rt
                # a response ends the routine
                continueRoutine = False
        
        # Autoresponder
        if t >= thisSimKey.rt and autorespond == 1:
            _TextImageKB_allKeys.extend([thisSimKey]) 

        # check for quit (typically the Esc key)
        if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
            core.quit()
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in TextImageComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()

    # -------Ending Routine "TextImage"-------
    print("CueOff Channel: " + str(biopacCode))
    if biopac_exists == 1:
        biopac.setData(biopac, 0)
    for thisComponent in TextImageComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    thisExp.addData(textname+'.started', Text.tStartRefresh)
    thisExp.addData(imgname+'.started', Img.tStartRefresh)
    thisExp.addData(imgname+'.stopped', Img.tStopRefresh)
    # check responses
    if TextImageKB.keys in ['', [], None]:  # No response was made
        TextImageKB.keys = None
    thisExp.addData(textname+'.keys',TextImageKB.keys)
    if TextImageKB.keys != None:  # we had a response
        thisExp.addData(textname+'.rt', TextImageKB.rt)
    thisExp.addData(textname+'.started', TextImageKB.tStartRefresh)
    thisExp.addData(textname+'.stopped', TextImageKB.tStopRefresh)
    # the Routine "TextImage" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()

    return

def confirmRunStart(TR=0.46):
    """
    Requires win, globalClock, autorespond, 
    Show some text, listen for TRs and return the time the run starts.


    return the fmriStart time in seconds.
    """
    
    start = visual.TextStim(win, text=start_msg, height=.05, color=win.rgb + 0.5)
    start.draw()  # Automatically draw every frame
    win.flip()
    fmriStart = globalClock.getTime()   # Start the clock
    if autorespond != 1:   
        continueRoutine = True
        event.clearEvents()
        while continueRoutine == True:
            if 's' in event.getKeys(keyList = 's'):         # experimenter start key - safe key before fMRI trigger
                s_confirm = visual.TextStim(win, text=s_text, height =.05, color="green", pos=(0.0, -.3))
                start.draw()
                s_confirm.draw()
                win.flip()
                event.clearEvents()
                while continueRoutine == True:
                    if '5' in event.getKeys(keyList = '5'): # fMRI trigger
                        fmriStart = globalClock.getTime()   # Start the clock
                        timer = core.CountdownTimer()       # Wait 6 TRs, Dummy Scans
                        timer.add(TR*6)
                        while timer.getTime() > 0:
                            continue
                        continueRoutine = False
    return fmriStart


def endScan():
    return

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

def showUnipolarScale(name, questionText, imgPath, ratingTime=5):
    """_summary_

    Args:
        name (string): _description_
        questionText (string): _description_
        imgPath (string): _description_
        ratingTime (int, optional): _description_. Defaults to 5 seconds.
    """
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

    medmap_bids_trial = []
    medmap_bids_trial.extend((onset, globalClock.getTime() - fmriStart - onset, sliderValue, bodySites[runs], temperature, 'Intensity Rating', None))
    medmap_bids.append(medmap_bids_trial)

    # the Routine "IntensityRating" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()

    return

def showBipolarScale(name, questionText, imgPath, ratingTime=5):
    # Initialize components for Routine "ComfortRating"
    ComfortText = "How comfortable do you feel right now?" # (Bipolar)
    ComfortRatingClock = core.Clock()
    ComfortMouse = event.Mouse(win=win, visible=False)
    ComfortMouse.mouseClock = core.Clock()
    ComfortRating = visual.Rect(win, height=ratingScaleHeight, width=abs(sliderMin), pos= [sliderMin/2, -.1], fillColor='red', lineColor='black')
    ComfortBlackTriangle = visual.ShapeStim(
        win, 
        vertices=bipolar_verts,
        fillColor='black', lineColor='black')
    ComfortAnchors = visual.ImageStim(
        win=win,
        image= os.sep.join([stimuli_dir,"ratingscale","ComfortScale.png"]),
        name='ComfortAnchors', 
        mask=None,
        ori=0, pos=(0, -0.09), size=(1.5, .4),
        color=[1,1,1], colorSpace='rgb', opacity=1,
        flipHoriz=False, flipVert=False,
        texRes=512, interpolate=True, depth=0.0)
    ComfortPrompt = visual.TextStim(win, name='ComfortPrompt', 
        text=ComfortText,
        font = 'Arial',
        pos=(0, 0.3), height=0.05, wrapWidth=None, ori=0, 
        color='white', colorSpace='rgb', opacity=1, 
        languageStyle='LTR',
        depth=0.0,
        anchorHoriz='center')

     # -------Run Routine "ComfortRating"-------
    while continueRoutine:
        # get current time
        t = ComfortRatingClock.getTime()
        tThisFlip = win.getFutureFlipTime(clock=ComfortRatingClock)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame

        timeNow = globalClock.getTime()
        if (timeNow - timeAtLastInterval) > TIME_INTERVAL:
            mouseRel=ComfortMouse.getRel()
            mouseX=oldMouseX + mouseRel[0]
        ComfortRating.pos = (mouseX/2,0)
        ComfortRating.width = abs(mouseX)
        if mouseX > sliderMax:
            mouseX = sliderMax
        if mouseX < sliderMin:
            mouseX = sliderMin
        timeAtLastInterval = timeNow
        oldMouseX=mouseX
        sliderValue = ((mouseX - sliderMin) / (sliderMax - sliderMin) * 200)-100

        # *ComfortMouse* updates
        if ComfortMouse.status == NOT_STARTED and t >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            ComfortMouse.frameNStart = frameN  # exact frame index
            ComfortMouse.tStart = t  # local t and not account for scr refresh
            ComfortMouse.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(ComfortMouse, 'tStartRefresh')  # time at next scr refresh
            ComfortMouse.status = STARTED
            ComfortMouse.mouseClock.reset()
            prevButtonState = ComfortMouse.getPressed()  # if button is down already this ISN'T a new click
        if ComfortMouse.status == STARTED:  # only update if started and not finished!
            if tThisFlipGlobal > ComfortMouse.tStartRefresh + ratingTime-frameTolerance:
                # keep track of stop time/frame for later
                ComfortMouse.tStop = t  # not accounting for scr refresh
                ComfortMouse.frameNStop = frameN  # exact frame index
                ComfortMouse.status = FINISHED
            buttons = ComfortMouse.getPressed()
            if buttons != prevButtonState:  # button state changed?
                prevButtonState = buttons
                if sum(buttons) > 0:  # state changed to a new click
                    # abort routine on response
                    continueRoutine = False

        # *ComfortRating* updates
        if ComfortRating.status == NOT_STARTED and t >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            ComfortRating.frameNStart = frameN  # exact frame index
            ComfortRating.tStart = t  # local t and not account for scr refresh
            ComfortRating.tStartRefresh = tThisFlipGlobal  # on global time
            win.callOnFlip(print, "Show Comfort Rating")
            if biopac_exists == 1:
                win.callOnFlip(biopac.setData, biopac, 0)
                win.callOnFlip(biopac.setData, biopac, comfort_rating)
            win.timeOnFlip(ComfortRating, 'tStartRefresh')  # time at next scr refresh
            ComfortRating.setAutoDraw(True)
        if ComfortRating.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > ComfortRating.tStartRefresh + ratingTime-frameTolerance:
                # keep track of stop time/frame for later
                ComfortRating.tStop = t  # not accounting for scr refresh
                ComfortRating.frameNStop = frameN  # exact frame index
                win.timeOnFlip(ComfortRating, 'tStopRefresh')  # time at next scr refresh
                ComfortRating.setAutoDraw(False)
        
        # *ComfortBlackTriangle* updates
        if ComfortBlackTriangle.status == NOT_STARTED and t >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            ComfortBlackTriangle.frameNStart = frameN  # exact frame index
            ComfortBlackTriangle.tStart = t  # local t and not account for scr refresh
            ComfortBlackTriangle.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(ComfortBlackTriangle, 'tStartRefresh')  # time at next scr refresh
            ComfortBlackTriangle.setAutoDraw(True)
        if ComfortBlackTriangle.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > ComfortBlackTriangle.tStartRefresh + ratingTime-frameTolerance:
                # keep track of stop time/frame for later
                ComfortBlackTriangle.tStop = t  # not accounting for scr refresh
                ComfortBlackTriangle.frameNStop = frameN  # exact frame index
                win.timeOnFlip(ComfortBlackTriangle, 'tStopRefresh')  # time at next scr refresh
                ComfortBlackTriangle.setAutoDraw(False)

        # *ComfortAnchors* updates
        if ComfortAnchors.status == NOT_STARTED and t >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            ComfortAnchors.frameNStart = frameN  # exact frame index
            ComfortAnchors.tStart = t  # local t and not account for scr refresh
            ComfortAnchors.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(ComfortAnchors, 'tStartRefresh')  # time at next scr refresh
            ComfortAnchors.setAutoDraw(True)
        if ComfortAnchors.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > ComfortAnchors.tStartRefresh + ratingTime-frameTolerance:
                # keep track of stop time/frame for later
                ComfortAnchors.tStop = t  # not accounting for scr refresh
                ComfortAnchors.frameNStop = frameN  # exact frame index
                win.timeOnFlip(ComfortAnchors, 'tStopRefresh')  # time at next scr refresh
                ComfortAnchors.setAutoDraw(False)
        
        # *ComfortPrompt* updates
        if ComfortPrompt.status == NOT_STARTED and t >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            ComfortPrompt.frameNStart = frameN  # exact frame index
            ComfortPrompt.tStart = t  # local t and not account for scr refresh
            ComfortPrompt.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(ComfortPrompt, 'tStartRefresh')  # time at next scr refresh
            ComfortPrompt.setAutoDraw(True)
        if ComfortPrompt.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > ComfortPrompt.tStartRefresh + ratingTime-frameTolerance:
                # keep track of stop time/frame for later
                ComfortPrompt.tStop = t  # not accounting for scr refresh
                ComfortPrompt.frameNStop = frameN  # exact frame index
                win.timeOnFlip(ComfortPrompt, 'tStopRefresh')  # time at next scr refresh
                ComfortPrompt.setAutoDraw(False)
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
        for thisComponent in ComfortRatingComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()

    # -------Ending Routine "ComfortRating"-------
    print("CueOff Channel " + str(comfort_rating))
    for thisComponent in ComfortRatingComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    # store data for thisExp (ExperimentHandler)
    thisExp.addData('ComfortRating.response', sliderValue)
    thisExp.addData('ComfortRating.rt', timeNow - ComfortRating.tStart)
    thisExp.nextEntry()
    thisExp.addData('ComfortRating.started', ComfortRating.tStart)
    thisExp.addData('ComfortRating.stopped', ComfortRating.tStop)
    medmap_bids.append(["Comfort Rating:", sliderValue])
    # the Routine "ComfortRating" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()   

    return

def showBinaryScale(name, prompt, timelimit, biopacCode):
    """
    Show a Binary Scale e.g., Yes-No. Collect data with mouseclick.


    """
    
    # Initialize components for Routine "Binary"
    BinaryClock = core.Clock()
    Binary = visual.Rect(win, height=ratingScaleHeight, width=0, pos= [0, 0], fillColor='red', lineColor='black')
    Mouse = event.Mouse(win=win)
    Mouse.mouseClock = core.Clock()
    Anchors = visual.ImageStim(
        win=win,
        image= os.sep.join([stimuli_dir,"ratingscale","YesNo.png"]),
        name='BinaryAnchors', 
        mask=None,
        ori=0, pos=(0, 0), size=(1, .25),
        color=[1,1,1], colorSpace='rgb', opacity=1,
        flipHoriz=False, flipVert=False,
        texRes=512, interpolate=True, depth=0.0)
    Prompt = visual.TextStim(win, name=name, 
        text=prompt,
        font = 'Arial',
        pos=(0, 0.3), height=0.05, wrapWidth=None, ori=0, 
        color='white', colorSpace='rgb', opacity=1, 
        languageStyle='LTR',
        depth=0.0,
        anchorHoriz='center')

        ############ ASK BINARY Question #######################################
        # ------Prepare to start Routine "Binary"-------
        continueRoutine = True
        routineTimer.add(timelimit)
        # update component parameters for each repeat
        # setup some python lists for storing info about the mouse
        
        Mouse = event.Mouse(win=win, visible=False) # Re-initialize Mouse
        Mouse.setPos((0,0))
        timeAtLastInterval = 0
        mouseX = 0
        oldMouseX = 0
        Binary.width = 0
        Binary.pos = (0,0)
        
        # keep track of which components have finished
        BinaryComponents = [Mouse, Binary, Anchors, Prompt]
        for thisComponent in BinaryComponents:
            thisComponent.tStart = None
            thisComponent.tStop = None
            thisComponent.tStartRefresh = None
            thisComponent.tStopRefresh = None
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        # reset timers
        t = 0
        _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        BinaryClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
        frameN = -1

        # -------Run Routine "Binary"-------
        onset = globalClock.getTime() - fmriStart           # Record onset time of the trial
        while continueRoutine:
            # get current time
            t = BinaryClock.getTime()
            tThisFlip = win.getFutureFlipTime(clock=BinaryClock)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame

            timeNow = globalClock.getTime()
            if (timeNow - timeAtLastInterval) > TIME_INTERVAL:
                mouseRel=Mouse.getRel()
                mouseX=oldMouseX + mouseRel[0]
            
            if mouseX==0:
                Binary.width = 0
            else:
                if mouseX>0:
                    Binary.pos = (.28,0)
                    sliderValue=1
                elif mouseX<0:
                    Binary.pos = (-.4,0)
                    sliderValue=-1
                Binary.width = .5

            timeAtLastInterval = timeNow
            oldMouseX=mouseX

            # *Mouse* updates
            if Mouse.status == NOT_STARTED and t >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                Mouse.frameNStart = frameN  # exact frame index
                Mouse.tStart = t  # local t and not account for scr refresh
                Mouse.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(Mouse, 'tStartRefresh')  # time at next scr refresh
                Mouse.status = STARTED
                Mouse.mouseClock.reset()
                prevButtonState = Mouse.getPressed()  # if button is down already this ISN'T a new click
            if Mouse.status == STARTED:  # only update if started and not finished!
                if tThisFlipGlobal > Mouse.tStartRefresh + ratingTime-frameTolerance:
                    # keep track of stop time/frame for later
                    Mouse.tStop = t  # not accounting for scr refresh
                    Mouse.frameNStop = frameN  # exact frame index
                    Mouse.status = FINISHED
                buttons = Mouse.getPressed()
                if buttons != prevButtonState:  # button state changed?
                    prevButtonState = buttons
                    if sum(buttons) > 0:  # state changed to a new click
                        # abort routine on response
                        continueRoutine = False

            # *Binary* updates
            if Binary.status == NOT_STARTED and t >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                Binary.frameNStart = frameN  # exact frame index
                Binary.tStart = t  # local t and not account for scr refresh
                Binary.tStartRefresh = tThisFlipGlobal  # on global time
                win.callOnFlip(print, "Show "+name+" Rating")
                if biopac_exists == 1:
                    win.callOnFlip(biopac.setData, biopac, 0)
                    win.callOnFlip(biopac.setData, biopac, biopacCode)
                win.timeOnFlip(Binary, 'tStartRefresh')  # time at next scr refresh
                Binary.setAutoDraw(True)
            if Binary.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > Binary.tStartRefresh + ratingTime-frameTolerance:
                    # keep track of stop time/frame for later
                    Binary.tStop = t  # not accounting for scr refresh
                    Binary.frameNStop = frameN  # exact frame index
                    win.timeOnFlip(Binary, 'tStopRefresh')  # time at next scr refresh
                    Binary.setAutoDraw(False)
            
            # *Anchors* updates
            if Anchors.status == NOT_STARTED and t >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                Anchors.frameNStart = frameN  # exact frame index
                Anchors.tStart = t  # local t and not account for scr refresh
                Anchors.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(Anchors, 'tStartRefresh')  # time at next scr refresh
                Anchors.setAutoDraw(True)
            if Anchors.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > Anchors.tStartRefresh + ratingTime-frameTolerance:
                    # keep track of stop time/frame for later
                    Anchors.tStop = t  # not accounting for scr refresh
                    Anchors.frameNStop = frameN  # exact frame index
                    win.timeOnFlip(Anchors, 'tStopRefresh')  # time at next scr refresh
                    Anchors.setAutoDraw(False)

            # *Prompt* updates
            if Prompt.status == NOT_STARTED and t >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                Prompt.frameNStart = frameN  # exact frame index
                Prompt.tStart = t  # local t and not account for scr refresh
                Prompt.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(Prompt, 'tStartRefresh')  # time at next scr refresh
                Prompt.setAutoDraw(True)
            if Prompt.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > Prompt.tStartRefresh + ratingTime-frameTolerance:
                    # keep track of stop time/frame for later
                    Prompt.tStop = t  # not accounting for scr refresh
                    Prompt.frameNStop = frameN  # exact frame index
                    win.timeOnFlip(Prompt, 'tStopRefresh')  # time at next scr refresh
                    Prompt.setAutoDraw(False)

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
            for thisComponent in BinaryComponents:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished
            
            # refresh the screen
            if continueRoutine:
                win.flip()

        # -------Ending Routine "Binary"-------
        print("CueOff Channel " + str(_binary))
        for thisComponent in BinaryComponents:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        # store data for thisExp (ExperimentHandler)
        thisExp.addData('Binary.response', sliderValue)
        thisExp.addData('Binary.rt', timeNow-Binary.tStart)
        thisExp.nextEntry()
        thisExp.addData('Binary.started', Binary.tStart)
        thisExp.addData('Binary.stopped', Binary.tStop)
        Rating=sliderValue

        medmap_bids_trial = []
        medmap_bids_trial.extend((onset, globalClock.getTime() - fmriStart - onset, Rating, bodySites[runs], temperature, ' Rating', jitter2))
        medmap_bids.append(medmap_bids_trial)

        # the Routine "Binary" was not non-slip safe, so reset the non-slip timer
        routineTimer.reset()


    return


