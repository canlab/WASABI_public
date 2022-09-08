#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This experiment was created using PsychoPy3 Experiment Builder (v2020.2.10),
    on January 28, 2021, at 23:04
If you publish work using this script the most relevant publication is:

    Peirce J, Gray JR, Simpson S, MacAskill M, Höchenberger R, Sogo H, Kastman E, Lindeløv JK. (2019) 
        PsychoPy2: Experiments in behavior made easy Behav Res 51: 195. 
        https://doi.org/10.3758/s13428-018-01193-y
        
Some measures have been taken to minimize experimental latency. PTB/Psychopy style is used to initialize all objects prior to screen flipping as much as possible.
    
Data is written in BIDS 1.4.1 format, as separate tab-separated-value (.tsv) files for each run per subject, (UTF-8 encoding). 
Following this format:
all data headers are in lower snake_case.

The paradigm will generate these files of name:
1x sub-SIDXXXXXX_ses-XX_task-distractmap-Practice0back_acq-turn-X_events.tsv
1x sub-SIDXXXXXX_ses-XX_task-distractmap-Practice0back_acq-turn-X_events.tsv

with the following headers:
'SID', 'date', 'gender', 'session', 'scanner', 'onset', 'duration', 'condition', 'rt'	'mouseclick'	'correct'	'condition'	'score' 'biopac_channel'

SID: DBIC Subject ID
day: First or second day of Distract Maps
gender
session
scanner: Initials of the scan operator of the day. 
onset: seconds
duration: seconds
rt: seconds
mouseclick: 
    0: left click, 1: middle click, 2: right click
correct:
    0: False, 1: True
condition: string
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

"""
2. Start Experimental Dialog Boxes
"""
# Upload participant file: Browse for file
# Store info about the experiment session
psychopyVersion = '2020.2.10'
if debug == 1:
    expInfo = {
    'DBIC Number': '99',
    'gender': 'm',
    'session': '99'
    }
else:
    expInfo = {
    'DBIC Number': '', 
    'gender': '',
    'session': ''
    }
    subjectInfoBox("NbackMap Practice", expInfo)

expInfo['date'] = data.getDateStr()  # add a simple timestamp
expInfo['psychopyVersion'] = psychopyVersion
expName = 'distractmap-Practice'
expInfo['expName'] = expName

""" 
3. Setup the Window
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
4. Prepare files to write
"""
sub_dir = os.path.join(_thisDir, 'data', 'sub-SID%06d' % (int(expInfo['DBIC Number'])), 'ses-%02d' % (int(expInfo['session'])))
if not os.path.exists(sub_dir):
    os.makedirs(sub_dir)
varNames=['SID', 'date', 'gender', 'session', 'onset', 'duration', 'condition', 'rt',	'mouseclick',	'correct',	'condition',	'score', 'biopac_channel']
Practice_0back_bids=pd.DataFrame(columns=varNames)
Practice_2back_bids=pd.DataFrame(columns=varNames)

"""
5. Initialize Custom Components
"""
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

continueText = visual.TextStim(win=win, name='continueText',
    text='Experimenter press [Space] to continue.',
    font='Arial',
    pos=(0, -.35), units='height', height=0.05, 
    color='white', colorSpace='rgb', opacity=1)

"""
6. Welcome Instructions
"""
NbackInstructionText1 = "Welcome to the n-back task \n\n\nPlease read the following instructions \nvery carefully.\n\n\n\nExperimenter press [Space] to continue."
NbackInstructionText2 = "During the task you will be presented a white square in one of nine positions on a grid. \n\n\n\n\n\n\n\nDepending on the instruction, your task is to indicate whether the \nyou see a square anywhere on the grid, or if the square's current position is the same as the position two trials ago\n\n\nPress [Space] to continue."
NbackInstructionText3 = "Between each trial, a fixation cross will appear in the middle of the grid. \n\n\n\n\n\n\n\n\nYou do not need to respond during this time. \nSimply wait for the next trial.\n\n\n\nPress [Space] to continue."
NbackInstructionText4 = "\n0-back\n\n\nWhen given the instruction '0-back' you will have to indicate whether a square appears anywhere on the grid by pressing the \"yes\" button (left click). \n\n\nPress [Space] to continue."

