# version for getting ready d
from __future__ import division, absolute_import
from psychopy import locale_setup
from psychopy import prefs
import argparse
from collections import OrderedDict
import sys
import numpy as np
import random
import os
import glob
import random, copy, time
import pandas as pd
import serial

#prefs.general['audioLib'] = ['pyo']
from psychopy import sound, visual, data, event, core, gui, logging, clock

biopac_exists = 1
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
fixation=53
audio1=54
audio2=55
visual3=56
checker4=57
visual5=58
audio6=59
audio7=60
audio8=61
visual9=62
audio10=63
audio11=64
checker12=65
visual13=66
visual14=67
visual15=68
visual16=69
visual17=70
visual18=71
visual19=72
visual20=73
checker21=74
visual22=75
visual23=76
audio24=77
audio25=78
visual26=79
visual27=80
visual28=81
visual29=82
visual30=83
audio31=84
visual32=85
checker33=86
visual34=87
visual35=88
visual36=89
visual37=90
visual38=91
visual39=92
audio40=93
audio41=94
checker42=95
audio43=96
visual44=97
visual45=98
visual46=99
visual47=100
checker48=101
visual49=102
audio50=103
checker51=104
audio52=105
checker53=106
visual54=107
visual55=108
audio56=109
visual57=110
visual58=111
visual59=112
checker60=113
visual61=114
visual62=115
visual63=116
checker64=117
visual65=118
visual66=119
audio67=120
audio68=121
checker69=122
checker70=123
checker71=124
audio72=125
audio73=126
checker74=127
audio75=128
checker76=129
audio77=130
visual78=131
audio79=132
audio80=133
visual81=134
visual82=135
visual83=136
checker84=137
visual85=138
visual86=139
visual87=140
audio88=141
checker89=142
checker90=143
checker91=144
visual92=145
audio93=146
checker94=147
visual95=148
audio96=149
visual97=150
audio98=151
audio99=152
audio100=153
end=154

word2biopaccode = {
"fixation": fixation,
"audio1": audio1,
"audio2": audio2,
"visual3": visual3,
"checker4": checker4,
"visual5": visual5,
"audio6": audio6,
"audio7": audio7,
"audio8": audio8,
"visual9": visual9,
"audio10": audio10,
"audio11": audio11,
"checker12": checker12,
"visual13": visual13,
"visual14": visual14,
"visual15": visual15,
"visual16": visual16,
"visual17": visual17,
"visual18": visual18,
"visual19": visual19,
"visual20": visual20,
"checker21": checker21,
"visual22": visual22,
"visual23": visual23,
"audio24": audio24,
"audio25": audio25,
"visual26": visual26,
"visual27": visual27,
"visual28": visual28,
"visual29": visual29,
"visual30": visual30,
"audio31": audio31,
"visual32": visual32,
"checker33": checker33,
"visual34": visual34,
"visual35": visual35,
"visual36": visual36,
"visual37": visual37,
"visual38": visual38,
"visual39": visual39,
"audio40": audio40,
"audio41": audio41,
"checker42": checker42,
"audio43": audio43,
"visual44": visual44,
"visual45": visual45,
"visual46": visual46,
"visual47": visual47,
"checker48": checker48,
"visual49": visual49,
"audio50": audio50,
"checker51": checker51,
"audio52": audio52,
"checker53": checker53,
"visual54": visual54,
"visual55": visual55,
"audio56": audio56,
"visual57": visual57,
"visual58": visual58,
"visual59": visual59,
"checker60": checker60,
"visual61": visual61,
"visual62": visual62,
"visual63": visual63,
"checker64": checker64,
"visual65": visual65,
"visual66": visual66,
"audio67": audio67,
"audio68": audio68,
"checker69": checker69,
"checker70": checker70,
"checker71": checker71,
"audio72": audio72,
"audio73": audio73,
"checker74": checker74,
"audio75": audio75,
"checker76": checker76,
"audio77": audio77,
"visual78": visual78,
"audio79": audio79,
"audio80": audio80,
"visual81": visual81,
"visual82": visual82,
"visual83": visual83,
"checker84": checker84,
"visual85": visual85,
"visual86": visual86,
"visual87": visual87,
"audio88": audio88,
"checker89": checker89,
"checker90": checker90,
"checker91": checker91,
"visual92": visual92,
"audio93": audio93,
"checker94": checker94,
"visual95": visual95,
"audio96": audio96,
"visual97": visual97,
"audio98": audio98,
"audio99": audio99,
"audio100": audio100,
"end": end
}

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
    # biopac.configIO(FIOAnalog=0, EIOAnalog=0)
    # for FIONUM in range(8):
    #     biopac.setFIOState(fioNum = FIONUM, state=0)
    # Set all FIO bits to digital output and set to low (i.e. “0")
    # The list in square brackets represent what’s desired for the FIO, EIO, CIO ports. We will only change the FIO port's state.
    biopac.configIO(FIOAnalog=0, EIOAnalog=0)
    biopac.setData(biopac, byte=0)
