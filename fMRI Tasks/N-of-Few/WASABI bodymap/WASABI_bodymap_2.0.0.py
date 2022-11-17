# -*- coding: utf-8 -*-
"""
This experiment was initialized using PsychoPy3 Experiment Builder (v2020.2.5),
    on November 10, 2020, at 15:04
If you publish work using this script the most relevant publication is:

    Peirce J, Gray JR, Simpson S, MacAskill M, Höchenberger R, Sogo H, Kastman E, Lindeløv JK. (2019) 
        PsychoPy2: Experiments in behavior made easy Behav Res 51: 195. 
        https://doi.org/10.3758/s13428-018-01193-y
        
This python script was extensively modified in order to work in the Dartmouth Brain Imaging Center environment reading in signals coming from a 
Siemens 3T fMRI scanner. Physiological data is acquired with a Biopac MP150 Physiological data acquisition device via LabJack U3.

Some measures have been taken to minimize experimental latency. PTB/Psychopy style is used to initialize all objects prior to screen flipping as much as possible.
    3124
Data is written in BIDS 1.4.1 format, as separate tab-separated-value (.tsv) files for each run per subject, (UTF-8 encoding). 
Following this format:
all data headers are in lower snake_case.
missing values are coded None or -99 (i.e., body_site for rest trials).

The paradigm will generate 8x of these files of name:
sub-XXXX_task-bodymapSTX_acq-bodysite_run-XX_events.tsv

Trials per file are defined by the following headers:
onset   duration    trial_type  body_site   temp

along with 3 rows indicating:
valence intensity   comfort

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
__version__ = "2.0.0"
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
thermode_exists = 1

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
0c. Prepare Devices: Biopac Psychophysiological Acquisition and Medoc Thermode
"""
# Biopac parameters _________________________________________________
# Relevant Biopac commands: 
#     To send a Biopac marker code to Acqknowledge, replace the FIO number with a value between 0-255(dec), or an 8-bit word(bin) 
#     For instance, the following code would send a value of 15 by setting the first 4 bits to “1": biopac.setData(biopac, 15)
#     Toggling each of the FIO 8 channels directly: biopac.setFIOState(fioNum = 0:7, state=1)

# biopac channels EDIT
task_ID=1
task_start=7

run_start=9

bodymapping_intro=14
bodymapping_instruction=15
imagination_instruction=16
leftface_heat=17
rightface_heat=18
leftarm_heat=19
rightarm_heat=20
leftleg_heat=21
rightleg_heat=22
chest_heat=23
abdomen_heat=24
leftface_warm=25
rightface_warm=26
leftarm_warm=27
rightarm_warm=28
leftleg_warm=29
rightleg_warm=30
chest_warm=31
abdomen_warm=32

leftface_imagine_cue=176
rightface_imagine_cue=177
leftarm_imagine_cue=179
rightarm_imagine_cue=179
leftleg_imagine_cue=180
rightleg_imagine_cue=181
chest_imagine_cue=182
abdomen_imagine_cue=183

leftface_imagine=33
rightface_imagine=34
leftarm_imagine=35
rightarm_imagine=36
leftleg_imagine=37
rightleg_imagine=38
chest_imagine=39
abdomen_imagine=40

rest=41
valence_rating=42
intensity_rating=43
comfort_rating=44

between_run_msg=45
end=46

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

# Medoc TSA2 parameters ______________________________________________
# Initialize the Medoc TSA2 thermal stimulation delivery device
    # Medoc Troubleshooting:
    # To find the computer IP address, check with MMS Arbel's External Control (or Windows ipconfig alternatively)
    # Communication port is always 20121
    # Relevant Medoc commands:
    #     Prepare a program: sendCommand('select_tp', config.START_CALIBRATION)
    #     Poll the Machine to know if it's ready for another command: poll_for_change("[RUNNING/IDLE]", poll_interval=0.5, poll_max = -1 (unlimited), verbose=False, server_lag=1)
    #           Select "RUNNING" if you are using a "Manual Trigger" and a SELECT_TP has already been sent. Select "IDLE" if you are using an "Auto" Trigger design
    #     Trigger a prepared program: sendCommand('trigger')
    #     Pause a program: sendCommand('pause')
    #     Stop a program: sendCommand('stop')
if thermode_exists == 1:
    # Import medocControl library, python library custom written for Medoc with pyMedoc pollforchange functionality. 
    # Make sure medocControl.py is in the same directory 
    from medocControl import *

"""
1. Experimental Parameters
Clocks, paths, etc.
"""
# Clocks
globalClock = core.Clock()              # to track the time since experiment started
routineTimer = core.CountdownTimer()    # to track time remaining of each (non-slip) routine
# fmriClock = core.Clock() 

# Paths
# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)
main_dir = _thisDir
stimuli_dir = main_dir + os.sep + "stimuli"
# Brings up the Calibration/Data folder to load the appropriate calibration data right away.
calibration_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir, os.path.pardir, os.path.pardir, 'Calibration', 'data')

"""
2. Start Experimental Dialog Boxes
"""

# Upload participant file: Browse for file
psychopyVersion = '2020.2.5'
expInfo = {
'subject number': '', 
'gender': '',
'bodymap first- or second-half (1 or 2)': '',
'session': '',
'handedness': '', 
'scanner': ''
}

## Limit the entries of this to hot temperatures (32-49 degrees in half-degree-steps)
participant_settingsHeat = {
    'Left Face': [32,32.5,33,33.5,34,34.5,35,35.5,36,36.5,37,37.5,38,38.5,39,39.5,40,40.5,41,41.5,42,42.5,43,43.5,44,44.5,45,45.5,46,46.5,47,47.5,48,48.5,49],    # Calibrated Temp for left face
    'Right Face': [32,32.5,33,33.5,34,34.5,35,35.5,36,36.5,37,37.5,38,38.5,39,39.5,40,40.5,41,41.5,42,42.5,43,43.5,44,44.5,45,45.5,46,46.5,47,47.5,48,48.5,49],   # Calibrated Temp for right face
    'Left Arm': [32,32.5,33,33.5,34,34.5,35,35.5,36,36.5,37,37.5,38,38.5,39,39.5,40,40.5,41,41.5,42,42.5,43,43.5,44,44.5,45,45.5,46,46.5,47,47.5,48,48.5,49],     # Calibrated Temp for left arm
    'Right Arm': [32,32.5,33,33.5,34,34.5,35,35.5,36,36.5,37,37.5,38,38.5,39,39.5,40,40.5,41,41.5,42,42.5,43,43.5,44,44.5,45,45.5,46,46.5,47,47.5,48,48.5,49],    # Calibrated Temp for right arm
    'Left Leg': [32,32.5,33,33.5,34,34.5,35,35.5,36,36.5,37,37.5,38,38.5,39,39.5,40,40.5,41,41.5,42,42.5,43,43.5,44,44.5,45,45.5,46,46.5,47,47.5,48,48.5,49],     # Calibrated Temp for left leg
    'Right Leg': [32,32.5,33,33.5,34,34.5,35,35.5,36,36.5,37,37.5,38,38.5,39,39.5,40,40.5,41,41.5,42,42.5,43,43.5,44,44.5,45,45.5,46,46.5,47,47.5,48,48.5,49],    # Calibrated Temp for right leg
    'Chest': [32,32.5,33,33.5,34,34.5,35,35.5,36,36.5,37,37.5,38,38.5,39,39.5,40,40.5,41,41.5,42,42.5,43,43.5,44,44.5,45,45.5,46,46.5,47,47.5,48,48.5,49],        # Calibrated Temp for chest
    'Abdomen': [32,32.5,33,33.5,34,34.5,35,35.5,36,36.5,37,37.5,38,38.5,39,39.5,40,40.5,41,41.5,42,42.5,43,43.5,44,44.5,45,45.5,46,46.5,47,47.5,48,48.5,49]       # Calibrated Temp for abdomen
    }
