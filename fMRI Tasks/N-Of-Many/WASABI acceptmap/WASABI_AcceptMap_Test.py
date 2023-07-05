#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This experiment was created using PsychoPy3 Experiment Builder (v2020.2.10),
    on January 28, 2021, at 23:04
If you publish work using this script the most relevant publication is:

    Peirce J, Gray JR, Simpson S, MacAskill M, Höchenberger R, Sogo H, Kastman E, Lindeløv JK. (2019) 
        PsychoPy2: Experiments in behavior made easy Behav Res 51: 195. 
        https://doi.org/10.3758/s13428-018-01193-y
        
This paradigm was developed to test the addition of expectancy and intensity questions to the Acceptmap for the N-of-Many paradigm. An adjustment that differs from the N-of-Few Acceptmap paradigm, and 
proposed as a way to match the N-of-Many Distractmap paradigm.

Physiological data is acquired with a Biopac MP150 Physiological data acquisition device via LabJack U3.

Some measures have been taken to minimize experimental latency. PTB/Psychopy style is used to initialize all objects prior to screen flipping as much as possible.
    
Data is written in BIDS 1.4.1 format, as separate tab-separated-value (.tsv) files for each run per subject, (UTF-8 encoding). 
Following this format:
all data headers are in lower snake_case.

This paradigm is run as 2 parts of an AcceptanceMap paradigm for 2 body sites: Right and Left Face. 

This paradigm is a simple instruction: either to simply experience or to follow regulation instructions that come from a prior training, 
which is followed by a repeating series of fixation crosses will coincide with a hot stimulation, followed by an intensity rating.
Following a set number of trials, the subject will be asked a series of questions regarding the run.

One session will consist of 4 total runs. Each run will feature 16 heat trials at 49 degrees C. 

As a consequence, in one day, correct running of these paradigms will generate 4x files of the names:
sub-XXXXX_ses-XX_task-acceptmapTEST-_acq-XXXX_run-X_events.tsv

Each file will consist of the following headers:
'SID', 'date', 'sex', 'session', 'handedness', 'scanner', 'onset', 'duration', 'temperature', 'body_site', 'skin_site', 'condition', 'rt', 'condition',	'biopac_channel'

SID: DBIC Subject ID
date: the mm/dd/yyyy date
sex
session
handedness
scanner: Initials of the scan operator of the day. 
onset: seconds
duration: seconds
temperature
body_site
condition: string
rt: seconds
biopac_channel

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
__version__ = "1.0.0"
__email__ = "msun@dartmouth.edu"
__status__ = "Production"

"""
1. Experimental Parameters
Clocks, paths, etc.
"""
# Paths
# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)
main_dir = _thisDir
stimuli_dir = main_dir + os.sep + "stimuli"

"""
2. Start Experimental Dialog Boxes
"""
psychopyVersion = '2020.2.10'

if debug == 1:
    expInfo = {
    'DBIC Number': '99',
    'dob (mm/dd/yyyy)': '06/20/1988',
    'sex': 'm',
    'session': '99',
    'handedness': 'r', 
    'scanner': 'MS',
    'run': 1,
    'body sites': ''
    }
else:
    expInfo = {
    'DBIC Number': '',
    'dob (mm/dd/yyyy)': '', 
    'sex': '',
    'session': '',
    'handedness': '', 
    'scanner': '',
    'run': 1,
    'body sites': ''
    }
    subjectInfoBox("AcceptMap Test", expInfo)

expInfo['date'] = data.getDateStr()  # add a simple timestamp
expInfo['psychopyVersion'] = psychopyVersion

RegulateInstruction = "Focus on your breath.\n\nFeel your body float.\n\nAccept the following sensations as they come.\n\nTransform negative sensations into positive."

InstructionText = RegulateInstruction
instructioncode = regulate_instructions
InstructionCondition = "Regulation Instruction"
ConditionName = "Regulation Phase"