# PARSE INPUTS - test or not
# parser=argparse.ArgumentParser(description= 'This script runs a psychopy version of the pinel task for an fmri experiment.')
# parser.add_argument('--test',action='store_true',default=False,help="Indicate whether we're testing and should expect scanner triggers. Otherwise start experiment with spacebar.")
# args = parser.parse_args()

# CREATE DIALOGUE SCREEN - enter subject ID
config_dialog = gui.Dlg(title="Experiment Info")
# config_dialog = psy.gui.Dlg(title="Experiment Info")
config_dialog.addField("Subject ID: ")
config_dialog.addField("Session: ")
config_dialog.addField("Test? 1=yes; 0=no: ")
config_dialog.show()

# create dialogue screen that will show if file already exists- must choose to manually overwrite
# exists_dialog= psy.gui.Dlg(title="File Already Exists", labelButtonOK=u'Yes/overwrite', labelButtonCancel=u'Quit Program!',)
exists_dialog = gui.Dlg(title="File Already Exists", labelButtonOK=u'Yes/overwrite', labelButtonCancel=u'Quit Program!')
exists_dialog.addText('File name already exists. Are you sure you want to overwrite?')

# if user enters both subID and run number save these, otherwise exit system
if config_dialog.OK:
    subID = config_dialog.data[0]
    session = config_dialog.data[1]
    test = int(config_dialog.data[2])  # make sure this is int
else:
    sys.exit("Canceled at configuration dialog.")

# create file w/subId in name
# change this so that filename is from teh gui- and needs extension. so if not . in
if test == int(1):
    fName = 'Pinel_sub-%s_task-pinel_ses-%s_TEST.txt' % (subID,session)
elif test == int(0):
    fName = 'Pinel_sub-%s_task-pinel_ses-%s.txt' % (subID,session)

# SET EXPERIMENT GLOBALS
base_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(base_dir, 'data', 'sub-%05d' % (int(subID)), 'ses-%02d' % (int(session)))
stim_dir = os.path.join(base_dir, 'stim')

# triggers
testTrigger = 'space'
expTrigger = '5'  # k
quitTrigger = 'q'
# stylistic settings
textColor = 'gray'
textFont = 'Arial'
textHeight = .20
testWinSize = (640, 480)  # 1280, 1024
expWinSize = (1920, 1080)
alignText = 'center'
alignVert = 'center'

# set durations for different stimuli types
visual_dur = .250
visual_black_dur = .100
click_dur = .800
checker_dur = 1.3
blank_dur = 1.3

# SETUP DATAFILE
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# make sure we don't overwrite a file- must click okay to overwrite
fPath = os.path.join(data_dir, fName)
if os.path.exists(fPath):
    exists_dialog.show()
    if exists_dialog.OK:
        data_file = open(fPath, 'w')
    else:
        sys.exit('Program ending!')
else:
    data_file = open(fPath, 'w')

# SETUP DEVICES
if test == 1:
    winSize = testWinSize
    fullScr = True
    screen = 0
else:
    winSize = expWinSize
    fullScr = True
    screen = 0

window = visual.Window(size=winSize, fullscr=fullScr, screen=screen, allowGUI=True, color='black',
                       monitor='testMonitor')
window.setRecordFrameIntervals(True)
logging.console.setLevel(logging.WARNING)
clock = core.Clock()

# set triggers
if test == 1:
    validTrigger = testTrigger
else:
    validTrigger = expTrigger
    #serial_settings = {
        ## 'mount': '/dev/tty.USA19H141P1.1',
        #'mount': '/dev/tty.KeySerial1',
        #'baud': 115200,
        #'timeout': 0}  # .0001
    #ser = serial.Serial(serial_settings['mount'], serial_settings['baud'], timeout=serial_settings['timeout'])
    #ser.flushInput()  # reset_input_buffer()

