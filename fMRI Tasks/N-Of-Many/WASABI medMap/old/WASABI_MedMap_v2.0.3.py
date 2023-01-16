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

This paradigm is run as 2 parts of a MedMap paradigm for 2 body sites: Left Face and Right Leg. 

One day will consist of 8 total runs of either Left Face or Right Leg interchanging between each run. Each run will feature 6 heat trials at 49 degrees C. 

As a consequence, in one day, correct running of these paradigms will generate 8x files of the names:
sub-SIDXXXXX_ses-XX_task-medmap_acq-[bodySite]_run-X_events.tsv

Each file will consist of the following headers:
'SID', 'day', 'sex', 'session', 'handedness', 'scanner', 'onset', 'duration', 'value', 'body_site', 'skin_site', 'temperature', 'condition', 'keys', 'rt', 'phase', 'biopac_channel'
 
Version 2.0.1: Updates the pre-trial question anchors. Will now accept calibration files with an extra Eligibility column
Version 2.0.2: Added Skin-Sites
Version 2.0.3: Fixed Skin-Site Assignment by Run.

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

from WASABI_psychopy_utilities import *
from WASABI_config import *

__author__ = "Michael Sun"
__version__ = "2.0.3"
__email__ = "msun@dartmouth.edu"
__status__ = "Production"

"""
0b. Helper functions
"""

def rescale(self, width=0, height=0, operation='', units=None, log=True):
    '''
    Function for rescaling the size of an object such as your ImageStim.
    '''
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
 
visual.ImageStim.rescale = rescale


def round_down(num, divisor):
    '''
    Function for rounding a number down.
    '''
    return num-(num%divisor)

# For setting the calibrated average heat
def round_to(n, precision):
    '''
    Function for rounding a number to the nearest precision point e.g., .5.
    '''
    correction = 0.5 if n >= 0 else -0.5
    # check if n is nan before casting to int
    try:
        return int( n/precision+correction ) * precision
    except:
        return np.nan

def round_to_halfdegree(n):
    '''
    Wrapper function for rounding a temperature to its closest half-degree.
    '''
    return round_to(n, 0.5)

"""
1. Experimental Parameters
Clocks, folder paths, etc.
"""
# Paths
# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)
main_dir = _thisDir
stimuli_dir = main_dir + os.sep + "stimuli"
video_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stimuli', 'videos')

# Brings up the Calibration/Data folder to load the appropriate calibration data right away.
calibration_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir, 'WASABI bodyCalibration', 'data')

"""
2. Start Experimental Dialog Boxes
"""
psychopyVersion = '2020.2.10'
if debug == 1:
    expInfo = {
    'DBIC Number': '99',
    'second(2) or third(3) day': '2',
    'sex': 'm',
    'session': '99',
    'handedness': 'r', 
    'scanner': 'MS',
    'run': '1',
    'body sites': ''
    }
else:
    expInfo = {
    'DBIC Number': '',
    'second(2) or third(3) day': '', 
    'sex': '',
    'session': '',
    'handedness': '', 
    'scanner': '',
    'run': '',
    'body sites': '' 
    }

