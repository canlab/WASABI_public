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
The design is as follows:
1. Start with a 48 degree stimulation trial (to be thrown away)
2. If not painful, increase the temperature by .5 degrees (max at 48.5)
3. If tolerable, then increase the temperature by .5 degrees (max at 48.5)
3. If intolerable, then reduce the temperature by .5 degrees and set that new temperature as the maximum temperature for the bodysite.
4. Average the ratings of the 6 subsequent trials

after every stimulation there will be questions (and rows in the data file) for:
[x] "Was that painful?"
[x] "How intense was the heat stimulation?" (Bartoshuk gLMS)
[x] "Was it tolerable, and can you take more of that heat?"

The paradigm will generate 8x of these files of name:
sub-SIDXXXXX_task-bodyCalibration_acq-[bodysite]_run-XX_events.tsv

Trials per file are defined by the following headers:
'SID', 'date', 'sex', 'session', 'handedness', 'scanner', 'onset', 'duration', 'repetition', 'rating', 'body_site', 'keys', 'temperature', 'condition' 'rt', 'mouseclick', 'biopac_channel']

With version 1.03, the stimulation duration was reduced to 15 seconds at peak time. Edits were made to the bids dataframe. 
With version 1.04, the stimulation duration was reduced to 10 seconds at peak time. Eyetracker functionality was added. Eligibility criteria includes being able to tolerate 47 degrees C to chest and left leg. Added an Eligibility column to the participants.tsv file.

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

import random
from datetime import datetime

from WASABI_psychopy_utilities import *
from WASABI_config import *

__author__ = "Michael Sun"
__version__ = "1.0.5"
__email__ = "msun@dartmouth.edu"
__status__ = "Production"

"""  
0b. Helper functions
"""
def rescale(self, width=0, height=0, operation='', units=None, log=True):
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


# For setting the heat-trial stimulation
def round_down(num, divisor):
    return num-(num%divisor)

# For setting the calibrated average heat
def round_to(n, precision):
    correction = 0.5 if n >= 0 else -0.5
    # check if n is nan before casting to int
    try:
        return int( n/precision+correction ) * precision
    except:
        return np.nan

def round_to_halfdegree(n):
    return round_to(n, 0.5)

from datetime import date

def calculate_age(born):
    b_date = datetime.strptime(born, '%m/%d/%Y')
    return (datetime.today() - b_date).days/365
 
visual.ImageStim.rescale = rescale

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
# Upload participant file: Browse for file
# Store info about the experiment session
psychopyVersion = '2020.2.10'
expName = 'bodyCalibration'  # from the Builder filename that created this script
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
    subjectInfoBox("BodyCalibration Scan", expInfo)

expInfo['date'] = data.getDateStr()  # add a simple timestamp
expInfo['psychopyVersion'] = psychopyVersion
expInfo['expName'] = expName

InstructionText = "Experience the following sensations as they come."

"""
5. Configure the Body-Site for each run
"""
if expInfo['body sites']=="":
    bodySites = ["Right Leg", "Left Face", "Right Face", "Left Arm", "Right Arm", "Left Leg", "Chest", "Abdomen"]
    random.shuffle(bodySites)
    # FOR THE RA: IF YOU NEED TO CONTINUE FROM AN INTERRUPTED BODYCALIBRATION:
    # 1. UNCOMMENT THE LINE BELOW,
    # 2. FILL IN THE FIRST ELEMENTS WITH BODYSITES ALREADY RUN, 
    # 3. AND THEN TYPE IN THE RUN YOU LEFT OFF ON IN THE DIALOGUE BOX UPON RE-RUNNING THIS TASK:!
    bodySites = ["Right Leg","Left Face", "Right Face","Left Arm", "Right Arm", "Left Leg", "Chest", "Abdomen"]
    
else:
    bodySites=list(expInfo['body sites'].split(", "))

# If bodysites and run order need to be manually set for the participant uncomment below and edit:
# bodySites = ["Left Leg"]

expInfo['body_site_order'] = str(bodySites)
expInfo['expName'] = expName