# All Visual Tasks
# calc tasks
calc1 = ['calculate', 'sixteen', 'minus', 'eight']
calc2 = ['calculate', 'ten', 'minus', 'two']
calc3 = ['calculate', 'eleven', 'minus', 'nine']
calc4 = ['calculate', 'twelve', 'minus', 'four']
calc5 = ['calculate', 'nineteen', 'minus', 'six']
calc6 = ['calculate', 'sixteen', 'minus', 'two']
calc7 = ['calculate', 'thirteen', 'minus', 'seven']
calc8 = ['calculate', 'nineteen', 'minus', 'seven']
calc9 = ['calculate', 'eleven', 'minus', 'three']
calc10 = ['calculate', 'seventeen', 'minus', 'six']
vis_subtraction_pre = [calc1, calc2, calc3, calc4, calc5, calc6, calc7, calc8, calc9, calc10]

# preload vis_subtraction stimuli, create stimuli objects
vis_subtraction = []
for item in vis_subtraction_pre:  # ex calc1, calc2
    for word in range(len(item)):  # for i in 0-3
        item[word] = visual.TextStim(win=window, text=item[word],
                                     color=textColor, alignHoriz=alignText, font=textFont, height=textHeight)
    vis_subtraction.append(item)

# visual reading tasks
read1 = ['the storm', 'frightened', 'the animals', 'at the zoo']
read2 = ['the cats', 'are looking', 'for a bird', 'on the wall']
read3 = ['the keep', 'of the castle', 'falls', 'into ruin']
read4 = ['we saw', 'the march', 'from', 'the balcony']
read5 = ['bears', 'are fond of', 'salmon', 'and honey']
read6 = ['in town', 'we easily', 'find', 'a taxi']
read7 = ['the cold', 'of winter', 'froze', 'the lake']
read8 = ['there are', 'many', 'bridges', 'in Paris']
read9 = ['the rain', 'has made', 'the road', 'dangerous']
read10 = ['roses', 'are nice', 'but', 'they prick']
sentences_pre = [read1, read2, read3, read4, read5, read6, read7, read8, read9, read10]

# preload vis_sentences stimuli, create stimuli objects
sentences = []
for item in sentences_pre:  # ex calc1, calc2
    for word in range(len(item)):  # for i in 0-3
        item[word] = visual.TextStim(win=window, text=item[word],
                                     color=textColor, alignHoriz=alignText, font=textFont, height=textHeight)
    sentences.append(item)

# visual motor tasks
visual_left = ['press', 'three times', 'on the', 'left button']
visual_right = ['press', 'three times', 'on the', 'right button']
vis_motor_pre = [visual_left, visual_right]
vis_motor = []
for item in vis_motor_pre:  # ex calc1, calc2
    for word in range(len(item)):  # for i in 0-3
        item[word] = visual.TextStim(win=window, text=item[word],
                                     color=textColor, font=textFont, height=textHeight, alignHoriz=alignText)
    vis_motor.append(item)

# Audio Stimuli
# create lists of audio stimuli
subtraction = glob.glob(os.path.join(stim_dir, 'calc*'))  # make list of image path names
audio_sentence = glob.glob(os.path.join(stim_dir, 'ph*'))  # make list of image path names
press_left = os.path.join(stim_dir, 'clic3G.wav')
press_right = os.path.join(stim_dir, 'clic3D.wav')

# Checkerboard image stimuli
# Make two wedges (in opposite contrast) and alternate them for flashing
vert_pic1 = os.path.join(stim_dir, 'checherboardVnb.bmp')
vert_pic2 = os.path.join(stim_dir, 'checherboardVpb.bmp')
ho_pic1 = os.path.join(stim_dir, 'checherboardHnb.bmp')
ho_pic2 = os.path.join(stim_dir, 'checherboardHpb.bmp')

# create image objects for checkerboards
ho_check1 = visual.ImageStim(window, image=ho_pic1, name=os.path.split(ho_pic1)[-1],
                             pos=(0.0, 0.0))  # this stim changes too much for autologging to be useful
ho_check2 = visual.ImageStim(window, image=ho_pic2, name=os.path.split(ho_pic2)[-1],
                             pos=(0.0, 0.0))  # this stim changes too much for autologging to be useful
vert_check1 = visual.ImageStim(window, image=vert_pic1, name=os.path.split(vert_pic1)[-1],
                               pos=(0.0, 0.0))  # this stim changes too much for autologging to be useful