# Load the subject's calibration file and ensure that it is valid
# Upload participant file: Browse for file
# Store info about the experiment session
if debug!=1:
    dlg1 = gui.fileOpenDlg(tryFilePath=calibration_dir, tryFileName="", prompt="Select participant calibration file (*_task-bodyCalibration_participants.tsv)", allowed="Calibration files (*.tsv)")
    if dlg1!=None:
        if "_task-bodyCalibration_participants.tsv" in dlg1[0]:
            # Read in participant info csv and convert to a python dictionary
            a = pd.read_csv(dlg1[0], delimiter='\t', index_col=0, header=0, squeeze=True)
            if a.shape == (1,23) or a.shape == (1,24):
                participant_settingsHeat = {}
                p_info = [dict(zip(a.iloc[i].index.values, a.iloc[i].values)) for i in range(len(a))][0]
                expInfo['DBIC Number'] = p_info['DBIC_id']
                expInfo['sex'] = p_info['sex']
                expInfo['handedness'] = p_info['handedness']
                # Heat Settings
                participant_settingsHeat['Left Face'] = p_info['leftface_ht']
                participant_settingsHeat['Right Face'] = p_info['rightface_ht']
                participant_settingsHeat['Left Arm'] = p_info['leftarm_ht']
                participant_settingsHeat['Right Arm'] = p_info['rightarm_ht']
                participant_settingsHeat['Left Leg'] = p_info['leftleg_ht']
                participant_settingsHeat['Right Leg'] = p_info['rightleg_ht']
                participant_settingsHeat['Chest'] = p_info['chest_ht']
                participant_settingsHeat['Abdomen'] = p_info['abdomen_ht']
                ses_num = str(1)

                expInfo2 = {
                'session': ses_num,
                'second(2) or third(3) day': '',
                'scanner': '',
                'run': '', # If re-inserting participant midday
                'body sites': '' # If inputting a list of body sites, make sure to delimit them with ', ' with the trailing space.
                }
                expInfo2=subjectInfoBox("MedMap Scan", expInfo2)
                expInfo['session'] = expInfo2['session']
                expInfo['second(2) or third(3) day'] = expInfo2['second(2) or third(3) day']
                expInfo['scanner'] = expInfo2['scanner']
                expInfo['run'] = expInfo2['run']
                expInfo['body sites'] = expInfo2['body sites']
            else:
                errorDlg1 = gui.Dlg(title="Error - invalid file")
                errorDlg1.addText("Selected file is not a valid calibration file. Data is incorrectly formatted. (Wrong dimensions)")
                errorDlg1.show()
                dlg1=None
        else:
            errorDlg2 = gui.Dlg(title="Error - invalid file")
            errorDlg2.addText("Selected file is not a valid calibration file. Name is not formatted sub-SIDXXXXXX_task-bodyCalibration_participant.tsv")
            errorDlg2.show()
            dlg1=None
        expInfo['date'] = data.getDateStr()  # add a simple timestamp
    if dlg1==None:
        ## This is used if an appropriate calibration is not selected. Generate a list of temperature choices.
        ## Limit the entries of this to hot temperatures (32-49 degrees in half-degree-steps)
        participant_settingsHeat = {
            'Left Face': [44,44.5,45,45.5,46,46.5,47,47.5,48,48.5],    # Calibrated Temp for left face
            'Right Face': [44,44.5,45,45.5,46,46.5,47,47.5,48,48.5],   # Calibrated Temp for right face
            'Left Arm': [44,44.5,45,45.5,46,46.5,47,47.5,48,48.5],     # Calibrated Temp for left arm
            'Right Arm': [44,44.5,45,45.5,46,46.5,47,47.5,48,48.5],    # Calibrated Temp for right arm
            'Left Leg': [44,44.5,45,45.5,46,46.5,47,47.5,48,48.5],     # Calibrated Temp for left leg
            'Right Leg': [44,44.5,45,45.5,46,46.5,47,47.5,48,48.5],    # Calibrated Temp for right leg
            'Chest': [44,44.5,45,45.5,46,46.5,47,47.5,48,48.5],        # Calibrated Temp for chest
            'Abdomen': [44,44.5,45,45.5,46,46.5,47,47.5,48,48.5]       # Calibrated Temp for abdomen
            }

        subjectInfoBox("MedMap Scan", expInfo)
        pphDlg = gui.DlgFromDict(participant_settingsHeat, 
                                title='Participant Heat Parameters')
        if pphDlg.OK == False:
            core.quit()
else:
    participant_settingsHeat = {
        'Left Face': '48.5',
        'Right Face': '48.5',
        'Left Arm': '48.5',
        'Right Arm': '48.5',
        'Left Leg': '48.5',
        'Right Leg': '48.5',
        'Chest': '48.5',
        'Abdomen': '48.5'
    }