## Limit the entries of this to hot temperatures (32-49 degrees in half-degree-steps)
participant_settingsWarm = {
    'Left Face': [32,32.5,33,33.5,34,34.5,35,35.5,36,36.5,37,37.5,38,38.5,39,39.5,40,40.5,41,41.5,42,42.5,43,43.5,44,44.5,45,45.5,46,46.5,47,47.5,48,48.5,49],     # Calibrated Temp for left face
    'Right Face': [32,32.5,33,33.5,34,34.5,35,35.5,36,36.5,37,37.5,38,38.5,39,39.5,40,40.5,41,41.5,42,42.5,43,43.5,44,44.5,45,45.5,46,46.5,47,47.5,48,48.5,49],    # Calibrated Temp for right face
    'Left Arm': [32,32.5,33,33.5,34,34.5,35,35.5,36,36.5,37,37.5,38,38.5,39,39.5,40,40.5,41,41.5,42,42.5,43,43.5,44,44.5,45,45.5,46,46.5,47,47.5,48,48.5,49],      # Calibrated Temp for left arm
    'Right Arm': [32,32.5,33,33.5,34,34.5,35,35.5,36,36.5,37,37.5,38,38.5,39,39.5,40,40.5,41,41.5,42,42.5,43,43.5,44,44.5,45,45.5,46,46.5,47,47.5,48,48.5,49],     # Calibrated Temp for right arm
    'Left Leg': [32,32.5,33,33.5,34,34.5,35,35.5,36,36.5,37,37.5,38,38.5,39,39.5,40,40.5,41,41.5,42,42.5,43,43.5,44,44.5,45,45.5,46,46.5,47,47.5,48,48.5,49],      # Calibrated Temp for left leg
    'Right Leg': [32,32.5,33,33.5,34,34.5,35,35.5,36,36.5,37,37.5,38,38.5,39,39.5,40,40.5,41,41.5,42,42.5,43,43.5,44,44.5,45,45.5,46,46.5,47,47.5,48,48.5,49],     # Calibrated Temp for right leg
    'Chest': [32,32.5,33,33.5,34,34.5,35,35.5,36,36.5,37,37.5,38,38.5,39,39.5,40,40.5,41,41.5,42,42.5,43,43.5,44,44.5,45,45.5,46,46.5,47,47.5,48,48.5,49],         # Calibrated Temp for chest
    'Abdomen': [32,32.5,33,33.5,34,34.5,35,35.5,36,36.5,37,37.5,38,38.5,39,39.5,40,40.5,41,41.5,42,42.5,43,43.5,44,44.5,45,45.5,46,46.5,47,47.5,48,48.5,49]       # Calibrated Temp for abdomen
    }

# Load the subject's calibration file and ensure that it is valid
if debug==1:
    expInfo = {
        'subject number': '999', 
        'gender': 'm',
        'bodymap first- or second-half (1 or 2)': '2',
        'session': '99',
        'handedness': 'r', 
        'scanner': 'TEST'
    }
    participant_settingsHeat = {
        'Left Face': 46,
        'Right Face': 46,
        'Left Arm': 46,
        'Right Arm': 46,
        'Left Leg': 46,
        'Right Leg': 46,
        'Chest': 46,
        'Abdomen': 46
    }
    participant_settingsWarm = {
        'Left Face': 40,
        'Right Face': 40,
        'Left Arm': 40,
        'Right Arm': 40,
        'Left Leg': 40,
        'Right Leg': 40,
        'Chest': 40,
        'Abdomen': 40
    }
else:
    dlg1 = gui.fileOpenDlg(tryFilePath=calibration_dir, tryFileName="", prompt="Select participant calibration file (*_task-Calibration_participants.tsv)", allowed="Calibration files (*.tsv)")
    if dlg1!=None:
        if "_task-Calibration_participants.tsv" in dlg1[0]:
            # Read in participant info csv and convert to a python dictionary
            a = pd.read_csv(dlg1[0], delimiter='\t', index_col=0, header=0, squeeze=True)
            if a.shape == (1,39):
                participant_settingsHeat = {}
                participant_settingsWarm = {}
                p_info = [dict(zip(a.iloc[i].index.values, a.iloc[i].values)) for i in range(len(a))][0]
                expInfo['subject number'] = p_info['participant_id']
                expInfo['gender'] = p_info['gender']
                expInfo['handedness'] = p_info['handedness']
                bodySites = p_info['calibration_order']
                # Heat Settings
                participant_settingsHeat['Left Face'] = p_info['leftface_ht']
                participant_settingsHeat['Right Face'] = p_info['rightface_ht']
                participant_settingsHeat['Left Arm'] = p_info['leftarm_ht']
                participant_settingsHeat['Right Arm'] = p_info['rightarm_ht']
                participant_settingsHeat['Left Leg'] = p_info['leftleg_ht']
                participant_settingsHeat['Right Leg'] = p_info['rightleg_ht']
                participant_settingsHeat['Chest'] = p_info['chest_ht']
                participant_settingsHeat['Abdomen'] = p_info['abdomen_ht']
                # Warm Settings
                participant_settingsWarm['Left Face'] = p_info['leftface_st']+1
                participant_settingsWarm['Right Face'] = p_info['rightface_st']+1
                participant_settingsWarm['Left Arm'] = p_info['leftarm_st']+1
                participant_settingsWarm['Right Arm'] = p_info['rightarm_st']+1
                participant_settingsWarm['Left Leg'] = p_info['leftleg_st']+1
                participant_settingsWarm['Right Leg'] = p_info['rightleg_st']+1
                participant_settingsWarm['Chest'] = p_info['chest_st']+1
                participant_settingsWarm['Abdomen'] =  p_info['abdomen_st']+1
                
                # count number of existing sessions and set the session number
                bodymap_num = str(1)
                ses_num = str(1) 
                expInfo2 = {
                'bodymap first- or second-half (1 or 2)': bodymap_num,
                'session': ses_num,
                'scanner': ''
                }
                dlg2 = gui.DlgFromDict(title="WASABI Body-Site Scan", dictionary=expInfo2, sortKeys=False) 
                expInfo['bodymap first- or second-half (1 or 2)'] = expInfo2['bodymap first- or second-half (1 or 2)']
                expInfo['session'] = expInfo2['session']
                expInfo['scanner'] = expInfo2['scanner']
                bodySites = bodySites.strip('][').replace("'","").split(', ')
                if expInfo['bodymap first- or second-half (1 or 2)'] == '1':
                    bodySites = bodySites[0:4]
                if expInfo['bodymap first- or second-half (1 or 2)'] == '2':
                    bodySites = bodySites[4:8]
                if dlg2.OK == False:
                    core.quit()  # user pressed cancel
            else:
                errorDlg1 = gui.Dlg(title="Error - invalid file")
                errorDlg1.addText("Selected file is not a valid calibration file. Data is incorrectly formatted. (Wrong dimensions)")
                errorDlg1.show()
                dlg1=None
        else:
            errorDlg2 = gui.Dlg(title="Error - invalid file")
            errorDlg2.addText("Selected file is not a valid calibration file. Name is not formatted sub-XXX_task-Calibration_participant.tsv")
            errorDlg2.show()
            dlg1=None
    if dlg1==None:
        dlg2 = gui.DlgFromDict(title="WASABI Body-Site Scan", dictionary=expInfo, sortKeys=False)
        if dlg2.OK == False:
            core.quit()  # user pressed cancel
        pphDlg = gui.DlgFromDict(participant_settingsHeat, 
                                title='Participant Heat Parameters')
        if pphDlg.OK == False:
            core.quit()
        ppwDlg = gui.DlgFromDict(participant_settingsWarm, 
                                title='Participant Warmth Parameters')
        if ppwDlg.OK == False:
            core.quit()