vert_check2 = visual.ImageStim(window, image=vert_pic2, name=os.path.split(vert_pic2)[-1],
                               pos=(0.0, 0.0))  # this stim changes too much for autologging to be useful
check = [vert_check1, vert_check2, ho_check1, ho_check2]  # list of stimuli objects for the images

# onset type
task_order = OrderedDict([
    ("audio1", audio_sentence[0]),
    ("audio2", audio_sentence[1]),
    ("visual3", "blank"),
    ("checker4", "ho_check"),
    ("visual5", visual_left),
    ("audio6", subtraction[0]),
    ("audio7", "press_left"),
    ("audio8", subtraction[1]),
    ("visual9", visual_right),
    ("audio10", "press_right"),
    ("audio11", subtraction[2]),
    ("checker12", "vert_check"),
    ("visual13", sentences[0]),
    ("visual14", vis_subtraction[0]),
    ("visual15", vis_subtraction[1]),
    ("visual16", sentences[1]),
    ("visual17", sentences[2]),
    ("visual18", "blank"),
    ("visual19", "blank"),
    ("visual20", vis_subtraction[2]),
    ("checker21", "ho_check"),
    ("visual22", visual_right),
    ("visual23", "blank"),
    ("audio24", "press_left"),
    ("audio25", "press_right"),
    ("visual26", vis_subtraction[3]),
    ("visual27", "blank"),
    ("visual28", "blank"),
    ("visual29", sentences[3]),
    ("visual30", visual_left),
    ("audio31", subtraction[3]),
    ("visual32", "blank"),
    ("checker33", "vert_check"),
    ("visual34", "blank"),
    ("visual35", "blank"),
    ("visual36", "blank"),
    ("visual37", sentences[4]),
    ("visual38", "blank"),
    ("visual39", "blank"),
    ("audio40", "press_right"),
    ("audio41", subtraction[4]),
    ("checker42", "vert_check"),
    ("audio43", audio_sentence[2]),
    ("visual44", "blank"),
    ("visual45", vis_subtraction[4]),
    ("visual46", sentences[5]),
    ("visual47", sentences[6]),
    ("checker48", "vert_check"),
    ("visual49", visual_left),
    ("audio50", subtraction[5]),
    ("checker51", "ho_check"),
    ("audio52", audio_sentence[3]),
    ("checker53", "vert_check"),
    ("visual54", vis_subtraction[5]),
    ("visual55", visual_left),
    ("audio56", audio_sentence[4]),
    ("visual57", vis_subtraction[6]),
    ("visual58", visual_right),
    ("visual59", sentences[7]),
    ("checker60", "ho_check"),
    ("visual61", "blank"),
    ("visual62", "blank"),
    ("visual63", "blank"),
    ("checker64", "ho_check"),
    ("visual65", sentences[8]),
    ("visual66", vis_subtraction[7]),
    ("audio67", audio_sentence[5]),
    ("audio68", audio_sentence[6]),
    ("checker69", "vert_check"),
    ("checker70", "vert_check"),
    ("checker71", "vert_check"),
    ("audio72", "press_right"),
    ("audio73", "press_right"),
    ("checker74", "ho_check"),
    ("audio75", audio_sentence[7]),
    ("checker76", "ho_check"),
    ("audio77", "press_left"),
    ("visual78", visual_left),
    ("audio79", audio_sentence[8]),
    ("audio80", subtraction[6]),
    ("visual81", "blank"),
    ("visual82", "blank"),
    ("visual83", vis_subtraction[8]),
    ("checker84", "ho_check"),
    ("visual85", sentences[9]),
    ("visual86", visual_right),
    ("visual87", visual_right),
    ("audio88", audio_sentence[9]),
    ("checker89", "vert_check"),
    ("checker90", "ho_check"),
    ("checker91", "ho_check"),
    ("visual92", "blank"),
    ("audio93", "press_left"),
    ("checker94", "vert_check"),
    ("visual95", "blank"),
    ("audio96", subtraction[7]),
    ("visual97", vis_subtraction[9]),
    ("audio98", "press_left"),
    ("audio99", subtraction[8]),
    ("audio100", subtraction[9])])