if expInfo['second(2) or third(3) day']=='2':
    expName = 'MedMap1-conditioning'
elif expInfo['second(2) or third(3) day']=='3':
    expName = 'MedMap2-test'  

expInfo['run']=int(expInfo['run'])
expInfo['date'] = data.getDateStr()  # add a simple timestamp
expInfo['psychopyVersion'] = psychopyVersion
expInfo['expName'] = expName

"""
3. Configure the Stimuli Arrays
"""
if expInfo['body sites']=="":
    ## Based on our discussion with Tor, these body sites will likely have to change to Left Leg and Chest.
    # bodySites1 = ['Right Leg', 'Left Face', 'Right Leg', 'Left Face', 'Right Leg', 'Left Face', 'Hyperalignment', 'Right Leg', 'Left Face']
    # bodySites2 = ['Left Face', 'Right Leg', 'Left Face', 'Right Leg', 'Left Face', 'Right Leg', 'Hyperalignment', 'Left Face', 'Right Leg'] 
    # bodySites1 = ['Left Face', 'Left Face', 'Left Face', 'Left Face']

    bodySites1 = ['Left Leg', 'Chest', 'Left Leg', 'Chest', 'Left Leg', 'Chest', 'Hyperalignment', 'Left Leg', 'Chest']
    bodySites2 = ['Chest', 'Left Leg', 'Chest', 'Left Leg', 'Chest', 'Left Leg', 'Hyperalignment', 'Chest', 'Left Leg'] 

    if int(expInfo['DBIC Number'])%2==0:
        bodySites=bodySites1
    else:
        bodySites=bodySites2
else:
    bodySites=list(expInfo['body sites'].split(", "))

# If bodysites and run order need to be manually set for the participant, in a pinch, uncomment below and edit:
# bodySites = ["Left Leg"]

expInfo['body_site_order'] = str(bodySites)