NbackInstructions.setText(NbackInstructionText1)
NbackInstructions.draw()
win.flip()

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
event.waitKeys(keyList = 'space')

NbackInstructionImg.setAutoDraw(False)
NbackInstructions.setText(NbackInstructionText4)
NbackInstructions.draw()

win.flip()
event.waitKeys(keyList = 'space')

routineTimer.reset()

"""
8. Start Practice 0-back
"""
turns = 1
score = 0
Nback0 = os.sep.join([nback_dir, "Practice_N-back-0.xlsx"])

if debug==1:
    turnLimit=1
else:
    turnLimit = 3

while turns <= turnLimit and score <= 70:
    ## 0-back Instructions
    NbackInstructionText5 = "When the screen says '0-back' you should make a \"yes\" response every time the square appears on the screen."
    ClickToContinueText = "Click to continue"
    NbackInstructionText6 = "First, we will practice some trials so that you can get used to the procedure.\nAfter each response you'll see whether you responded correctly, incorrectly, or whether you forgot to respond.\n\n\n\n\nGood Luck!"
    ClickToStartText = "Click to start practice"

    NbackInstructions.setText(NbackInstructionText5)
    NbackInstructions.setAutoDraw(True)
    ClickPrompt.setText(ClickToContinueText)
    mouse = event.Mouse(win=win, visible=False)
    prevButtonState = mouse.getPressed()  # if button is down already this ISN'T a new click
    buttons = prevButtonState
    win.flip()

    while(mouse.getPressed()[0] != 1):
        ClickPrompt.setText(ClickToStartText)
        ClickPrompt.setAutoDraw(True)
        win.flip()

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
    win.flip()
    routineTimer.reset()

    ########################
    # Practice 0-back Begins
    ########################
    """
    9. Save Practice-0back File
    """
    # each _%s refers to the respective field in the parentheses
    Practice_0back_bids_name = sub_dir + os.sep + u'sub-SID%06d_ses-%02d_task-%s_acq-%s_events.tsv' % (int(expInfo['DBIC Number']), int(expInfo['session']), expName+"0back", "turn-"+str(turns))
    Practice_0back = nback(win, "Practice 0-back", answers=Nback0, cheat=cheat, feedback=True, nofMRI=True)
    Practice_0back['SID']=expInfo['DBIC Number']
    Practice_0back['date']=expInfo['date']
    Practice_0back['gender']=expInfo['gender']
    Practice_0back['session']=expInfo['session']
    Practice_0back.to_csv(Practice_0back_bids_name, sep="\t")
    score = Practice_0back['score'].iloc[-2]
    turns = turns + 1

while turns > turnLimit and score <= 70:
    PleaseWaitText = "Please wait for the experimenter ..."
    showText(win, "TurnLimitReached", text=PleaseWaitText, advanceKey='space', noRecord=True)
    Practice_0back = nback(win, "Practice 0-back", answers=Nback0, cheat=cheat, feedback=True, nofMRI=True)
    Practice_0back_bids_name = sub_dir + os.sep + u'sub-SID%06d_ses-%02d_task-%s_acq-%s_events.tsv' % (int(expInfo['DBIC Number']), int(expInfo['session']), expName+"0back", "turn-"+str(turns))
    Practice_0back['SID']=expInfo['DBIC Number']
    Practice_0back['date']=expInfo['date']
    Practice_0back['gender']=expInfo['gender']
    Practice_0back.to_csv(Practice_0back_bids_name, sep="\t")
    score = Practice_0back['score'].iloc[-2]
    turns = turns+1