# print task_order
ITIs = [2.4, 3.3, 3.0, 2.7, 3.6, 3.0, 2.7, 3.0, 3.0, 3.0, 3.3, 2.4, 3.6, 2.7, 3.0, 3.3, 2.7, 3.0, 2.7, 3.3, 2.7, 3.6,
        3.0, 2.4, 3.6, 3.0, 2.4, 3.0, 3.6, 2.7, 3.3, 3.0, 3.0, 3.0, 3.0, 3.0, 2.4, 3.3, 3.0, 2.7, 3.3, 2.7, 3.6, 2.4,
        3.6, 2.7, 2.7, 3.0, 3.3, 2.7, 3.6, 3.0, 3.0, 3.0, 2.4, 3.3, 2.7, 3.3, 3.0, 3.0, 3.0, 3.3, 2.4, 3.3, 3.3, 3.0,
        3.0, 2.7, 3.3, 3.0, 2.7, 3.0, 3.0, 2.7, 3.3, 3.0, 3.0, 3.3, 2.7, 3.3, 3.0, 3.0, 2.4, 3.3, 3.0, 2.7, 3.0, 3.6,
        2.7, 3.0, 3.0, 2.7, 3.0, 3.3, 2.7, 3.6, 3.0, 2.4, 3.3, 0.0]

# CREATE SCREENS
fixation = visual.TextStim(win=window, name='fixation',
                           text='+',
                           color=textColor,
                           font=textFont,
                           height=textHeight)

Text = visual.TextStim(win=window, name='Text',
                       text="",
                       color=textColor,
                       font=textFont,
                       height=textHeight, alignHoriz=alignText)

wait_stim = visual.TextStim(win=window, name='waitText',
                            text="Waiting for scanner",
                            color=textColor,
                            font=textFont,
                            height=textHeight, alignHoriz=alignText)

end_msg = visual.TextStim(win=window, name='end_msg',
                          text='Thank you for participating!',
                          color=textColor,
                          font=textFont,
                          height=textHeight, alignHoriz=alignText)

# EXPERIMENT START
trigger = ''
wait_stim.draw()
if biopac_exists:
    window.callOnFlip(biopac.setData, biopac, 0)
    window.callOnFlip(biopac.setData, biopac, task_ID)
    window.callOnFlip(biopac.setData, biopac, 0)
window.flip()

# wait until trigger is pressed- or fMRI scanner trigger
while trigger != validTrigger:
    if test == 1:
        trigger = event.getKeys(keyList=['space'])
        if trigger:
            trigger = trigger[0]
    else:
        trigger = event.getKeys(keyList=['5']) #ser.read()
        if trigger:
            trigger = trigger[0]
window.mouseVisible = False
# start experiment timing
experimentStart = clock.getTime()

# counter for looping through ITI list
ITI_counter = 0

# create timer
timer = core.Clock()