expInfo['date'] = data.getDateStr()  # add a simple timestamp
expInfo['psychopyVersion'] = psychopyVersion
if expInfo['bodymap first- or second-half (1 or 2)'] == '1':
    expName = 'bodymapST1'
if expInfo['bodymap first- or second-half (1 or 2)'] == '2':
    expName = 'bodymapST2'
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
4. Prepare Experimental Dictionaries for Body-Site Cues and Medoc Temperature Programs
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
bodysite_word2warmcode = {"Left Face": leftface_warm, 
                        "Right Face": rightface_warm, 
                        "Left Arm": leftarm_warm, 
                        "Right Arm": rightarm_warm, 
                        "Left Leg": leftleg_warm, 
                        "Right Leg": rightleg_warm, 
                        "Chest": chest_warm,
                        "Abdomen": abdomen_warm 
                        }
bodysite_word2imaginecode = {"Left Face": leftface_imagine, 
                        "Right Face": rightface_imagine, 
                        "Left Arm": leftarm_imagine, 
                        "Right Arm": rightarm_imagine, 
                        "Left Leg": leftleg_imagine, 
                        "Right Leg": rightleg_imagine, 
                        "Chest": chest_imagine,
                        "Abdomen": abdomen_imagine 
                        }

bodysite_word2cuecode = {"Left Face": leftface_imagine_cue, 
                        "Right Face": rightface_imagine_cue, 
                        "Left Arm": leftarm_imagine_cue, 
                        "Right Arm": rightarm_imagine_cue, 
                        "Left Leg": leftleg_imagine_cue, 
                        "Right Leg": rightleg_imagine_cue, 
                        "Chest": chest_imagine_cue,
                        "Abdomen": abdomen_imagine_cue 
                        }


# Set up a dictionary for all the configured Medoc programs for the main thermode
thermode1_temp2program = {}
with open("thermode1_programs.txt") as f:
    for line in f:
       (key, val) = line.split()
       thermode1_temp2program[float(key)] = int(val)

"""
5. Create Body-Site Pairs for each run for this participant
"""
# EAFP: Easier to ask forgiveness than permission style
# See if bodysite order was generated by the calibration file, otherwise make a new one.
try:
    bodySites
except NameError:
    bodySites_exists = False
else:
    bodySites_exists = True
if bodySites_exists == False:
    bodySites = ["Left Face", "Right Face", "Left Arm", "Right Arm", "Left Leg", "Right Leg", "Chest", "Abdomen"]
    random.shuffle(bodySites)
    bodySites = bodySites[0:4]

# random.shuffle(bodySites)

# # For melanie's run / if a session needs to be rerun; enter body site in below array and make sure varaible name is in line with if statemnet/no indent or space
###bodySites = ["Right Face"]


# For Stephanie's run / if a session needs to be rerun; enter body site in below array and make sure varaible name is in line with if statemnet/no indent or space
# bodySites = ["Left Arm", "Left Leg", "Right Face"]

bodySites = ["Left Leg"]
random.shuffle(bodySites)
# If you want to rerun a run mid-run, shuffle remaining bodysites first, and then prepend the interrupted run:
# bodySites.insert(0, "Left Face")



expInfo['body_site_order'] = str(bodySites)

"""
6. Prepare files to write
"""
sub_dir = os.path.join(_thisDir, 'data', 'sub-%05d' % (int(expInfo['subject number'])), 'ses-%02d' % (int(expInfo['session'])))
if not os.path.exists(sub_dir):
    os.makedirs(sub_dir)
psypy_filename = sub_dir + os.sep + u'sub-%05d_ses-%02d_task-%s_%s' % (int(expInfo['subject number']), int(expInfo['session']), expName, expInfo['date'])