"""
3. Configure the parameters for each run
"""

bodySites1 = ['Right Arm', 'Left Arm', 'Right Arm', 'Left Arm']
bodySites2 = ['Left Arm', 'Right Arm', 'Left Arm', 'Right Arm'] 

if random.choice([True, False]): # Randomly select the order
    bodySites = bodySites1
else:
    bodySites = bodySites2

expInfo['body_site_order'] = str(bodySites)

test1 = ['acceptmapTEST-orig', 'acceptmapTEST-orig', 'acceptmapTEST-new', 'acceptmapTEST-new']
test2 = ['acceptmapTEST-new', 'acceptmapTEST-new', 'acceptmapTEST-orig', 'acceptmapTEST-orig'] 

if random.choice([True, False]): # Randomly select the order
    test = test1
else:
    test = test2

expInfo['expName'] = 'acceptmapTEST'

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
5. Prepare Experimental Dictionaries for Body-Site Cues and Medoc Temperature Programs
"""
cueImg = os.sep.join([stimuli_dir, "cue", "thermode.png"])
## Check gender for Chest cue
Chest_imgPath = os.sep.join([stimuli_dir,"cue","ChestF.png"])
if expInfo['sex'] in {"M", "m", "Male", "male"}:
    Chest_imgPath = os.sep.join([stimuli_dir,"cue","ChestM.png"])
elif expInfo['sex'] in {"F", "f", "Female", "female"}:
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
6. Prepare files to write
"""
sub_dir = os.path.join(_thisDir, 'data', 'sub-%05d' % (int(expInfo['DBIC Number'])), 'ses-%02d' % (int(expInfo['session'])))
if not os.path.exists(sub_dir):
    os.makedirs(sub_dir)

varNames = ['SID', 'date', 'sex', 'session', 'handedness', 'scanner', 'onset', 'duration', 'repetition', 'rating', 'body_site', 'keys', 'temperature', 'condition' 'rt', 'mouseclick', 'biopac_channel']
acceptmap_bids=pd.DataFrame(columns=varNames)

"""
5. Initialize Trial-level Components
"""
# General Instructional Text
start_msg = 'Please wait. \nThe scan will begin shortly. \n Experimenter press [s] to continue.'
in_between_run_msg = 'Thank you.\n Please wait for the next scan to start \n Experimenter press [e] to continue.'
end_msg = 'Please wait for instructions from the experimenter. \n Experimenter press [e] to continue.'

# Rating question text
painText="Was that painful?"
trialIntensityText="How intense was the heat stimulation?"

totalTrials = 16 # Figure out how many trials would be equated to 5 minutes
stimtrialTime = 13 # This becomes very unreliable with the use of poll_for_change().
ratingTime = 5

if debug == 1:
    stimtrialTime = 1 # This becomes very unreliable with the use of poll_for_change().
    totalTrials = 1
    # ratingTime = 1
# create a default keyboard (e.g. to check for escape)
defaultKeyboard = keyboard.Keyboard()

# 06/29/2022: Tor suggested we add an audio ding
rating_sound=mySound=sound.Sound('B', octave=5, stereo=1, secs=.5)  
## When you want to play the sound, run this line of code:
# rating_sound.play()

# Pre-Trial
expText="How painful do you expect this next stimulation will be?"

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

if biopac_exists:
    biopac.setData(biopac, 0)
    biopac.setData(biopac, task_ID) # Start demarcation of the T1 task in Biopac Acqknowledge

win.mouseVisible = False

"""
6. Welcome Instructions
"""
showText(win, "Instructions", 'Welcome to the scan\nPlease read the following instructions \nvery carefully.\n\n\n\nExperimenter press [Space] to continue.', biopacCode=instructions, noRecord=True)

if expInfo['run']>1:
    runRange=range(expInfo['run']-1, 8)
else:
    runRange=range(len(bodySites))
    