""" 
4. Setup the Window
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

## Check sex for Chest cue
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

"""
5. Prepare files to write
"""
sub_dir = os.path.join(_thisDir, 'data', 'sub-SID%06d' % (int(expInfo['DBIC Number'])), 'ses-%02d' % (int(expInfo['session'])))
if not os.path.exists(sub_dir):
    os.makedirs(sub_dir)

varNames = ['SID', 'day', 'sex', 'session', 'handedness', 'scanner', 'onset', 'duration', 'value', 'body_site', 'skin_site', 'temperature', 'condition', 'keys', 'rt', 'phase', 'biopac_channel']
medmap_bids=pd.DataFrame(columns=varNames)

"""
5. Initialize Trial-level Components
"""
# General Instructional Text
start_msg = 'Please wait. \nThe scan will begin shortly. \n Experimenter press [s] to continue.'
s_text='[s]-press confirmed.'
in_between_run_msg = 'Thank you.\n Please wait for the next scan to start \n Experimenter press [e] to continue.'
end_msg = 'Please wait for instructions from the experimenter'

## Instruction Parameters
ExperienceInstruction = "Experience the following sensations as they come."
InstructionText = "Welcome to the scan, please wait for the experimenter to press [Space]."
instructioncode = instruction_code
InstructionCondition = "Instruction"

# Rating question text

# Pre-Control and Post-Treatment
threatText="How threatened or safe do you feel?" # -100 (Maximally Threatened) to 100 (Maximally Safe)
stressText="What is your stress level?" # 0 (None) to 100 (Strongest Imaginable)
painAnxText="What is your pain anxiety level?" # 0 (None) to 100 (Strongest Imaginable)
othAnxText="What is your anxiety level on things other than pain?" # 0 (None) to 100 (Strongest Imaginable)
painConfText="How confident do you feel in your ability to handle the pain?" #0 (None) to 100 (Strongest Imaginable)

# Pre-Trial
expText="How painful do you expect this next stimulation will be?"

# Post-Trial
painText="Was that painful?"
trialIntensityText="How intense was the heat stimulation?"

totalTrials = 6 # Figure out how many trials would be equated to 5 minutes
stimtrialTime = 15 # This becomes very unreliable with the use of poll_for_change().

ratingTime = 5 # Rating Time limit in seconds during the inter-stimulus-interval

if debug == 1:
    stimtrialTime = 1 # This becomes very unreliable with the use of poll_for_change().
    totalTrials = 1

# Pre-rating audio ding to wake participants up.
rating_sound=mySound=sound.Sound('B', octave=5, stereo=1, secs=.5, sampleRate=44100)  
## When you want to play the sound, run this line of code:
# rating_sound.play()

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

if expInfo['second(2) or third(3) day']=='2':
    movie=preloadMovie(win, "kungfury1", os.path.join(video_dir,'kungfury1.mp4'))
    movieCode=kungfury1
if expInfo['second(2) or third(3) day']=='3':
    movie=preloadMovie(win, "kungfury2", os.path.join(video_dir,'kungfury2.mp4'))
    movieCode=kungfury2

if biopac_exists:
    biopac.setData(biopac, 0)
    biopac.setData(biopac, task_ID) # Start demarcation of the T1 task in Biopac Acqknowledge

win.mouseVisible = False

"""
6. Welcome Instructions
"""
showText(win, "Instructions", InstructionText, biopacCode=instructions, noRecord=True)

# if eyetracker_exists==1:
#     calibrateEyeTracker(win, el_tracker, eyetrackerCalibration)

if expInfo['run']>1:
    runRange=range(expInfo['run']-1, 9)
else:
    runRange=range(len(bodySites)) # +1 for hyperalignment

for runs in runRange:
    if eyetracker_exists==1:
        sourceEDF_filename = "S%dR%s.EDF" % (int(expInfo['DBIC Number']), runs+1)
        destinationEDF = os.path.join(sub_dir, "S%dR%s.EDF" % (int(expInfo['DBIC Number']), runs+1))
        sourceEDF = setupEyetrackerFile(el_tracker, sourceEDF_filename)
        startEyetracker(el_tracker, sourceEDF, destinationEDF, eyetrackerCode)

    """
    7. Check if you should run the Hyperalignment Scan 
    """
    if runs==6:
        fmriStart=confirmRunStart(win)
        hyperalignment_bids=showMovie(win, movie, movie.name, movieCode)

        """
        8. Save hyperalignment data into its own .TSV
        """ 
        hyperalignment_bids_data = pd.DataFrame([hyperalignment_bids])
        hyperalignment_bids_filename = sub_dir + os.sep + u'sub-SID%06d_ses-%02d_task-%s_acq-%s_run-%d_events.tsv' % (int(expInfo['DBIC Number']), int(expInfo['session']), expName, 'hyperalignment', runs+1)
        hyperalignment_bids_data.to_csv(hyperalignment_bids_filename, sep="\t")
        continue
    else:
        """
        7. Body-Site Instructions: Instruct the Experimenter on the Body Sites to attach thermodes to at the beginning of each run 
        """
        # Set Skin-Site to prevent burns:
        if (expInfo['second(2) or third(3) day']=='2'):
            if runs in [0, 1, 4, 5]:
                skinSite='1'
            if runs in [2, 3, 7, 8]:
                skinSite='2'
        elif (expInfo['second(2) or third(3) day']=='3'):
            if runs in [2, 3, 7, 8]:
                skinSite='2'
            if runs in [0, 1, 4, 5]:
                skinSite='3'

        # Update instructions and cues based on current run's body-sites:
        if runs in [0, 1, 7, 8]:
            bodysiteInstruction="Experimenter: \nPlease place the thermode on the: \n" + bodySites[runs].lower() + " on site " + skinSite + "\n\n Prepare the site for stimulation"
        else:
            bodysiteInstruction="Experimenter: \nPlease place the thermode on the: \n" + bodySites[runs].lower() + " on site " + skinSite + "\n\n Apply the Lidoderm analgesic cream"
        showTextAndImg(win, "Bodysite Instruction", bodysiteInstruction, imgPath=bodysite_word2img[bodySites[runs]], biopacCode=bodymapping_instruction, noRecord=True)

        ## Conditioning parameters; Ideally this should be read from the participant's file 
        if expInfo['second(2) or third(3) day']=='2':
            if runs==0 or runs==1:
                temperature = participant_settingsHeat[bodySites[runs]]
                thermodeCommand=thermode_temp2program[temperature]
                ConditionName="Control"
                # Highest tolerable temperature
            if runs==2 or runs==3:
                # temperature = 44 # Not hot enough
                temperature = float(participant_settingsHeat[bodySites[runs]])-2
                thermodeCommand=thermode_temp2program[temperature]
                ConditionName="Placebo"
                # Warm and not hot temperature, set to -2 degrees from max for everyone
            if runs==4 or runs==5 or runs==6 or runs==7:
                # temperature=round_to_halfdegree(float(participant_settingsHeat[bodySites[runs]])-((float(participant_settingsHeat[bodySites[runs]])-44)/2))
                temperature = float(participant_settingsHeat[bodySites[runs]])-1 # Just slightly lower than max
                thermodeCommand=thermode_temp2program[temperature] 
                if runs==4 or runs==5:
                    ConditionName="Placebo"
                if runs==6 or runs==7:
                    ConditionName="Control"

        elif expInfo['second(2) or third(3) day']=='3':
            if runs in [0, 1, 6, 7]:
                ConditionName="Control"
            if runs in [2, 3, 4 ,5]:
                ConditionName="Placebo"
            temperature = participant_settingsHeat[bodySites[runs]]
            thermodeCommand=thermode_temp2program[temperature]
        
        if runs in [0, 2, 6]:
            rating_sound.play()
            medmap_bids=medmap_bids.append(showRatingScale(win, "Threat", threatText, os.sep.join([stimuli_dir,"ratingscale","SafeThreat.png"]), type="bipolar", time=None, nofMRI=True), ignore_index=True)
            medmap_bids=medmap_bids.append(showRatingScale(win, "Stress", stressText, os.sep.join([stimuli_dir,"ratingscale","UnipolarSensation.png"]), type="unipolar", time=None, nofMRI=True), ignore_index=True)
            medmap_bids=medmap_bids.append(showRatingScale(win, "PainAnxiety", painAnxText, os.sep.join([stimuli_dir,"ratingscale","UnipolarSensation.png"]), type="unipolar", time=None, nofMRI=True), ignore_index=True)
            medmap_bids=medmap_bids.append(showRatingScale(win, "OtherAnxiety", othAnxText, os.sep.join([stimuli_dir,"ratingscale","UnipolarSensation.png"]), type="unipolar", time=None, nofMRI=True), ignore_index=True)
            medmap_bids=medmap_bids.append(showRatingScale(win, "PainConfidence", painConfText, os.sep.join([stimuli_dir,"ratingscale","UnipolarSensation.png"]), type="unipolar", time=None, nofMRI=True), ignore_index=True)

        """
        8. Start Scanner
        """
        fmriStart=confirmRunStart(win)

        """
        9. Set Trial parameters
        """
        jitter2 = None  # Reset Jitter2
        BiopacChannel = bodysite_word2heatcode[bodySites[runs]]
        routineTimer.reset()
        
        """
        10. Start Trial Loop
        """
        for r in range(totalTrials): # 16 repetitions
            """
            11. Show the Instructions prior to the First Trial
            """
            if r == 0:      # First trial
                medmap_bids=medmap_bids.append(showText(win, "Instructions", ExperienceInstruction, time=5, advanceKey=None, biopacCode=instructioncode), ignore_index=True)
                routineTimer.reset()

            # Select Medoc Thermal Program
            if thermode_exists == 1:
                sendCommand('select_tp', thermodeCommand)
            
            medmap_bids=medmap_bids.append(showRatingScale(win, "Expectancy", expText, os.sep.join([stimuli_dir,"ratingscale","intensityScale.png"]), type="unipolar", time=ratingTime, biopacCode=expectancy_rating), ignore_index=True)

            """
            12. Show Heat Cue
            """
            # Need a biopac code
            medmap_bids=medmap_bids.append(showImg(win, "Cue", imgPath=cueImg, time=2, biopacCode=cue), ignore_index=True)

            """ 
            13. Pre-Heat Fixation Cross
            """
            jitter1 = random.choice([4, 6, 8])
            if debug==1:
                jitter1=1

            medmap_bids=medmap_bids.append(showFixation(win, "Pre-Jitter", time=jitter1, biopacCode=prefixation), ignore_index=True)

            """ 
            14. Heat-Trial Fixation Cross
            """
            if thermode_exists == 1:
                sendCommand('trigger') # Trigger the thermode
            medmap_bids=medmap_bids.append(showFixation(win, ConditionName+" Heat ", time=stimtrialTime, biopacCode=BiopacChannel), ignore_index=True)

            """
            15. Post-Heat Fixation Cross
            """
            if debug==1:
                jitter2=1
            else:
                jitter2 = random.choice([5,7,9])
            medmap_bids=medmap_bids.append(showFixation(win, "Mid-Jitter", time=jitter2, biopacCode=midfixation), ignore_index=True)

            """
            16. Begin post-trial self-report questions
            """        
            rating_sound.play()
            medmap_bids=medmap_bids.append(showRatingScale(win, "PainBinary", painText, os.sep.join([stimuli_dir,"ratingscale","YesNo.png"]), type="binary", time=ratingTime, biopacCode=pain_binary), ignore_index=True)
            painRating=medmap_bids['value'].iloc[-1]
            if painRating < 0:
                medmap_bids.append(wait("WaitPeriod", time=ratingTime), ignore_index=True)
            else:
                medmap_bids=medmap_bids.append(showRatingScale(win, "IntensityRating", trialIntensityText, os.sep.join([stimuli_dir,"ratingscale","intensityScale.png"]), type="unipolar", time=ratingTime, biopacCode=trialIntensity_rating), ignore_index=True)

            """
            17. Post-Question jitter
            """
            if debug==1:
                jitter3=1
            else:
                jitter3 = random.choice([5,7,9])
            medmap_bids=medmap_bids.append(showFixation(win, "Post-Q-Jitter", time=jitter2, biopacCode=postfixation), ignore_index=True)

        """
        18. Begin post-run self-report questions
        """        
        rating_sound.stop() # I think a stop needs to be introduced in order to play again.
        rating_sound.play()

        medmap_bids=medmap_bids.append(showRatingScale(win, "ComfortRating", ComfortText, os.sep.join([stimuli_dir,"ratingscale","ComfortScale.png"]), type="bipolar", time=None, biopacCode=comfort_rating), ignore_index=True)
        medmap_bids=medmap_bids.append(showRatingScale(win, "ValenceRating", ValenceText, os.sep.join([stimuli_dir,"ratingscale","postvalenceScale.png"]), type="unipolar", time=None, biopacCode=valence_rating), ignore_index=True)
        medmap_bids=medmap_bids.append(showRatingScale(win, "IntensityRating", IntensityText, os.sep.join([stimuli_dir,"ratingscale","postintensityScale.png"]), type="unipolar", time=None, biopacCode=comfort_rating), ignore_index=True)
        medmap_bids=medmap_bids.append(showRatingScale(win, "AvoidanceRating", AvoidText, os.sep.join([stimuli_dir,"ratingscale","AvoidScale.png"]), type="bipolar", time=None, biopacCode=avoid_rating), ignore_index=True)
        medmap_bids=medmap_bids.append(showRatingScale(win, "RelaxationRating", RelaxText, os.sep.join([stimuli_dir,"ratingscale","RelaxScale.png"]), type="unipolar", time=None, biopacCode=relax_rating), ignore_index=True)
        medmap_bids=medmap_bids.append(showRatingScale(win, "AttentionRating", TaskAttentionText, os.sep.join([stimuli_dir,"ratingscale","TaskAttentionScale.png"]), type="unipolar", time=None, biopacCode=taskattention_rating), ignore_index=True)
        medmap_bids=medmap_bids.append(showRatingScale(win, "BoredomRating", BoredomText, os.sep.join([stimuli_dir,"ratingscale","BoredomScale.png"]), type="unipolar", time=None, biopacCode=boredom_rating), ignore_index=True)
        medmap_bids=medmap_bids.append(showRatingScale(win, "AlertnessRating", AlertnessText, os.sep.join([stimuli_dir,"ratingscale","AlertnessScale.png"]), type="bipolar", time=None, biopacCode=alertness_rating), ignore_index=True)
        medmap_bids=medmap_bids.append(showRatingScale(win, "PosThxRating", PosThxText, os.sep.join([stimuli_dir,"ratingscale","PosThxScale.png"]), type="bipolar", time=None, biopacCode=posthx_rating), ignore_index=True)
        medmap_bids=medmap_bids.append(showRatingScale(win, "NegThxRating", NegThxText, os.sep.join([stimuli_dir,"ratingscale","NegThxScale.png"]), type="bipolar", time=None, biopacCode=negthx_rating), ignore_index=True)  
        medmap_bids=medmap_bids.append(showRatingScale(win, "SelfRating", SelfText, os.sep.join([stimuli_dir,"ratingscale","SelfScale.png"]), type="bipolar", time=None, biopacCode=self_rating), ignore_index=True)
        medmap_bids=medmap_bids.append(showRatingScale(win, "OtherRating", OtherText, os.sep.join([stimuli_dir,"ratingscale","OtherScale.png"]), type="bipolar", time=None, biopacCode=other_rating), ignore_index=True)
        medmap_bids=medmap_bids.append(showRatingScale(win, "ImageryRating", ImageryText, os.sep.join([stimuli_dir,"ratingscale","ImageryScale.png"]), type="bipolar", time=None, biopacCode=posthx_rating), ignore_index=True)
        medmap_bids=medmap_bids.append(showRatingScale(win, "PresentRating", PresentText, os.sep.join([stimuli_dir,"ratingscale","PresentScale.png"]), type="bipolar", time=None, biopacCode=present_rating), ignore_index=True)


        rating_sound.stop() # Stop the sound so it can be played again.

        """
        19. Save data into .TSV formats and Tying up Loose Ends
        """ 
        # Append constants to the entire run
        medmap_bids['SID']=expInfo['DBIC Number']
        medmap_bids['day']=expInfo['second(2) or third(3) day']
        medmap_bids['sex']=expInfo['sex']
        medmap_bids['session']=expInfo['session']
        medmap_bids['handedness']=expInfo['handedness'] 
        medmap_bids['scanner']=expInfo['scanner']
        medmap_bids['body_site']=bodySites[runs]
        medmap_bids['skin_site']=skinSite
        medmap_bids['phase']=ConditionName
        medmap_bids['temperature']=temperature

        medmap_bids_filename = sub_dir + os.sep + u'sub-SID%06d_ses-%02d_task-%s_acq-%s_run-%s_events.tsv' % (int(expInfo['DBIC Number']), int(expInfo['session']), expName, bodySites[runs].replace(" ", "").lower(), str(runs+1))
        medmap_bids.to_csv(medmap_bids_filename, sep="\t")
        medmap_bids=pd.DataFrame(columns=varNames) # Clear it out for a new file.

        if eyetracker_exists==1:
            stopEyeTracker(el_tracker, sourceEDF, destinationEDF, biopacCode=eyetrackerCode)

        """
        20. End of Run, Wait for Experimenter instructions to begin next run
        """   
        nextRun(win)
    
"""
23. Wrap up
"""
if eyetracker_exists==1:
    # Close the link to the tracker.
    el_tracker.close()
endScan(win)

"""
End of Experiment
"""