# An ExperimentHandler isn't essential but helps with data saving
thisExp = data.ExperimentHandler(name=expName, version='2.0.0',
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

stimtrialTime = 13 # This becomes very unreliable with the use of poll_for_change().
poststimTime = 5 # Ensure that nonstimtrialTime - poststimTime is at least 5 or 6 seconds.
nonstimtrialTime = 13 # trial time in seconds (ISI)

imaginationCueTime = 2
imaginationTrialTime = nonstimtrialTime - imaginationCueTime

if debug == 1:
    stimtrialTime = 1 # This becomes very unreliable with the use of poll_for_change().
    poststimTime = 1 # Ensure that nonstimtrialTime - poststimTime is at least 5 or 6 seconds.
    nonstimtrialTime = 2 # trial time in seconds (ISI)

    imaginationCueTime = 1
    imaginationTrialTime = nonstimtrialTime - imaginationCueTime

#############
# Body Mapping Components
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
# Initialize components for Routine "BodySiteInstruction"
BodySiteInstructionClock = core.Clock()
BodySiteInstructionRead = keyboard.Keyboard()
BodySiteInstructionText = visual.TextStim(win, name='BodySiteInstructionText', 
    text="Experimenter: Please place thermodes on the designated body-site.",
    font = 'Arial',
    pos=(0, -.2), height=0.05, wrapWidth=1.6, ori=0, 
    color='white', colorSpace='rgb', opacity=1, 
    languageStyle='LTR',
    depth=0.0, 
    anchorHoriz='center')
BodySiteImg = visual.ImageStim(
    win=win,
    name='BodySiteImg', 
    mask=None,
    ori=0, pos=(0, 0), size=(.40,.40),
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=512, interpolate=True, depth=0.0)

# Initialize components for Routine "ImaginationInstruction"
ImaginationInstructionClock = core.Clock()
ImaginationInstructionRead = keyboard.Keyboard()
# Create experimenter instructions
ImagineInstructionText = visual.TextStim(win, name='ImageInstructionText', 
    text="During this scan, you will occasionally see picture cues of the body part where the thermode is attached. When you see this, without closing your eyes, try to imagine as hard as you can that the thermal stimulations are more painful than they are. Try to focus on how unpleasant the pain is, for instance, how strongly you would like to remove yourself from it. Pay attention to the burning, stinging and shooting sensations. You can use your mind to turn up the dial of the pain, much like turning up the volume dial on a stereo. As you feel the pain rise in intensity, imagine it rising faster and faster and going higher and higher. Picture your skin being held up against a glowing hot metal or fire. Think of how disturbing it is to be burned, and visualize your skin sizzling, melting, and bubbling as a result of the intense heat. Hold this thought in your mind for as long as the fixation cross on the screen is orange. When it is no longer on screen (or is white) you may stop imagining.",
    font = 'Arial',
    pos=(0, 0), height=0.05, wrapWidth=1.5, ori=0,      # Edit wrapWidth for the 1920 full screen
    color='white', colorSpace='rgb', opacity=1, 
    languageStyle='LTR',
    depth=0.0, 
    anchorHoriz='center')
ImagineInstructionText.size=(1,1)

# Initialize components for Routine "StimTrial"
# Three Conditions: Hot, Warm, Rest
StimTrialClock = core.Clock()
fix_cross = visual.TextStim(win = win, text = '+', color = [1,1,1], height = 0.3, anchorHoriz='center')

# Initialize components for Routine "NonStimTrial"
# One Condition: Imagine
NonStimTrialClock = core.Clock()
image_shortinstr = "Your skin is being held up against a glowing hot metal or fire. \nVisualize your skin sizzling, melting and bubbling "
NonStimTrialText = visual.TextStim(win, name='NonStimTrialText', 
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

# Initialize components for each Rating
ratingTime = 10 # Rating Time limit in seconds
TIME_INTERVAL = 0.005   # Speed at which slider ratings udpate
ratingScaleWidth=1.5
ratingScaleHeight=.4
sliderMin = -.75
sliderMax = .75
valenceText = "How pleasant was that overall?"
intensityText = "How intense was that overall?"
comfortText = "How comfortable do you feel right now?"
black_triangle_verts = [(sliderMin, .2),    # left point
                        (sliderMax, .2),    # right point
                        (0, -.2)]           # bottom-point

# Initialize components for Routine "ValenceRating"
ValenceRatingClock = core.Clock()
ValenceRating = visual.Rect(win, height=ratingScaleHeight, width=0, pos= [0, 0], fillColor='red', lineColor='black')
ValenceBlackTriangle = visual.ShapeStim(win, vertices=black_triangle_verts, fillColor='black', lineColor='black')
ValenceMouse = event.Mouse(win=win)
ValenceMouse.mouseClock = core.Clock()
ValenceAnchors = visual.ImageStim(
    win=win,
    image= os.sep.join([stimuli_dir,"ratingscale","valenceScale.png"]),
    name='ValenceAnchors', 
    mask=None,
    ori=0, pos=(0, -.09), size=(1.5, .4),
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=512, interpolate=True, depth=0.0)
ValencePrompt = visual.TextStim(win, name='ValencePrompt', 
    text=valenceText,
    font = 'Arial',
    pos=(0, 0.3), height=0.05, wrapWidth=None, ori=0, 
    color='white', colorSpace='rgb', opacity=1, 
    languageStyle='LTR',
    depth=0.0,
    anchorHoriz='center')

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

# Initialize components for Routine "ComfortRating"
ComfortRatingClock = core.Clock()
ComfortRating = visual.Rect(win, height=ratingScaleHeight, width=0, pos= [0, 0], fillColor='red', lineColor='black')
ComfortBlackTriangle = visual.ShapeStim(win, vertices=black_triangle_verts, fillColor='black', lineColor='black')
ComfortMouse = event.Mouse(win=win)
ComfortMouse.mouseClock = core.Clock()
ComfortAnchors = visual.ImageStim(
    win=win,
    image= os.sep.join([stimuli_dir,"ratingscale","comfortScale.png"]),
    name='ComfortAnchors', 
    mask=None,
    ori=0, pos=(0, -.105), size=(1.5,.4),
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=512, interpolate=True, depth=0.0)
ComfortPrompt = visual.TextStim(win, name='ComfortPrompt', 
    text=comfortText,
    font = 'Arial',
    pos=(0, 0.3), height=0.05, wrapWidth=None, ori=0, 
    color='white', colorSpace='rgb', opacity=1, 
    languageStyle='LTR',
    depth=0.0,
    anchorHoriz='center')

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
8. Start Experimental Loops: 
    runLoop (prepare the trial order for the run)
    trialLoop (prepare the trial_type for each trial)
"""
# Start demarcation of the bodymap task in Biopac Acqknowledge
if biopac_exists:
    biopac.setData(biopac, 0)     
    biopac.setData(biopac, task_ID) 
"""
8a. Body Mapping Introduction
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
        win.callOnFlip(print, "Cueing Biopac Channel: " + str(bodymapping_intro))
        if biopac_exists == 1:
            win.callOnFlip(biopac.setData, biopac, 0)
            win.callOnFlip(biopac.setData, biopac, bodymapping_intro)
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
print("CueOff Channel: " + str(bodymapping_intro))
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
if int(expInfo['subject number']) % 2 == 0: subjectOrder = os.sep.join([stimuli_dir,"EvenOrders.xlsx"]) 
else: subjectOrder = subjectOrder = os.sep.join([stimuli_dir,"OddOrders.xlsx"])

if expName == 'bodymapST1':
    runLoop = data.TrialHandler(nReps=1, method='random', extraInfo=expInfo, originPath=-1, trialList=data.importConditions(subjectOrder, selection='0:4'), seed=None, name='runLoop')
if expName == 'bodymapST2':
    runLoop = data.TrialHandler(nReps=1, method='random', extraInfo=expInfo, originPath=-1, trialList=data.importConditions(subjectOrder, selection='4:9'), seed=None, name='runLoop')

thisExp.addLoop(runLoop)  # add the loop to the experiment
thisrunLoop = runLoop.trialList[0]  # so we can initialise stimuli with some values

# abbreviate parameter names if possible (e.g. rgb = thisrunLoop.rgb)
if thisrunLoop != None:
    for paramName in thisrunLoop:
        exec('{} = thisrunLoop[paramName]'.format(paramName))

"""
8c. Instruct the Experimenter on the Body Sites to attach thermodes to at the beginning of each run
"""
for thisrunLoop in runLoop:                     # Loop through each run.
    currentLoop = runLoop
    # abbreviate parameter names if possible (e.g. rgb = thisrunLoop.rgb)
    if thisrunLoop != None:
        for paramName in thisrunLoop:
            exec('{} = thisrunLoop[paramName]'.format(paramName))

    # ------Prepare to start Routine "BodySiteInstruction"-------
    continueRoutine = True
    # update component parameters for each repeat
    BodySiteInstructionRead.keys = []
    BodySiteInstructionRead.rt = []
    _BodySiteInstructionRead_allKeys = []
    ## Update instructions and cues based on current run's body-sites:
    BodySiteInstructionText.text="Experimenter: \nPlease place the thermode on the: \n" + bodySites[runLoop.thisTrialN].lower()
    # keep track of which components have finished
    BodySiteInstructionComponents = [BodySiteInstructionText, BodySiteImg, BodySiteInstructionRead]

    for thisComponent in BodySiteInstructionComponents:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    BodySiteInstructionClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    frameN = -1
    
    # -------Run Routine "BodySiteInstruction"-------
    while continueRoutine:
        # get current time
        t = BodySiteInstructionClock.getTime()
        tThisFlip = win.getFutureFlipTime(clock=BodySiteInstructionClock)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *BodySiteInstructionText* updates
        if BodySiteInstructionText.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            BodySiteInstructionText.frameNStart = frameN  # exact frame index
            BodySiteInstructionText.tStart = t  # local t and not account for scr refresh
            BodySiteInstructionText.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(BodySiteInstructionText, 'tStartRefresh')  # time at next scr refresh
            BodySiteInstructionText.setAutoDraw(True)

        # *BodySiteImg* updates
        if BodySiteImg.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            BodySiteImg.image = bodysite_word2img[bodySites[runLoop.thisTrialN]]
            BodySiteImg.pos = (0, .2)
            # keep track of start time/frame for later
            BodySiteImg.frameNStart = frameN  # exact frame index
            BodySiteImg.tStart = t  # local t and not account for scr refresh
            BodySiteImg.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(BodySiteImg, 'tStartRefresh')  # time at next scr refresh
            BodySiteImg.setAutoDraw(True)
        
        # *BodySiteInstructionRead* updates
        waitOnFlip = False
        if BodySiteInstructionRead.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            BodySiteInstructionRead.frameNStart = frameN  # exact frame index
            BodySiteInstructionRead.tStart = t  # local t and not account for scr refresh
            BodySiteInstructionRead.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(BodySiteInstructionRead, 'tStartRefresh')  # time at next scr refresh
            BodySiteInstructionRead.status = STARTED
            # keyboard checking is just starting
            waitOnFlip = True
            win.callOnFlip(print, "Cueing Off All Biopac Channels")            
            win.callOnFlip(print, "Showing BodySite Instructions")
            win.callOnFlip(print, "Cueing Biopac Channel: " + str(bodymapping_instruction))
            if biopac_exists == 1:
                win.callOnFlip(biopac.setData, biopac, 0)
                win.callOnFlip(biopac.setData, biopac, bodymapping_instruction)
            win.callOnFlip(BodySiteInstructionRead.clock.reset)  # t=0 on next screen flip
            win.callOnFlip(BodySiteInstructionRead.clearEvents, eventType='keyboard')  # clear events on next screen flip
        if BodySiteInstructionRead.status == STARTED and not waitOnFlip:
            theseKeys = BodySiteInstructionRead.getKeys(keyList=['space'], waitRelease=False)
            _BodySiteInstructionRead_allKeys.extend(theseKeys)
            if len(_BodySiteInstructionRead_allKeys):
                BodySiteInstructionRead.keys = _BodySiteInstructionRead_allKeys[-1].name  # just the last key pressed
                BodySiteInstructionRead.rt = _BodySiteInstructionRead_allKeys[-1].rt
                # a response ends the routine
                continueRoutine = False
        
        # Autoresponder
        if t >= thisSimKey.rt and autorespond == 1:
            _BodySiteInstructionRead_allKeys.extend([thisSimKey]) 

        # check for quit (typically the Esc key)
        if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
            core.quit()
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in BodySiteInstructionComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()

    # -------Ending Routine "BodySiteInstruction"-------
    print("CueOff Channel: " + str(bodymapping_instruction))
    for thisComponent in BodySiteInstructionComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    runLoop.addData('BodySiteInstructionText.started', BodySiteInstructionText.tStartRefresh)
    runLoop.addData('BodySiteImg.started', BodySiteImg.tStartRefresh)
    runLoop.addData('BodySiteImg.stopped', BodySiteImg.tStopRefresh)
    # check responses
    if BodySiteInstructionRead.keys in ['', [], None]:  # No response was made
        BodySiteInstructionRead.keys = None
    runLoop.addData('BodySiteInstructionRead.keys',BodySiteInstructionRead.keys)
    if BodySiteInstructionRead.keys != None:  # we had a response
        runLoop.addData('BodySiteInstructionRead.rt', BodySiteInstructionRead.rt)
    runLoop.addData('BodySiteInstructionRead.started', BodySiteInstructionRead.tStartRefresh)
    runLoop.addData('BodySiteInstructionRead.stopped', BodySiteInstructionRead.tStopRefresh)
    # Start a new BIDS data collection array for each run
    bodymap_bids_data = []
    # the Routine "BodySiteInstruction" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()
    """
    7c. Undergo the imagination instruction with the participant on the first run
    """
    if runLoop.thisTrialN == 0:
        # ------Prepare to start Routine "ImaginationInstruction"-------
        # Initialize trial stimuli
        ###########################################################################################
        continueRoutine = True

        # update component parameters for each repeat
        ImaginationInstructionRead.keys = []
        ImaginationInstructionRead.rt = []
        _ImaginationInstructionRead_allKeys = []
        
        # keep track of which components have finished
        ImaginationInstructionComponents = [ImagineInstructionText, ImaginationInstructionRead]
        for thisComponent in ImaginationInstructionComponents:
            thisComponent.tStart = None
            thisComponent.tStop = None
            thisComponent.tStartRefresh = None
            thisComponent.tStopRefresh = None
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        # reset timers
        t = 0
        _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        ImaginationInstructionClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
        frameN = -1
        
        # -------Run Routine "ImaginationInstruction"-------
        while continueRoutine:
            # get current time
            t = ImaginationInstructionClock.getTime()
            tThisFlip = win.getFutureFlipTime(clock=ImaginationInstructionClock)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame
            
            # *ImagineInstructionText* updates
            if ImagineInstructionText.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                ImagineInstructionText.frameNStart = frameN  # exact frame index
                ImagineInstructionText.tStart = t  # local t and not account for scr refresh
                ImagineInstructionText.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(ImagineInstructionText, 'tStartRefresh')  # time at next scr refresh
                ImagineInstructionText.setAutoDraw(True)
            
            # *ImaginationInstructionRead* updates
            waitOnFlip = False
            if ImaginationInstructionRead.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                ImaginationInstructionRead.frameNStart = frameN  # exact frame index
                ImaginationInstructionRead.tStart = t  # local t and not account for scr refresh
                ImaginationInstructionRead.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(ImaginationInstructionRead, 'tStartRefresh')  # time at next scr refresh
                ImaginationInstructionRead.status = STARTED
                # keyboard checking is just starting
                waitOnFlip = True
                win.callOnFlip(print, "Showing Imagination Instructions")
                win.callOnFlip(print, "Cue Biopac " + str(imagination_instruction))
                if biopac_exists == 1:
                    win.callOnFlip(biopac.setData, biopac, 0)
                    win.callOnFlip(biopac.setData, biopac, imagination_instruction)
                win.callOnFlip(ImaginationInstructionRead.clock.reset)  # t=0 on next screen flip
                win.callOnFlip(ImaginationInstructionRead.clearEvents, eventType='keyboard')  # clear events on next screen flip
            if ImaginationInstructionRead.status == STARTED and not waitOnFlip:
                theseKeys = ImaginationInstructionRead.getKeys(keyList=['space'], waitRelease=False)
                _ImaginationInstructionRead_allKeys.extend(theseKeys)
                if len(_ImaginationInstructionRead_allKeys):
                    ImaginationInstructionRead.keys = _ImaginationInstructionRead_allKeys[-1].name  # just the last key pressed
                    ImaginationInstructionRead.rt = _ImaginationInstructionRead_allKeys[-1].rt
                    # a response ends the routine
                    print("Starting mainloop")
                    continueRoutine = False

            # Autoresponder
            if t >= thisSimKey.rt and autorespond == 1:
                _ImaginationInstructionRead_allKeys.extend([thisSimKey]) 

            # check for quit (typically the Esc key)
            if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
                core.quit()
            
            # check if all components have finished
            if not continueRoutine:  # a component has requested a forced-end of Routine
                break
            continueRoutine = False  # will revert to True if at least one component still running
            for thisComponent in ImaginationInstructionComponents:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished
            
            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()
        # -------Ending Routine "ImaginationInstruction"-------
#         print("Cueing Biopac Channel " + str(task_start))
        for thisComponent in ImaginationInstructionComponents:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        runLoop.addData('ImagineInstructionText.started', ImagineInstructionText.tStartRefresh)
        # check responses
        if ImaginationInstructionRead.keys in ['', [], None]:  # No response was made
            ImaginationInstructionRead.keys = None
        runLoop.addData('ImaginationInstructionRead.keys',ImaginationInstructionRead.keys)
        if ImaginationInstructionRead.keys != None:  # we had a response
            runLoop.addData('ImaginationInstructionRead.rt', ImaginationInstructionRead.rt)
        runLoop.addData('ImaginationInstructionRead.started', ImaginationInstructionRead.tStartRefresh)
        runLoop.addData('ImaginationInstructionRead.stopped', ImaginationInstructionRead.tStopRefresh)
        # the Routine "ImaginationInstruction" was not non-slip safe, so reset the non-slip timer
        routineTimer.reset()

    """
    8d. Begin the run of 42 trials. 
        4 Conditions (trial_type)
        2 Trial Types: (Stimulation and Non-Stimulation)
        Stimulation
            1. Heat applied to body-site
            2. Warmth applied to body-site
            4. Rest
        Non-Stimulation
            3. Imagine Heat applied to body-site
    """
    # set up handler to look after randomisation of conditions etc
    trials = data.TrialHandler(nReps=1, method='sequential', extraInfo=expInfo, originPath=-1, trialList=runLoop.trialList[runLoop.thisTrialN]['runSeq'], seed=None, name='trials')
    thisExp.addLoop(trials)  # add the loop to the experiment
    thisTrial = trials.trialList[0]  # so we can initialise stimuli with some values
    # abbreviate parameter names if possible (e.g. rgb = thisTrial.rgb)

    hot = thermode1_temp2program[participant_settingsHeat[bodySites[runLoop.thisTrialN]]]
    warm = thermode1_temp2program[participant_settingsWarm[bodySites[runLoop.thisTrialN]]]
    """
    8e. Prepare the scanner trigger, set clock(s), and wait for dummy scans
    """
    ###############################################################################################
    # Experimenter fMRI Start Instruction ____________________________________________________
    ###############################################################################################
    start = visual.TextStim(win, text=start_msg, height=.05, color=win.rgb + 0.5)
    start.draw()  # Automatically draw every frame

    # Experimenter: Check to make sure the program is loaded if the first trial is a heat stimulation trial 
    if thisTrial['trial_type'] == 1:
        print("Loading Medoc Stimulation Program ", str(thisTrial['trial_type']))
        thermodeCommand = thermode1_temp2program[participant_settingsHeat[bodySites[runLoop.thisTrialN]]]
        tp_selected = 1
        if thermode_exists == 1 & tp_selected ==1:
            win.callOnFlip(sendCommand, 'select_tp', thermodeCommand)
    if thisTrial['trial_type'] == 2:
        print("Loading Medoc Stimulation Program ", str(thisTrial['trial_type']))
        thermodeCommand = thermode1_temp2program[participant_settingsWarm[bodySites[runLoop.thisTrialN]]]
        tp_selected = 1
        if thermode_exists == 1 & tp_selected ==1:
            win.callOnFlip(sendCommand, 'select_tp', thermodeCommand)
    win.flip()
    tp_selected = 0
    fmriStart = globalClock.getTime()
    
    if autorespond != 1:
        # Trigger
        event.waitKeys(keyList = 's') # experimenter start key - safe key before fMRI trigger
        event.waitKeys(keyList='5')   # fMRI trigger
        fmriStart = globalClock.getTime()
        TR = 0.46
        core.wait(TR*6)         # Wait 6 TRs, Dummy Scans

    print("Starting run " + str(runLoop.thisTrialN+1))
    print("Cue Biopac Channel " + str(run_start))
    if biopac_exists == 1:
        biopac.setData(biopac, 0)
        biopac.setData(biopac, run_start)
    routineTimer.reset()

    if thisTrial != None:
        for paramName in thisTrial:
            exec('{} = thisTrial[paramName]'.format(paramName))  
    for thisTrial in trials:
        currentLoop = trials
        # abbreviate parameter names if possible (e.g. rgb = thisTrial.rgb)
        if thisTrial != None:
            for paramName in thisTrial:
                exec('{} = thisTrial[paramName]'.format(paramName))

        # Setup the next trial if it is a thermal stimulation condition    
        next_trial = trials.getFutureTrial()
        if (trials.nRemaining > 0 and next_trial['trial_type'] in {1, 2}):
            print("Loading Program")
            if (next_trial['trial_type'] == 1):
                print("Loading Thermal Program for Heat to", bodySites[runLoop.thisTrialN])
                thermodeCommand = thermode1_temp2program[participant_settingsHeat[bodySites[runLoop.thisTrialN]]]
                tp_selected = 1

                # if thermode_exists == 1:
                #     sendCommand('select_tp', thermodeCommand)  
            elif (next_trial['trial_type'] == 2):
                print("Loading Thermal Program for Warm to", bodySites[runLoop.thisTrialN])
                thermodeCommand = thermode1_temp2program[participant_settingsWarm[bodySites[runLoop.thisTrialN]]]
                tp_selected = 1
                # if thermode_exists == 1:
                #     sendCommand('select_tp', thermodeCommand)

        ## Thermal Stimulation Trials:        
        if trial_type in {1, 2, 4}:
            startTime = timeit.default_timer()
            if (trial_type == 1):
                BiopacChannel = bodysite_word2heatcode[bodySites[runLoop.thisTrialN]]
                #BiopacChannel = thermode1
                bodySiteData = bodySites[runLoop.thisTrialN]
                temperature = participant_settingsHeat[bodySites[runLoop.thisTrialN]]
                thermodeCommand = hot
            elif (trial_type == 2):
                BiopacChannel = bodysite_word2warmcode[bodySites[runLoop.thisTrialN]]
                # BiopacChannel = thermode2
                bodySiteData = bodySites[runLoop.thisTrialN]
                temperature = participant_settingsWarm[bodySites[runLoop.thisTrialN]]
                thermodeCommand = warm
            elif (trial_type == 4):
                BiopacChannel = rest
                bodySiteData = None
                temperature = None
            fix_cross.color = "white"

            # ------Prepare to start Routine "StimTrial"-------
            continueRoutine = True
            routineTimer.reset()
            if trial_type == 4:
                stimtrialTime = nonstimtrialTime
            routineTimer.add(stimtrialTime)
            # update component parameters for each repeat
            # keep track of which components have finished
            StimTrialComponents = [fix_cross]
            for thisComponent in StimTrialComponents:
                thisComponent.tStart = None
                thisComponent.tStop = None
                thisComponent.tStartRefresh = None
                thisComponent.tStopRefresh = None
                if hasattr(thisComponent, 'status'):
                    thisComponent.status = NOT_STARTED
            # reset timers
            t = 0
            _timeToFirstFrame = win.getFutureFlipTime(clock="now")
            StimTrialClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
            frameN = -1
            # -------Run Routine "StimTrial"-------
            onset = globalClock.getTime() - fmriStart   
            while continueRoutine and routineTimer.getTime() > 0:
                # get current time
                t = StimTrialClock.getTime()
                tThisFlip = win.getFutureFlipTime(clock=StimTrialClock)
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
                    if trial_type == 1:
                        win.callOnFlip(print, "Starting Heat Stimulation to the", bodySites[runLoop.thisTrialN])
                        if thermode_exists == 1:
                            win.callOnFlip(sendCommand, 'trigger')
                    elif trial_type == 2:
                        win.callOnFlip(print, "Starting Warm Stimulation to the", bodySites[runLoop.thisTrialN])
                        if thermode_exists == 1:
                            win.callOnFlip(sendCommand, 'trigger')
                    elif trial_type == 4:
                        win.callOnFlip(print, "Resting")
                    win.callOnFlip(print, "Cue Biopac channel " + str(BiopacChannel))
                    if biopac_exists == 1:
                        win.callOnFlip(biopac.setData, biopac, 0)
                        win.callOnFlip(biopac.setData, biopac, BiopacChannel)
                    fix_cross.setAutoDraw(True)
                if fix_cross.status == STARTED:
                    if thermode_exists == 1 and tp_selected == 1 and trial_type ==4 and tThisFlipGlobal > fix_cross.tStartRefresh + poststimTime-frameTolerance:
                        sendCommand('select_tp', thermodeCommand)
                        tp_selected = 0  
                    # is it time to stop? (based on global clock, using actual start)
                    if tThisFlipGlobal > fix_cross.tStartRefresh + stimtrialTime-frameTolerance:
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
                for thisComponent in StimTrialComponents:
                    if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                        continueRoutine = True
                        break  # at least one component has not yet finished
                # refresh the screen
                if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                    win.flip()

            # -------Ending Routine "StimTrial"-------
            for thisComponent in StimTrialComponents:
                if hasattr(thisComponent, "setAutoDraw"):
                    thisComponent.setAutoDraw(False)
            trials.addData('fix_cross.started', fix_cross.tStartRefresh)
            trials.addData('fix_cross.stopped', fix_cross.tStopRefresh)
            # duration = timeit.default_timer()-startTime # Consider comparing with TTLs output.
            bodymap_trial = []
            # bodymap_trial.extend((fix_cross.tStartRefresh - fmriStart, t, trial_type, bodySiteData, temperature))
            bodymap_trial.extend((onset, t, trial_type, bodySiteData, temperature))
            bodymap_bids_data.append(bodymap_trial)
            routineTimer.reset()

        ## Nonstimulus Trials
        elif (trial_type == 3):
            startTime = timeit.default_timer()
            print("Starting Imagine Site")
            BodySiteCue = BodySiteImg
            BodySiteCue.pos = (0,0)
            NonStimTrialText.text="Picture your " + bodySites[runLoop.thisTrialN].lower() + " being held up against a glowing hot metal or fire. \nVisualize the skin on your " + bodySites[runLoop.thisTrialN].lower() + " sizzling, melting, and bubbling."
            BiopacCueChannel = bodysite_word2cuecode[bodySites[runLoop.thisTrialN]]
            BiopacImagineChannel = bodysite_word2imaginecode[bodySites[runLoop.thisTrialN]]
            fix_cross.color = "orange" 
            bodySiteData = bodySites[runLoop.thisTrialN]
            temperature = None

            # ------Prepare to start Routine "NonStimTrial"-------
            continueRoutine = True
            routineTimer.reset()
            routineTimer.add(nonstimtrialTime)
            # update component parameters for each repeat
            # keep track of which components have finished
            NonStimTrialComponents = [BodySiteCue, NonStimTrialText, fix_cross]
            for thisComponent in NonStimTrialComponents:
                thisComponent.tStart = None
                thisComponent.tStop = None
                thisComponent.tStartRefresh = None
                thisComponent.tStopRefresh = None
                if hasattr(thisComponent, 'status'):
                    thisComponent.status = NOT_STARTED
            # reset timers
            t = 0
            _timeToFirstFrame = win.getFutureFlipTime(clock="now")
            NonStimTrialClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
            frameN = -1
            
            # -------Run Routine "NonStimTrial"-------
            onset = globalClock.getTime() - fmriStart
            while continueRoutine and routineTimer.getTime() > 0:
                # get current time
                t = NonStimTrialClock.getTime()
                tThisFlip = win.getFutureFlipTime(clock=NonStimTrialClock)
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
                    win.callOnFlip(print, "Cue Biopac channel " + str(BiopacCueChannel))
                    if biopac_exists == 1:
                        win.callOnFlip(biopac.setData, biopac, 0)
                        win.callOnFlip(biopac.setData, biopac, BiopacCueChannel)
                    BodySiteCue.setAutoDraw(True)
                if BodySiteCue.status == STARTED:
                    # is it time to stop? (based on global clock, using actual start)
                    if tThisFlipGlobal > BodySiteCue.tStartRefresh + imaginationCueTime-frameTolerance:
                        # keep track of stop time/frame for later
                        BodySiteCue.tStop = t  # not accounting for scr refresh
                        BodySiteCue.frameNStop = frameN  # exact frame index
                        win.timeOnFlip(BodySiteCue, 'tStopRefresh')  # time at next scr refresh
                        BodySiteCue.setAutoDraw(False)
            
                # *NonStimTrialText* updates
                if NonStimTrialText.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    NonStimTrialText.frameNStart = frameN  # exact frame index
                    NonStimTrialText.tStart = t  # local t and not account for scr refresh
                    NonStimTrialText.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(NonStimTrialText, 'tStartRefresh')  # time at next scr refresh
                    NonStimTrialText.setAutoDraw(True)
                if NonStimTrialText.status == STARTED:
                    # is it time to stop? (based on global clock, using actual start)
                    if tThisFlipGlobal > NonStimTrialText.tStartRefresh + imaginationCueTime-frameTolerance:
                        # keep track of stop time/frame for later
                        NonStimTrialText.tStop = t  # not accounting for scr refresh
                        NonStimTrialText.frameNStop = frameN  # exact frame index
                        win.timeOnFlip(NonStimTrialText, 'tStopRefresh')  # time at next scr refresh
                        NonStimTrialText.setAutoDraw(False)

                # *fix_cross* updates
                if fix_cross.status == NOT_STARTED and tThisFlip >= imaginationCueTime-frameTolerance:
                    # keep track of start time/frame for later
                    fix_cross.frameNStart = frameN  # exact frame index
                    fix_cross.tStart = t  # local t and not account for scr refresh
                    fix_cross.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(fix_cross, 'tStartRefresh')  # time at next scr refresh
                    win.callOnFlip(print, "Cue Biopac channel " + str(BiopacImagineChannel))
                    if biopac_exists == 1:
                        win.callOnFlip(biopac.setData, biopac, 0)
                        win.callOnFlip(biopac.setData, biopac, BiopacImagineChannel)
                    fix_cross.setAutoDraw(True)
                if fix_cross.status == STARTED:
                    if thermode_exists == 1 and tp_selected == 1 and tThisFlipGlobal > BodySiteCue.tStartRefresh + poststimTime-frameTolerance:
                        sendCommand('select_tp', thermodeCommand)
                        tp_selected = 0  
                    # is it time to stop? (based on global clock, using actual start)
                    if tThisFlipGlobal > fix_cross.tStartRefresh + imaginationTrialTime-frameTolerance:
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
                for thisComponent in NonStimTrialComponents:
                    if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                        continueRoutine = True
                        break  # at least one component has not yet finished
                
                # refresh the screen
                if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                    win.flip()
            
            # -------Ending Routine "NonStimTrial"-------
            TrialEndTime = timeit.default_timer()-startTime
            print("TrialEndTime: " + str(TrialEndTime))
            print("CueOff Biopac Channel " + str(BiopacImagineChannel))
            for thisComponent in NonStimTrialComponents:
                if hasattr(thisComponent, "setAutoDraw"):
                    thisComponent.setAutoDraw(False)
            trials.addData('BodySiteCue.started', BodySiteCue.tStartRefresh)
            trials.addData('BodySiteCue.stopped', BodySiteCue.tStopRefresh)
            trials.addData('NonStimTrialText.started', NonStimTrialText.tStartRefresh)
            trials.addData('NonStimTrialText.stopped', NonStimTrialText.tStopRefresh)
            trials.addData('fix_cross.started', fix_cross.tStartRefresh)
            trials.addData('fix_cross.stopped', fix_cross.tStopRefresh)
            cue_duration = fix_cross.tStartRefresh-BodySiteCue.tStartRefresh
            trial_duration = t - cue_duration
            bodymap_trial = []
            # bodymap_trial.extend((BodySiteCue.tStartRefresh - fmriStart, cue_duration, "3-cue", bodySiteData, temperature))
            bodymap_trial.extend((onset, cue_duration, "3-cue", bodySiteData, temperature))
            bodymap_bids_data.append(bodymap_trial)
            bodymap_trial = []
            bodymap_trial.extend((onset + cue_duration, trial_duration, "3-trial", bodySiteData, temperature))
            bodymap_bids_data.append(bodymap_trial)
            routineTimer.reset()
            thisExp.nextEntry()
            # completed 42 repeats of 'trials'
    """
    8f. Begin post-run self-report questions
    """        
    ############ ASK PAIN VALENCE #######################################
    # ------Prepare to start Routine "ValenceRating"-------
    continueRoutine = True
    routineTimer.add(ratingTime)
    # update component parameters for each repeat
    # setup some python lists for storing info about the mouse
    
    ValenceMouse = event.Mouse(win=win, visible=False) # Re-initialize ValenceMouse
    ValenceMouse.setPos((0,0))
    timeAtLastInterval = 0
    mouseX = 0
    oldMouseX = 0
    ValenceRating.width = 0
    ValenceRating.pos = (0,0)
    
    # keep track of which components have finished
    ValenceRatingComponents = [ValenceMouse, ValenceRating, ValenceBlackTriangle, ValenceAnchors, ValencePrompt]
    for thisComponent in ValenceRatingComponents:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    ValenceRatingClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    frameN = -1

    # -------Run Routine "ValenceRating"-------
    while continueRoutine:
        # get current time
        t = ValenceRatingClock.getTime()
        tThisFlip = win.getFutureFlipTime(clock=ValenceRatingClock)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame

        timeNow = globalClock.getTime()
        if (timeNow - timeAtLastInterval) > TIME_INTERVAL:
            mouseRel=ValenceMouse.getRel()
            mouseX=oldMouseX + mouseRel[0]
        ValenceRating.pos = (mouseX/2,0)
        ValenceRating.width = abs(mouseX)
        if mouseX > sliderMax:
            mouseX = sliderMax
        if mouseX < sliderMin:
            mouseX = sliderMin
        timeAtLastInterval = timeNow
        oldMouseX=mouseX
        sliderValue = ((mouseX - sliderMin) / (sliderMax - sliderMin) * 200)-100

        # *ValenceMouse* updates
        if ValenceMouse.status == NOT_STARTED and t >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            ValenceMouse.frameNStart = frameN  # exact frame index
            ValenceMouse.tStart = t  # local t and not account for scr refresh
            ValenceMouse.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(ValenceMouse, 'tStartRefresh')  # time at next scr refresh
            ValenceMouse.status = STARTED
            ValenceMouse.mouseClock.reset()
            prevButtonState = ValenceMouse.getPressed()  # if button is down already this ISN'T a new click
        if ValenceMouse.status == STARTED:  # only update if started and not finished!
            if tThisFlipGlobal > ValenceMouse.tStartRefresh + ratingTime-frameTolerance:
                # keep track of stop time/frame for later
                ValenceMouse.tStop = t  # not accounting for scr refresh
                ValenceMouse.frameNStop = frameN  # exact frame index
                ValenceMouse.status = FINISHED
            buttons = ValenceMouse.getPressed()
            if buttons != prevButtonState:  # button state changed?
                prevButtonState = buttons
                if sum(buttons) > 0:  # state changed to a new click
                    # abort routine on response
                    continueRoutine = False

        # *ValenceRating* updates
        if ValenceRating.status == NOT_STARTED and t >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            ValenceRating.frameNStart = frameN  # exact frame index
            ValenceRating.tStart = t  # local t and not account for scr refresh
            ValenceRating.tStartRefresh = tThisFlipGlobal  # on global time
            win.callOnFlip(print, "Show Valence Rating")
            if biopac_exists == 1:
                win.callOnFlip(biopac.setData, biopac, 0)
                win.callOnFlip(biopac.setData, biopac, valence_rating)
            win.timeOnFlip(ValenceRating, 'tStartRefresh')  # time at next scr refresh
            ValenceRating.setAutoDraw(True)
        if ValenceRating.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > ValenceRating.tStartRefresh + ratingTime-frameTolerance:
                # keep track of stop time/frame for later
                ValenceRating.tStop = t  # not accounting for scr refresh
                ValenceRating.frameNStop = frameN  # exact frame index
                win.timeOnFlip(ValenceRating, 'tStopRefresh')  # time at next scr refresh
                ValenceRating.setAutoDraw(False)
        
        # *ValenceBlackTriangle* updates
        if ValenceBlackTriangle.status == NOT_STARTED and t >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            ValenceBlackTriangle.frameNStart = frameN  # exact frame index
            ValenceBlackTriangle.tStart = t  # local t and not account for scr refresh
            ValenceBlackTriangle.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(ValenceBlackTriangle, 'tStartRefresh')  # time at next scr refresh
            ValenceBlackTriangle.setAutoDraw(True)
        if ValenceBlackTriangle.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > ValenceBlackTriangle.tStartRefresh + ratingTime-frameTolerance:
                # keep track of stop time/frame for later
                ValenceBlackTriangle.tStop = t  # not accounting for scr refresh
                ValenceBlackTriangle.frameNStop = frameN  # exact frame index
                win.timeOnFlip(ValenceBlackTriangle, 'tStopRefresh')  # time at next scr refresh
                ValenceBlackTriangle.setAutoDraw(False)

        # *ValenceAnchors* updates
        if ValenceAnchors.status == NOT_STARTED and t >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            ValenceAnchors.frameNStart = frameN  # exact frame index
            ValenceAnchors.tStart = t  # local t and not account for scr refresh
            ValenceAnchors.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(ValenceAnchors, 'tStartRefresh')  # time at next scr refresh
            ValenceAnchors.setAutoDraw(True)
        if ValenceAnchors.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > ValenceAnchors.tStartRefresh + ratingTime-frameTolerance:
                # keep track of stop time/frame for later
                ValenceAnchors.tStop = t  # not accounting for scr refresh
                ValenceAnchors.frameNStop = frameN  # exact frame index
                win.timeOnFlip(ValenceAnchors, 'tStopRefresh')  # time at next scr refresh
                ValenceAnchors.setAutoDraw(False)

        # *ValencePrompt* updates
        if ValencePrompt.status == NOT_STARTED and t >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            ValencePrompt.frameNStart = frameN  # exact frame index
            ValencePrompt.tStart = t  # local t and not account for scr refresh
            ValencePrompt.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(ValencePrompt, 'tStartRefresh')  # time at next scr refresh
            ValencePrompt.setAutoDraw(True)
        if ValencePrompt.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > ValencePrompt.tStartRefresh + ratingTime-frameTolerance:
                # keep track of stop time/frame for later
                ValencePrompt.tStop = t  # not accounting for scr refresh
                ValencePrompt.frameNStop = frameN  # exact frame index
                win.timeOnFlip(ValencePrompt, 'tStopRefresh')  # time at next scr refresh
                ValencePrompt.setAutoDraw(False)

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
        for thisComponent in ValenceRatingComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:
            win.flip()

    # -------Ending Routine "ValenceRating"-------
    print("CueOff Channel " + str(valence_rating))
    for thisComponent in ValenceRatingComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    # store data for thisExp (ExperimentHandler)
    thisExp.addData('ValenceRating.response', sliderValue)
    thisExp.addData('ValenceRating.rt', timeNow-ValenceRating.tStart)
    thisExp.nextEntry()
    thisExp.addData('ValenceRating.started', ValenceRating.tStart)
    thisExp.addData('ValenceRating.stopped', ValenceRating.tStop)
    bodymap_bids_data.append(["Valence Rating:", sliderValue])
    # the Routine "ValenceRating" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()

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
    bodymap_bids_data.append(["Intensity Rating:", sliderValue])
    # the Routine "IntensityRating" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()

    ############ ASK OVERALL LEVEL OF PHYSICAL DISCOMFORT #################
    # ------Prepare to start Routine "ComfortRating"-------
    continueRoutine = True
    routineTimer.add(ratingTime)
    # update component parameters for each repeat
    # ComfortRating.reset()
    ComfortMouse = event.Mouse(win=win, visible=False) # Re-initialize ComfortMouse
    ComfortMouse.setPos((0,0))
    timeAtLastInterval = 0
    mouseX = 0
    oldMouseX = 0
    ComfortRating.width = 0
    ComfortRating.pos = (0,0)

    # keep track of which components have finished
    ComfortRatingComponents = [ComfortMouse, ComfortRating, ComfortBlackTriangle, ComfortAnchors, ComfortPrompt]
    for thisComponent in ComfortRatingComponents:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    ComfortRatingClock.reset(-_timeToFirstFrame)  # t0 is time of first possible flip
    frameN = -1

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
        sliderValue = (mouseX - sliderMin) / (sliderMax - sliderMin) * 100
        ## 1/27/2022: This is actually a bipolar question so the data recording should be this:
        # sliderValue = ((mouseX - sliderMin) / (sliderMax - sliderMin) * 200)-100

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
    bodymap_bids_data.append(["Comfort Rating:", sliderValue])
    # the Routine "ComfortRating" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()

    ########################## END SELF REPORT RUNS #######################################################
    """
    9. Save Run File
    """
    # file_savename = os.sep.join([main_dir, 'data', session_info['session_id'], 'practice.csv'])
    # Data file name stem = absolute path + name; later add .psyexp, .csv, .log, etc
    # each _%s refers to the respective field in the parentheses
    ## This needs to be at the end of the run
    bids_run_filename = sub_dir + os.sep + u'sub-%05d_ses-%02d_task-%s_acq-%s_run-%s_events.tsv' % (int(expInfo['subject number']), int(expInfo['session']), expName, bodySites[runLoop.thisTrialN].replace(" ", "").lower(), str(runLoop.thisTrialN+1))
    bodymap_bids_data = pd.DataFrame(bodymap_bids_data, columns = ['onset','duration','trial_type','body_site','temp'])
    bodymap_bids_data.to_csv(bids_run_filename, sep="\t")

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
if biopac_exists == 1:
    biopac.setData(biopac, 0)
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