"""
10. Start Practice 2-back
"""
turns = 1
score = 0
Nback2 = os.sep.join([nback_dir, "Practice_N-back-2.xlsx"])
while turns <= turnLimit and score <= 70:
    # ------Prepare to start Routine "Instructions_2"-------
    NbackInstructionText8 = "2-back\n\n\nYou will have to indicate whether the current position matches the position that was presented two trials ago, by either pressing the \"yes\" button (left click) or the \"no\" button (right click).\n\n\nExperimenter press [Space] to see an example."

    NbackInstructions.setText(NbackInstructionText8)
    NbackInstructions.draw()
    win.flip()
    continueRoutine = True
    event.clearEvents()
    while continueRoutine == True:
        if 'space' in event.getKeys(keyList = 'space'):
            continueRoutine = False
    routineTimer.reset()

    NbackInstructionText9 = "In this example you should not respond to the first trial or the second trial (as there are insufficient previous trials), and make a \"yes\" response (left click) on trial 3, since the position is the same as the position on trial 1.\n\n\n\n\n\n\n\n\n\n"
    ClickToContinueText = "Click to continue"

    NbackInstructionText10 = "You should make a \"no\" response (right click) on trial 3, if the position was NOT the same as the position on trial 1.\n\n\n\n\n\n\n\n\n\n"

    NbackInstructionText11 = "Now, we will practice some trials so that you can get used to the procedure.\nAfter each response you'll see whether your response was correct, incorrect, or whether you forgot to respond.\n\n\n\n\n\n\n\n\n\nGood Luck!"
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

    NbackInstructions.setText(NbackInstructionText11)
    NbackInstructions.setAutoDraw(True)
    win.flip()
    mouse = event.Mouse(win=win, visible=False)
    while(mouse.getPressed()[0] != 1):
        ClickPrompt.setText(ClickToStartText)
        ClickPrompt.setAutoDraw(True)
        win.flip()

    # Wipe the screen
    ClickPrompt.setAutoDraw(False)
    NbackInstructions.setAutoDraw(False)
    NbackInstructionWideImg.setAutoDraw(False)
    win.flip()
    routineTimer.reset()

    ########################
    # Practice 2-back Begins
    ########################
    """
    9. Start Practice-2back and Save File
    """
    # each _%s refers to the respective field in the parentheses
    Practice_2back_bids_name = sub_dir + os.sep + u'sub-SID%06d_ses-%02d_task-%s_acq-%s_events.tsv' % (int(expInfo['DBIC Number']), int(expInfo['session']), expName+"2back", "turn-"+str(turns))
    Practice_2back = nback(win, "Practice 2-back", answers=Nback2, feedback=True, cheat=cheat, nofMRI=True)
    Practice_2back['SID']=expInfo['DBIC Number']
    Practice_2back['date']=expInfo['date']
    Practice_2back['gender']=expInfo['gender']
    Practice_2back['session']=expInfo['session']
    Practice_2back.to_csv(Practice_2back_bids_name, sep="\t")

    score = Practice_2back['score'].iloc[-2]
    turns = turns + 1

while turns > turnLimit and score <= 70:
    PleaseWaitText = "Your score was " + str(score) + "\n\n\nPlease wait for the experimenter ..."
    showText(win, "TurnLimitReached", text=PleaseWaitText, advanceKey='space', noRecord=True)
    Practice_2back_bids_name = sub_dir + os.sep + u'sub-SID%06d_ses-%02d_task-%s_acq-%s_events.tsv' % (int(expInfo['DBIC Number']), int(expInfo['session']), expName+"2back", "turn-"+str(turns))
    Practice_2back = nback(win, "Practice 0-back", answers=Nback2, feedback=True, cheat=cheat, nofMRI=True)
    Practice_2back['SID']=expInfo['DBIC Number']
    Practice_2back['date']=expInfo['date']
    Practice_2back['gender']=expInfo['gender']
    Practice_2back['session']=expInfo['session']
    Practice_2back['handedness']=expInfo['handedness'] 
    Practice_2back['scanner']=expInfo['scanner']
    
    Practice_2back.to_csv(Practice_2back_bids_name, sep="\t")
    score = Practice_2back['score'].iloc[-2]
    turns = turns + 1

message = visual.TextStim(win, text=end_msg, height=0.05, units='height')
message.draw()
win.close()  # close the window
core.quit()

"""
End of Experiment
"""