for runs in runRange:
    # Set Skin-Site to prevent burns:
    if (runs==0 or runs==1):
            skinSite='1'
    elif (runs==2 or runs==3):
            skinSite='2'
    else:
            skinSite='99'
    
    """
    7. Body-Site Instructions: Instruct the Experimenter on the Body Sites to attach thermodes to at the beginning of each run
    """
    bodysiteInstruction="Experimenter: \nPlease place the thermode on skin site " + skinSite + " of the: \n" + bodySites[runs].lower()
    showTextAndImg(win, "Bodysite Instruction", bodysiteInstruction, imgPath=bodysite_word2img[bodySites[runs]], biopacCode=bodymapping_instruction, noRecord=True)
    routineTimer.reset()
    
    """
    8. Start Scanner
    """
    if eyetracker_exists==1:
        sourceEDF_filename = "S%dR%s.EDF" % (int(expInfo['DBIC Number']), runs+1)
        destinationEDF = os.path.join(sub_dir, "S%dR%s.EDF" % (int(expInfo['DBIC Number']), runs+1))
        sourceEDF = setupEyetrackerFile(el_tracker, sourceEDF_filename)
        startEyetracker(el_tracker, sourceEDF, destinationEDF, eyetrackerCode)
    # fmriStart=confirmRunStart(win)
    
    """
    9. Set Trial parameters
    """
    jitter2 = None  # Reset Jitter2

    bodySiteData = bodySites[runs]
    # temperature = participant_settingsHeat[bodySites[runs]]
    temperature = 49
    BiopacChannel = bodysite_word2heatcode[bodySites[runs]]
    thermodeCommand = 135
    # thermodeCommand = 132 # Set to 47.5 for Maryam
    routineTimer.reset()

    """
    10. Start Trial Loop
    """
    for r in range(totalTrials): # 16 repetitions

        """
        11. Show the Instructions prior to the First Trial
        """
        if r == 0:      # First trial
            acceptmap_bids=acceptmap_bids.append(showText(win, InstructionCondition, InstructionText, fontSize=0.15, time=5, biopacCode=instructioncode), ignore_index=True)
       
        if test[runs] == 'acceptmapTEST-new':  
            rating_sound.play()
            acceptmap_bids=acceptmap_bids.append(showRatingScale(win, "Expectancy", expText, os.sep.join([stimuli_dir,"ratingscale","intensityScale.png"]), type="unipolar", time=ratingTime, biopacCode=expectancy_rating), ignore_index=True)
            rating_sound.stop()
            acceptmap_bids=acceptmap_bids.append(showImg(win, "ExpectancyCue", imgPath=cueImg, imgPos=(0, 0), time=5, biopacCode=expectancy_cue), ignore_index=True)      
       
        # Select Medoc Thermal Program
        if thermode_exists == 1:
            sendCommand('select_tp', thermodeCommand)

        """ 
        12. Pre-Heat Fixation Cross
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
            
        acceptmap_bids=acceptmap_bids.append(showFixation(win, "Pre-Trial Jitter", type='big', time=jitter1, biopacCode=prefixation), ignore_index=True)

        """ 
        13. Heat-Trial Fixation Cross
        """
        # Trigger Thermal Program
        if thermode_exists == 1:
            sendCommand('trigger') # Trigger the thermode

        acceptmap_bids=acceptmap_bids.append(showFixation(win, "Heat-Stimulation", type='big', time=stimtrialTime, biopacCode=BiopacChannel), ignore_index=True)
        acceptmap_bids['temperature'].iloc[-4:-1]=temperature
  
        """
        14. Post-Heat Fixation Cross
        """
        if debug==1:
            jitter2=1
        else:
            jitter2 = random.choice([5,7,9])
        acceptmap_bids=acceptmap_bids.append(showFixation(win, "Post-Trial Jitter", type='big', time=jitter2, biopacCode=midfixation), ignore_index=True)

        """
        15. Intensity Rating
        """
        rating_sound.play() # Play a sound to ensure the participant is awake.
        acceptmap_bids=acceptmap_bids.append(showRatingScale(win, "PainBinary", painText, os.sep.join([stimuli_dir,"ratingscale","YesNo.png"]), type="binary", time=ratingTime, biopacCode=pain_binary), ignore_index=True)
        painRating=acceptmap_bids['value'].iloc[-1]
        acceptmap_bids=acceptmap_bids.append(showRatingScale(win, "IntensityRating", trialIntensityText, os.sep.join([stimuli_dir,"ratingscale","intensityScale.png"]), type="unipolar", time=ratingTime, biopacCode=trialIntensity_rating), ignore_index=True)
        rating_sound.stop()

        """
        16. Post-Question jitter
        """
        if debug==1:
            jitter3=1
        else:
            jitter3 = random.choice([5,7,9])
        acceptmap_bids=acceptmap_bids.append(showFixation(win, "Post-Q-Jitter", type='big', time=jitter3, biopacCode=postfixation), ignore_index=True)

    """
    16. Begin post-run self-report questions
    """        
    rating_sound.stop() # I think a stop needs to be introduced in order to play again.
    rating_sound.play()

    acceptmap_bids=acceptmap_bids.append(showRatingScale(win, "ComfortRating", ComfortText, os.sep.join([stimuli_dir,"ratingscale","ComfortScale.png"]), type="bipolar", time=None, biopacCode=comfort_rating), ignore_index=True)
    acceptmap_bids=acceptmap_bids.append(showRatingScale(win, "ValenceRating", ValenceText, os.sep.join([stimuli_dir,"ratingscale","postvalenceScale.png"]), type="unipolar", time=None, biopacCode=valence_rating), ignore_index=True)
    acceptmap_bids=acceptmap_bids.append(showRatingScale(win, "IntensityRating", IntensityText, os.sep.join([stimuli_dir,"ratingscale","postintensityScale.png"]), type="unipolar", time=None, biopacCode=comfort_rating), ignore_index=True)
    acceptmap_bids=acceptmap_bids.append(showRatingScale(win, "AvoidanceRating", AvoidText, os.sep.join([stimuli_dir,"ratingscale","AvoidScale.png"]), type="bipolar", time=None, biopacCode=avoid_rating), ignore_index=True)
    acceptmap_bids=acceptmap_bids.append(showRatingScale(win, "RelaxationRating", RelaxText, os.sep.join([stimuli_dir,"ratingscale","RelaxScale.png"]), type="unipolar", time=None, biopacCode=relax_rating), ignore_index=True)
    acceptmap_bids=acceptmap_bids.append(showRatingScale(win, "AttentionRating", TaskAttentionText, os.sep.join([stimuli_dir,"ratingscale","TaskAttentionScale.png"]), type="unipolar", time=None, biopacCode=taskattention_rating), ignore_index=True)
    acceptmap_bids=acceptmap_bids.append(showRatingScale(win, "BoredomRating", BoredomText, os.sep.join([stimuli_dir,"ratingscale","BoredomScale.png"]), type="unipolar", time=None, biopacCode=boredom_rating), ignore_index=True)
    acceptmap_bids=acceptmap_bids.append(showRatingScale(win, "AlertnessRating", AlertnessText, os.sep.join([stimuli_dir,"ratingscale","AlertnessScale.png"]), type="bipolar", time=None, biopacCode=alertness_rating), ignore_index=True)
    acceptmap_bids=acceptmap_bids.append(showRatingScale(win, "PosThxRating", PosThxText, os.sep.join([stimuli_dir,"ratingscale","PosThxScale.png"]), type="bipolar", time=None, biopacCode=posthx_rating), ignore_index=True)
    acceptmap_bids=acceptmap_bids.append(showRatingScale(win, "NegThxRating", NegThxText, os.sep.join([stimuli_dir,"ratingscale","NegThxScale.png"]), type="bipolar", time=None, biopacCode=negthx_rating), ignore_index=True)  
    acceptmap_bids=acceptmap_bids.append(showRatingScale(win, "SelfRating", SelfText, os.sep.join([stimuli_dir,"ratingscale","SelfScale.png"]), type="bipolar", time=None, biopacCode=self_rating), ignore_index=True)
    acceptmap_bids=acceptmap_bids.append(showRatingScale(win, "OtherRating", OtherText, os.sep.join([stimuli_dir,"ratingscale","OtherScale.png"]), type="bipolar", time=None, biopacCode=other_rating), ignore_index=True)
    acceptmap_bids=acceptmap_bids.append(showRatingScale(win, "ImageryRating", ImageryText, os.sep.join([stimuli_dir,"ratingscale","ImageryScale.png"]), type="bipolar", time=None, biopacCode=posthx_rating), ignore_index=True)
    acceptmap_bids=acceptmap_bids.append(showRatingScale(win, "PresentRating", PresentText, os.sep.join([stimuli_dir,"ratingscale","PresentScale.png"]), type="bipolar", time=None, biopacCode=present_rating), ignore_index=True)

    rating_sound.stop() # Stop the sound so it can be played again.

    if eyetracker_exists==1:
        # stopEyeTracker(el_tracker, sourceEDF, destinationEDF, biopacCode=eyetrackerCode)

        if el_tracker.isConnected():
            # Terminate the current trial first if the task terminated prematurely
            error = el_tracker.isRecording()
            # if error == pylink.TRIAL_OK:
            #     abort_trial()

            # Put tracker in Offline mode
            el_tracker.setOfflineMode()

            # Clear the Host PC screen and wait for 500 ms
            el_tracker.sendCommand('clear_screen 0')
            pylink.msecDelay(500)

            # el_tracker = pylink.getEYELINK()

            if el_tracker.isConnected():
                # Close the edf data file on the Host
                el_tracker.closeDataFile()

                #### SHOULD I WAIT HERE? ####

                # Download the EDF data file from the Host PC to a local data folder
                # parameters: source_file_on_the_host, destination_file_on_local_drive
                # local_edf = os.path.join(sub_dir, '%s.EDF' % expInfo['run'])
                try:
                    # source: edf_file
                    el_tracker.receiveDataFile(sourceEDF, destinationEDF)
                except RuntimeError as error:
                    print('ERROR:', error)

    """
    17. Save data into .TSV formats and Tying up Loose Ends
    """ 
    # Append constants to the entire run
    acceptmap_bids['SID']=expInfo['DBIC Number']
    acceptmap_bids['date']=expInfo['date']
    acceptmap_bids['sex']=expInfo['sex']
    acceptmap_bids['session']=expInfo['session']
    acceptmap_bids['handedness']=expInfo['handedness']
    acceptmap_bids['scanner']=expInfo['scanner']
    acceptmap_bids['body_site']=bodySites[runs]
    acceptmap_bids['skin_site']=skinSite
    
    acceptmap_bidsfilename = sub_dir + os.sep + u'sub-SID%06d_ses-%02d_task-%s_acq-%s_run-%s_events.tsv' % (int(expInfo['DBIC Number']), int(expInfo['session']), test[runs], bodySites[runs].replace(" ", "").lower(), str(expInfo['run']+runs))
    
    acceptmap_bids.to_csv(acceptmap_bidsfilename, sep="\t")
    acceptmap_bids=pd.DataFrame(columns=varNames) # Clear it out for a new file.
    
    """
    18. End of Run, Wait for Experimenter instructions to begin next run
    """   
    if eyetracker_exists==1:
        stopEyeTracker(el_tracker, sourceEDF, destinationEDF, biopacCode=eyetrackerCode)
    
    nextRun(win)

"""
19. Wrap up
"""
endScan(win)

"""
End of Experiment
"""