""" 
3. Setup the Window
"""
win=setupWindow()
# store frame rate of monitor if we can measure it
expInfo['frameRate'] = win.getActualFrameRate()
if expInfo['frameRate'] != None:
    frameDur = 1.0 / round(expInfo['frameRate'])
else:
    frameDur = 1.0 / 60.0  # could not measure, so guess

"""
4. Prepare Experimental Dictionaries for Body-Site Cues and Medoc Temperature Programs
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

# varNames = ['onset', 'duration', 'value', 'bodySite', 'temperature', 'condition', 'keys', 'rt', 'phase', 'biopacCode']
varNames = ['SID', 'date', 'sex', 'session', 'handedness', 'scanner', 'onset', 'duration', 'repetition', 'rating', 'body_site', 'keys', 'temperature', 'condition' 'rt', 'mouseclick', 'biopac_channel']
bodyCalibration_bids=pd.DataFrame(columns=varNames)

# Create python lists to later concatenate or convert into pandas dataframes
bodyCalibration_bids_total = []

averaged_data = []

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
painText="Was that painful?"
trialIntensityText="How intense was the heat stimulation?"
tolerableText="Was it tolerable, and can you take more of that heat?"


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

totalTrials = 7 # Figure out how many trials would be equated to 5 minutes
# Attribute 5 seconds to rampup and rampdown time
# stimtrialTime = 25 # This becomes very unreliable with the use of poll_for_change().
stimtrialTime = 15 # This becomes very unreliable with the use of poll_for_change().
ratingTime = 5 # Intensity Rating Time limit in seconds during the inter-trial-interval

if debug == 1:
    stimtrialTime = 1 # This becomes very unreliable with the use of poll_for_change().
    totalTrials = 2
# create a default keyboard (e.g. to check for escape)
defaultKeyboard = keyboard.Keyboard()

# 06/29/2022: Tor suggested we add an audio ding
rating_sound=mySound=sound.Sound('B', octave=5, stereo=1, secs=.5)  
## When you want to play the sound, run this line of code:
# rating_sound.play()

if biopac_exists:
    biopac.setData(biopac, 0)
    biopac.setData(biopac, task_ID) # Start demarcation of the T1 task in Biopac Acqknowledge

"""
6. Welcome Instructions
"""
showText(win, "Instructions", InstructionText, biopacCode=instructions, noRecord=True)

if expInfo['run']>1:
    runRange=range(expInfo['run']-1, 8)
else:
    runRange=range(len(bodySites)) # +1 for hyperalignment

for runs in runRange:
    if eyetracker_exists==1:
        sourceEDF_filename = "S%dR%s.EDF" % (int(expInfo['DBIC Number']), runs+1)
        destinationEDF = os.path.join(sub_dir, "S%dR%s.EDF" % (int(expInfo['DBIC Number']), runs+1))
        sourceEDF = setupEyetrackerFile(el_tracker, sourceEDF_filename)
        startEyetracker(el_tracker, sourceEDF, destinationEDF, eyetrackerCode)

    """
    7. Body-Site Instructions: Instruct the Experimenter on the Body Sites to attach thermodes to at the beginning of each run 
    """
    bodysiteInstruction="Experimenter: \nPlease place the thermode on the: \n" + bodySites[runs].lower()
    showTextAndImg(win, "Bodysite Instruction", bodysiteInstruction, imgPath=bodysite_word2img[bodySites[runs]], biopacCode=bodymapping_instruction, noRecord=True)

    """
    8. Start Scanner
    """
    fmriStart=confirmRunStart(win)

    """
    9. Set Trial parameters
    """
    jitter2 = None  # Reset Jitter2

    currentTemp=48
    maxTemp=48.5
    minTemp=45

    bodySiteData = bodySites[runs]
    BiopacChannel = bodysite_word2heatcode[bodySites[runs]]
    routineTimer.reset()

    """
    10. Start Trial Loop
    """
    for r in range(totalTrials): # 7 repetitions
        """
        11. Show the Instructions prior to the First Trial
        """
        if r == 0:      # First trial
            bodyCalibration_bids=bodyCalibration_bids.append(showText(win, "Instructions", ExperienceInstruction, time=5, advanceKey=None, biopacCode=instructioncode), ignore_index=True)
            routineTimer.reset()

        # Select Medoc Thermal Program
        if thermode_exists == 1:
            sendCommand('select_tp', thermode_temp2program[currentTemp])

        """
        12. Show Heat Cue
        """
        # Need a biopac code
        bodyCalibration_bids=bodyCalibration_bids.append(showImg(win, "Cue", imgPath=cueImg, time=2, biopacCode=cue), ignore_index=True)

        """ 
        13. Pre-Heat Fixation Cross
        """
        jitter1 = random.choice([4, 6, 8])
        if debug==1:
            jitter1=1

        bodyCalibration_bids=bodyCalibration_bids.append(showFixation(win, "Pre-Jitter", time=jitter1, biopacCode=prefixation), ignore_index=True)

        """ 
        14. Heat-Trial Fixation Cross
        """
        if thermode_exists == 1:
            sendCommand('trigger') # Trigger the thermode
        bodyCalibration_bids=bodyCalibration_bids.append(showFixation(win, "Heat-Stimulation", time=stimtrialTime, biopacCode=BiopacChannel), ignore_index=True)
        # bodyCalibration_bids.tail(1)['temperature']=currentTemp
        # bodyCalibration_bids.tail(1)['body_site']=bodySites[runs]
        bodyCalibration_bids['temperature'].iloc[-1]=currentTemp
        bodyCalibration_bids['body_site'].iloc[-1]=bodySites[runs]
        """
        15. Post-Heat Fixation Cross
        """
        if debug==1:
            jitter2=1
        else:
            jitter2 = random.choice([5,7,9])
        bodyCalibration_bids=bodyCalibration_bids.append(showFixation(win, "Mid-Jitter", time=jitter2, biopacCode=midfixation), ignore_index=True)

        """
        16. Begin post-trial self-report questions
        """        
        rating_sound.play()
        bodyCalibration_bids=bodyCalibration_bids.append(showRatingScale(win, "PainBinary", painText, os.sep.join([stimuli_dir,"ratingscale","YesNo.png"]), type="binary", time=ratingTime, biopacCode=pain_binary), ignore_index=True)
        
        painRating=bodyCalibration_bids['value'].iloc[-1]

        if painRating < 0:
            bodyCalibration_bids.append(wait("WaitPeriod", time=2*ratingTime), ignore_index=True)
            bodyCalibration_total_trial = []
            bodyCalibration_total_trial.extend((r+1, bodySites[runs], currentTemp, painRating, None, 1))
            bodyCalibration_bids_total.append(bodyCalibration_total_trial)
               
            # Update Temperature if Pain Binary is -1
            if currentTemp < maxTemp:
                currentTemp=currentTemp+.5
        else:
            bodyCalibration_bids=bodyCalibration_bids.append(showRatingScale(win, "IntensityRating", trialIntensityText, os.sep.join([stimuli_dir,"ratingscale","intensityScale.png"]), type="unipolar", time=ratingTime, biopacCode=trialIntensity_rating), ignore_index=True)
            intensityRating=bodyCalibration_bids['value'].iloc[-1]
            bodyCalibration_bids=bodyCalibration_bids.append(showRatingScale(win, "ToleranceRating", tolerableText, os.sep.join([stimuli_dir,"ratingscale","YesNo.png"]), type="binary", time=ratingTime, biopacCode=tolerance_binary), ignore_index=True)
            toleranceRating=bodyCalibration_bids['value'].iloc[-1]
            bodyCalibration_total_trial =[]
            bodyCalibration_total_trial.extend((r+1, bodySites[runs], currentTemp, painRating, intensityRating, toleranceRating))
            bodyCalibration_bids_total.append(bodyCalibration_total_trial)
            
            # Update Temperature if Tolerance Binary is 1
            if toleranceRating>0 and currentTemp < maxTemp:
                currentTemp=currentTemp+.5
            # Adjust temperature down if the temperature is not tolerable
            if toleranceRating<0 and currentTemp > minTemp:
                currentTemp=currentTemp-.5
                maxTemp = currentTemp
            if toleranceRating<0 and currentTemp == minTemp:
                # End the run.
                break
        
        rating_sound.stop() # I think sounds have to stopped before they can be played again.
        """
        17. Post-Question jitter
        """
        if debug==1:
            jitter3=1
        else:
            jitter3 = random.choice([5,7,9])
        bodyCalibration_bids=bodyCalibration_bids.append(showFixation(win, "Post-Q-Jitter", time=jitter2, biopacCode=postfixation), ignore_index=True)

    """
    18. Begin post-run self-report questions
    """        
    rating_sound.stop() # I think a stop needs to be introduced in order to play again.
    rating_sound.play()

    bodyCalibration_bids=bodyCalibration_bids.append(showRatingScale(win, "ComfortRating", ComfortText, os.sep.join([stimuli_dir,"ratingscale","ComfortScale.png"]), type="bipolar", time=None, biopacCode=comfort_rating), ignore_index=True)
    bodyCalibration_bids=bodyCalibration_bids.append(showRatingScale(win, "ValenceRating", ValenceText, os.sep.join([stimuli_dir,"ratingscale","postvalenceScale.png"]), type="unipolar", time=None, biopacCode=valence_rating), ignore_index=True)
    bodyCalibration_bids=bodyCalibration_bids.append(showRatingScale(win, "IntensityRating", IntensityText, os.sep.join([stimuli_dir,"ratingscale","postintensityScale.png"]), type="unipolar", time=None, biopacCode=comfort_rating), ignore_index=True)
    bodyCalibration_bids=bodyCalibration_bids.append(showRatingScale(win, "AvoidanceRating", AvoidText, os.sep.join([stimuli_dir,"ratingscale","AvoidScale.png"]), type="bipolar", time=None, biopacCode=avoid_rating), ignore_index=True)
    bodyCalibration_bids=bodyCalibration_bids.append(showRatingScale(win, "RelaxationRating", RelaxText, os.sep.join([stimuli_dir,"ratingscale","RelaxScale.png"]), type="unipolar", time=None, biopacCode=relax_rating), ignore_index=True)
    bodyCalibration_bids=bodyCalibration_bids.append(showRatingScale(win, "AttentionRating", TaskAttentionText, os.sep.join([stimuli_dir,"ratingscale","TaskAttentionScale.png"]), type="unipolar", time=None, biopacCode=taskattention_rating), ignore_index=True)
    bodyCalibration_bids=bodyCalibration_bids.append(showRatingScale(win, "BoredomRating", BoredomText, os.sep.join([stimuli_dir,"ratingscale","BoredomScale.png"]), type="unipolar", time=None, biopacCode=boredom_rating), ignore_index=True)
    bodyCalibration_bids=bodyCalibration_bids.append(showRatingScale(win, "AlertnessRating", AlertnessText, os.sep.join([stimuli_dir,"ratingscale","AlertnessScale.png"]), type="bipolar", time=None, biopacCode=alertness_rating), ignore_index=True)
    bodyCalibration_bids=bodyCalibration_bids.append(showRatingScale(win, "PosThxRating", PosThxText, os.sep.join([stimuli_dir,"ratingscale","PosThxScale.png"]), type="bipolar", time=None, biopacCode=posthx_rating), ignore_index=True)
    bodyCalibration_bids=bodyCalibration_bids.append(showRatingScale(win, "NegThxRating", NegThxText, os.sep.join([stimuli_dir,"ratingscale","NegThxScale.png"]), type="bipolar", time=None, biopacCode=negthx_rating), ignore_index=True)  
    bodyCalibration_bids=bodyCalibration_bids.append(showRatingScale(win, "SelfRating", SelfText, os.sep.join([stimuli_dir,"ratingscale","SelfScale.png"]), type="bipolar", time=None, biopacCode=self_rating), ignore_index=True)
    bodyCalibration_bids=bodyCalibration_bids.append(showRatingScale(win, "OtherRating", OtherText, os.sep.join([stimuli_dir,"ratingscale","OtherScale.png"]), type="bipolar", time=None, biopacCode=other_rating), ignore_index=True)
    bodyCalibration_bids=bodyCalibration_bids.append(showRatingScale(win, "ImageryRating", ImageryText, os.sep.join([stimuli_dir,"ratingscale","ImageryScale.png"]), type="bipolar", time=None, biopacCode=posthx_rating), ignore_index=True)
    bodyCalibration_bids=bodyCalibration_bids.append(showRatingScale(win, "PresentRating", PresentText, os.sep.join([stimuli_dir,"ratingscale","PresentScale.png"]), type="bipolar", time=None, biopacCode=present_rating), ignore_index=True)

    rating_sound.stop() # Stop the sound so it can be played again.

    """
    17. Save data into .TSV formats and Tying up Loose Ends
    """ 
    bodyCalibration_bids['SID']=expInfo['DBIC Number']
    bodyCalibration_bids['date']=expInfo['date']
    bodyCalibration_bids['sex']=expInfo['sex']
    bodyCalibration_bids['session']=expInfo['session']
    bodyCalibration_bids['handedness']=expInfo['handedness']
    bodyCalibration_bids['scanner']=expInfo['scanner']

    bodyCalibration_bids_filename = sub_dir + os.sep + u'sub-SID%06d_ses-%02d_task-%s_acq-%s_run-%s_events.tsv' % (int(expInfo['DBIC Number']), int(expInfo['session']), expName, bodySites[runs].replace(" ", "").lower(), str(runs+1))
    bodyCalibration_bids.to_csv(bodyCalibration_bids_filename, sep="\t")
    bodyCalibration_bids = pd.DataFrame(columns=varNames) # Reset collection

    """
    18. End of Run, Wait for Experimenter instructions to begin next run
    """
    if eyetracker_exists==1:
        stopEyeTracker(el_tracker, sourceEDF, destinationEDF, biopacCode=eyetrackerCode)
    nextRun(win)

"""
19. Saving data in BIDS
"""
bids_filename = sub_dir + os.sep + u'sub-SID%06d_task-%s.tsv' % (int(expInfo['DBIC Number']), expName)
bids_df=pd.DataFrame(pd.DataFrame(bodyCalibration_bids_total, columns = ['repetition', 'body_site', 'temperature', 'pain', 'intensity', 'tolerance']))
bids_df.to_csv(bids_filename, sep="\t")

averaged_filename = sub_dir + os.sep + u'sub-SID%06d_task-%s_participants.tsv' % (int(expInfo['DBIC Number']), expName)
averaged_data.extend([expInfo['date'], expInfo['DBIC Number'], calculate_age(expInfo['dob (mm/dd/yyyy)']), expInfo['dob (mm/dd/yyyy)'], expInfo['sex'], expInfo['handedness'], bodySites,
                    round_to_halfdegree(bids_df.loc[(bids_df['body_site']=='Left Arm') & (bids_df['repetition']!=1) & (bids_df['pain']==1) & (bids_df['tolerance']==1)]['temperature'].mean()), 
                    round_to_halfdegree(bids_df.loc[(bids_df['body_site']=='Right Arm') & (bids_df['repetition']!=1) & (bids_df['pain']==1) & (bids_df['tolerance']==1)]['temperature'].mean()), 
                    round_to_halfdegree(bids_df.loc[(bids_df['body_site']=='Left Leg') & (bids_df['repetition']!=1) & (bids_df['pain']==1) & (bids_df['tolerance']==1)]['temperature'].mean()), 
                    round_to_halfdegree(bids_df.loc[(bids_df['body_site']=='Right Leg') & (bids_df['repetition']!=1) & (bids_df['pain']==1) & (bids_df['tolerance']==1)]['temperature'].mean()), 
                    round_to_halfdegree(bids_df.loc[(bids_df['body_site']=='Left Face') & (bids_df['repetition']!=1) & (bids_df['pain']==1) & (bids_df['tolerance']==1)]['temperature'].mean()), 
                    round_to_halfdegree(bids_df.loc[(bids_df['body_site']=='Right Face') & (bids_df['repetition']!=1) & (bids_df['pain']==1) & (bids_df['tolerance']==1)]['temperature'].mean()), 
                    round_to_halfdegree(bids_df.loc[(bids_df['body_site']=='Chest') & (bids_df['repetition']!=1) & (bids_df['pain']==1) & (bids_df['tolerance']==1)]['temperature'].mean()), 
                    round_to_halfdegree(bids_df.loc[(bids_df['body_site']=='Abdomen') & (bids_df['repetition']!=1) & (bids_df['pain']==1) & (bids_df['tolerance']==1)]['temperature'].mean()),
                    bids_df.loc[(bids_df['body_site']=='Left Arm') & (bids_df['repetition']!=1) & (bids_df['pain']==1) & (bids_df['tolerance']==1)]['intensity'].mean(), bids_df.loc[(bids_df['body_site']=='Right Arm') & (bids_df['repetition']!=1) & (bids_df['pain']==1) & (bids_df['tolerance']==1)]['intensity'].mean(), 
                    bids_df.loc[(bids_df['body_site']=='Left Leg') & (bids_df['repetition']!=1) & (bids_df['pain']==1) & (bids_df['tolerance']==1)]['intensity'].mean(), bids_df.loc[(bids_df['body_site']=='Right Leg') & (bids_df['repetition']!=1) & (bids_df['pain']==1) & (bids_df['tolerance']==1)]['intensity'].mean(), 
                    bids_df.loc[(bids_df['body_site']=='Left Face') & (bids_df['repetition']!=1) & (bids_df['pain']==1) & (bids_df['tolerance']==1)]['intensity'].mean(), bids_df.loc[(bids_df['body_site']=='Right Face') & (bids_df['repetition']!=1) & (bids_df['pain']==1) & (bids_df['tolerance']==1)]['intensity'].mean(), 
                    bids_df.loc[(bids_df['body_site']=='Chest') & (bids_df['repetition']!=1) & (bids_df['pain']==1) & (bids_df['tolerance']==1)]['intensity'].mean(), bids_df.loc[(bids_df['body_site']=='Abdomen') & (bids_df['repetition']!=1) & (bids_df['pain']==1) & (bids_df['tolerance']==1)]['intensity'].mean()])

averaged_df = pd.DataFrame(data = [averaged_data], columns = ['date','DBIC_id','age','dob','sex','handedness','calibration_order',
                                                    'leftarm_ht','rightarm_ht','leftleg_ht','rightleg_ht','leftface_ht','rightface_ht','chest_ht','abdomen_ht',
                                                    'leftarm_i','rightarm_i','leftleg_i','rightleg_i','leftface_i','rightface_i','chest_i','abdomen_i'])

# If there are no left face or right leg trials other than the first that are painful yet tolerable, then calibration has failed. 
if bids_df.loc[(bids_df['body_site']=='Left Leg') & (bids_df['repetition']!=1) & (bids_df['pain']==1) & (bids_df['tolerance']==1)]['temperature'].count()==0:
    end_msg="Thank you for your participation. \n\n\nUnfortunately you don't qualify for the continuation of this study. Experimenter please press [e]."
    averaged_df['Eligible']=-1

if bids_df.loc[(bids_df['body_site']=='Chest') & (bids_df['repetition']!=1) & (bids_df['pain']==1) & (bids_df['tolerance']==1)]['temperature'].count()==0:
    end_msg="Thank you for your participation. \n\n\nUnfortunately you don't qualify for the continuation of this study. Experimenter please press [e]."
    averaged_df['Eligible']=-2

elif averaged_df['leftleg_ht']<47 | averaged_df['chest_ht']<47:
    end_msg="Thank you for your participation. \n\n\nUnfortunately you don't qualify for the continuation of this study. Experimenter please press [e]."
    averaged_df['Eligible']=-3

averaged_df.to_csv(averaged_filename, sep="\t")

"""
19. Wrap up
"""
if biopac_exists:
    biopac.setData(biopac,0)
    biopac.setData(biopac,end_task)
win.flip()

"""
20. Wrap up
"""
endScan(win, text=end_msg)

"""
End of Experiment
"""