# main experiment loop
for key, task in task_order.items():
    print
    key  # get rid of this
    if biopac_exists:
        window.callOnFlip(biopac.setData, biopac, 0)
        window.callOnFlip(biopac.setData, biopac, word2biopaccode[key])

    # if task is flashing checkerboard
    if "checker" in key:
        name = task
        t = 0
        rotationRate = 0.1  # revs per sec
        flashPeriod = 0.1  # seconds for one B-W cycle (ie 1/Hz)

        preztime = clock.getTime() - experimentStart
        trial_start = clock.getTime()
        timer.add(checker_dur)  # add 1.3 to the timer
        while timer.getTime() < 0:

            if "vert_check" in task:
                t = clock.getTime()
                if t % flashPeriod < flashPeriod / 4.0:  # more accurate to count frames
                    stim = check[0]
                else:
                    stim = check[1]

                stim.draw()
                window.flip()

            else:  # horizontal checkerboard
                t = clock.getTime()
                if t % flashPeriod < flashPeriod / 2.0:  # more accurate to count frames
                    stim = check[2]
                else:

                    stim = check[3]

                stim.draw()
                window.flip()

            duration = clock.getTime() - trial_start

        # Present SOA from ITIs List
        Text.text = '+'
        Text.draw()
        if biopac_exists:
            window.callOnFlip(biopac.setData, biopac, 0)
            window.callOnFlip(biopac.setData, biopac, word2biopaccode['fixation'])
        window.flip()
        timer.add(ITIs[ITI_counter] - duration)
        while timer.getTime() < 0:
            pass

            # if type is audio file
    elif "audio" in key:
        name = os.path.split(task)[-1]
        # audio press right task
        if "press_right" in task:
            # create sound stimuli
            audio_file = sound.Sound(press_right, stereo=True, hamming=True)

            # get duration of sound stimuli
            duration = audio_file.getDuration()

            # get presentation time and write to file
            preztime = clock.getTime() - experimentStart

            # play sound file
            audio_file.play()

            Text.text = ''
            Text.draw()
            window.flip()
            timer = core.Clock()
            timer.add(duration)  # is this supposed to be .8 or 1.3
            while timer.getTime() < 0:
                pass


        elif "press_left" in task:
            # create sound stimuli
            audio_file = sound.Sound(press_left, stereo=True, hamming=True)

            # get duration of sound stimuli
            duration = audio_file.getDuration()

            # get presentation time and write to file
            preztime = clock.getTime() - experimentStart

            # play sound file
            audio_file.play()

            Text.text = ''
            Text.draw()
            window.flip()
            timer = core.Clock()
            timer.add(duration)  # is this supposed to be .8 or 1.3
            while timer.getTime() < 0:
                pass

        # all other audio stimuli( sentences and subtraction)
        else:
            # create sound stimuli
            audio_file = sound.Sound(task, stereo=True, hamming=True)

            # get duration of sound stimuli
            duration = audio_file.getDuration()

            # get presentation time and write to file
            preztime = clock.getTime() - experimentStart

            temp = clock.getTime()
            # play sound file
            audio_file.play()

            Text.text = ''
            Text.draw()
            window.flip()
            timer = core.Clock()
            timer.add(duration)  # is this supposed to be .8 or 1.3
            while timer.getTime() < 0:
                pass
        
        # Present SOA
        Text.text = '+'
        Text.draw()
        window.flip()
        # audio_dur=(duration+ ITIs[ITI_counter])
        audio_dur = (ITIs[ITI_counter] - duration)
        timer = core.Clock()
        timer.add(audio_dur)
        while timer.getTime() < 0:
            pass

    # "visual" in key - ex sentences, subtraction, press left/right, blank
    else:
        name = str(task)
        # if blank
        if "blank" in task:
            Text.text = ''
            Text.draw()
            window.flip()
            trial_start = clock.getTime()
            preztime = clock.getTime() - experimentStart
            timer.add(blank_dur)  # is this supposed to be .8 or 1.3
            while timer.getTime() < 0:
                pass
            duration = clock.getTime() - trial_start

        else:
            preztime = clock.getTime() - experimentStart
            trial_start = clock.getTime()
            i = 0
            for word in task:
                print
                clock.getTime()
                word.draw()
                window.flip()
                temp = clock.getTime()
                timer.add(.25)
                while timer.getTime() < 0:
                    pass
                print
                clock.getTime() - temp

                if i < 3:
                    Text.text = ''
                    Text.draw()
                    window.flip()
                    temp = clock.getTime()
                    timer.add(.1)
                    while timer.getTime() < 0:
                        pass
                    print
                    clock.getTime() - temp
                i += 1

            # duration = clock.getTime()- preztime
            duration = clock.getTime() - trial_start
            print('Duration: %s' % duration)

        # Present SOA
        # duration = clock.getTime()- preztime
        Text.text = '+'
        Text.draw()
        if biopac_exists:
            window.callOnFlip(biopac.setData, biopac, 0)
            window.callOnFlip(biopac.setData, biopac, word2biopaccode['fixation'])
        window.flip()
        timer.add(ITIs[ITI_counter] - duration)
        while timer.getTime() < 0:
            pass

            # write run number, picture name and presentation time to file
    soa_num = "SOA%s" % str(ITI_counter + 1)
    data_file.write(str(key) + '\t' + str(preztime) + '\t' + str(duration) + '\t' + str(soa_num) + '\t' + str(
        ITIs[ITI_counter]) + '\n')

    ITI_counter += 1

    # quit program if key pressed during pinel task presentation
    if event.getKeys(keyList=['q']):
        window.close()
        core.quit()

# after all stimuli presented show end message
# message
end_msg.draw()
if biopac_exists:
    window.callOnFlip(biopac.setData, biopac, 0)
    window.callOnFlip(biopac.setData, biopac, word2biopaccode['end'])
    window.callOnFlip(biopac.setData, biopac, 0)
window.flip()
timer.add(2.0)
while timer.getTime()<0:
   pass
# cleanup section:
# make sure everything is saved
# make sure everything is closed down
# end experiment timing
experimentEnd = clock.getTime()
experimentDuration = experimentEnd - experimentStart 
data_file.write('this is the duration: ' + str(experimentDuration))
print("Experiment is finished")
data_file.close()




window.close()
core.quit()