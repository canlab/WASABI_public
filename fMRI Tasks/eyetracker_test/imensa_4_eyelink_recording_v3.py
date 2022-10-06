# === IMENSA PROJECT === 
# using ntp module. add actual time stamp and ntp time using server time. erase while loop during recording. Used 4/12~

""" 
0. General SETUP 
"""
# === 0a. Import Libraries ===
from __future__ import absolute_import, division
import numpy as np  # whole numpy lib is available, prepend 'np.'
from numpy import (sin, cos, tan, log, log10, pi, sqrt, deg2rad, rad2deg, eye, average, std, linspace, asarray)
from numpy.random import random, randint, normal, shuffle
import pandas as pd
import os, sys, time, ntplib
from string import ascii_letters, digits
import pylink
from EyeLinkCoreGraphicsPsychoPy import EyeLinkCoreGraphicsPsychoPy
from psychopy import locale_setup, sound, gui, visual, core, data, event, logging, clock, prefs
prefs.hardware['audioLib'] = ['PTB']
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED, STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)
from psychopy.hardware import keyboard


# === 0b. Constants and Togglers ===
debug = 0
eyelink_use = 1
expInfo = {'subject number': '60', 
'visit': '2', 
'condition': 'p', 
'run': 'm1'}

__author__ = "Byeol Kim"
__version__ = "0.3"
__computer__ = "DELL IMENSA stem PC"
__email__ = "byeol.kim.gr@dartmouth.edu"

# === 0e. Experimental Dialog Boxes and expInfo ===
expName = 'eyelink'
if not debug:
    dlg = gui.DlgFromDict(title="IMENSA study eyelink recording", dictionary=expInfo, sortKeys=False) 
    if not dlg.OK:
        core.quit()  # user pressed cancel
expInfo['date'] = data.getDateStr()[0:16]  # add a timestamp '2021_Dec_27_1947'
expInfo['expName'] = expName

# === 0f. Window setup ===
""" DBIC uses a Panasonic DW750 Projector with a native resolution of 1920x1200 (16:10), but it is configured at 1920x1080 (16:9) at DBIC. Configure a black window with a 16:9 aspect ratio during development (1280x720) and production (1920x1080)"""
win = visual.Window(size=[1280, 720], fullscr=False, screen=0, winType='pyglet', allowGUI=True, 
allowStencil=True, monitor='testMonitor', color='black', colorSpace='rgb', blendMode='avg', useFBO=True, units='height')

IntensityMouse = event.Mouse(win=win)

# === 1b. Directory setup ===
_thisDir = os.path.dirname(os.path.abspath(__file__)) 
os.chdir(_thisDir)
main_dir = _thisDir
sub_dir = os.path.join(main_dir, 'scan_data', 'sub%03d' % (int(expInfo['subject number'])), 'sess%01d_%s' % (int(expInfo['visit']), expInfo['condition']), 'eyelink')
if not os.path.exists(sub_dir):
    os.makedirs(sub_dir)
psypy_filename = sub_dir + os.sep + u'imensa_sub%03d_sess%01d_%s_%s' % (int(expInfo['subject number']), int(expInfo['visit']), expName, expInfo['run'])


# === 1d. Log for detail verbose info ===
# logFile = logging.LogFile(psypy_filename+'.log', level=logging.EXP)
# logging.console.setLevel(logging.WARNING)  # this outputs to the screen, not a file
# endExpNow = False   # flag for 'escape' or other condition => quit the exp

# === 2c. Instructional TextStim ===
starts_time_strg = ['12:16', '9:40', '6:59']
run_type_strg = ['MOVIE','RESTING','RSA']
if expInfo['run'][0] == 'm':
    run_type_i = 0
elif expInfo['run'] == 'rs':
    run_type_i = 1
elif expInfo['run'][0] == 'r':
    run_type_i = 2
wait_trigger_msg = 'SUB%03d SESS %01d - %s %s \n\n Press [z] before MR trigger starts\n\n %s' % (int(expInfo['subject number']), int(expInfo['visit']), run_type_strg[run_type_i], expInfo['run'][1], starts_time_strg[run_type_i])


end_msg = 'Closing run and saving the data'
ongoing_run_msg = 'SUB%03d SESS%01d - %s %s\n\nPress [e] to stop recording' %(int(expInfo['subject number']), int(expInfo['visit']), 
    run_type_strg[run_type_i], expInfo['run'][1])
ongoing_run_msg_stim = visual.TextStim(win, text=ongoing_run_msg, height=0.05)

wait_trigger_stim_1 = visual.TextStim(win, text=wait_trigger_msg, height=.07, color='white')
end_msg_stim = visual.TextStim(win, text=end_msg, height=0.06)


# === 2c. Keyboard and Clocks ===
defaultKeyboard = keyboard.Keyboard()   # to check for escape
Begin_resp = keyboard.Keyboard()

### ticktock
globalClock = core.Clock()              # to track the time since experiment started
ntp_c = ntplib.NTPClient()

# === **. Eyelink setup ===
if eyelink_use:
    # Step 1: Connect to the EyeLink Host PC
    try:
        el_tracker = pylink.EyeLink("100.1.1.1")
    except RuntimeError as error:
        print('ERROR:', error)
        core.quit()
        sys.exit()
else:
    el_tracker = pylink.EyeLink(None)

if eyelink_use:
    # Step 2: Open an EDF data file on the Host PC
    edf_file = "i%02d%s.EDF" % (int(expInfo['subject number']), expInfo['run'])
    # We download EDF data file from the EyeLink Host PC to the local hard
    # drive at the end of each testing session, here we rename the EDF to
    # include session start date/time
    # session_identifier = expName + time.strftime("_%Y_%m_%d_%H_%M", time.localtime())
    # create a folder for the current testing session in the "results" folder
    # session_folder = os.path.join(sub_dir, session_identifier)
    # if not os.path.exists(session_folder):
    #     os.makedirs(session_folder)

    try:
        el_tracker.openDataFile(edf_file)
    except RuntimeError as err:
        print('ERROR:', err)
        # close the link if we have one open
        if el_tracker.isConnected():
            el_tracker.close()
        core.quit()
        sys.exit()
    
    # Add a header text to the EDF file to identify the current experiment name
    # This is OPTIONAL. If your text starts with "RECORDED BY " it will be
    # available in DataViewer's Inspector window by clicking
    # the EDF session node in the top panel and looking for the "Recorded By:"
    # field in the bottom panel of the Inspector.
    preamble_text = 'RECORDED BY %s' % os.path.basename(__file__)
    el_tracker.sendCommand("add_file_preamble_text '%s'" % preamble_text)

    # Step 3: Configure the tracker
    # Put the tracker in offline mode before we change tracking parameters
    el_tracker.setOfflineMode()

    # Get the software version:  1-EyeLink I, 2-EyeLink II, 3/4-EyeLink 1000,
    # 5-EyeLink 1000 Plus, 6-Portable DUO
    eyelink_ver = 0  # set version to 0, in case running in Dummy mode
    vstr = el_tracker.getTrackerVersionString()
    eyelink_ver = int(vstr.split()[-1].split('.')[0])
    # print out some version info in the shell
    print('Running experiment on %s, version %d' % (vstr, eyelink_ver))

    # File and Link data control
    file_event_flags = 'LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON,INPUT'
    link_event_flags = 'LEFT,RIGHT,FIXATION,SACCADE,BLINK,BUTTON,FIXUPDATE,INPUT'
    file_sample_flags = 'LEFT,RIGHT,GAZE,HREF,RAW,AREA,HTARGET,GAZERES,BUTTON,STATUS,INPUT'
    link_sample_flags = 'LEFT,RIGHT,GAZE,GAZERES,AREA,HTARGET,STATUS,INPUT'
    el_tracker.sendCommand("file_event_filter = %s" % file_event_flags)
    el_tracker.sendCommand("file_sample_data = %s" % file_sample_flags)
    el_tracker.sendCommand("link_event_filter = %s" % link_event_flags)
    el_tracker.sendCommand("link_sample_data = %s" % link_sample_flags)

    # Optional tracking parameters
    # Sample rate, 250, 500, 1000, or 2000, check your tracker specification
    if eyelink_ver > 2:
        el_tracker.sendCommand("sample_rate 250")
    # Choose a calibration type, H3, HV3, HV5, HV13 (HV = horizontal/vertical),
    el_tracker.sendCommand("calibration_type = HV5")
    # Set a gamepad button to accept calibration/drift check target
    # You need a supported gamepad/button box that is connected to the Host PC
    el_tracker.sendCommand("button_function 5 'accept_target_fixation'")

    # Optional -- Shrink the spread of the calibration/validation targets
    # if the default outermost targets are not all visible in the bore.
    # The default <x, y display proportion> is 0.88, 0.83 (88% of the display
    # horizontally and 83% vertically)
    # el_tracker.sendCommand('calibration_area_proportion 0.88 0.83')
    # el_tracker.sendCommand('validation_area_proportion 0.88 0.83')

    # Optional: online drift correction.
    # See the EyeLink 1000 / EyeLink 1000 Plus User Manual
    #
    # Online drift correction to mouse-click position:
    # el_tracker.sendCommand('driftcorrect_cr_disable = OFF')
    # el_tracker.sendCommand('normal_click_dcorr = ON')

    # Online drift correction to a fixed location, e.g., screen center
    # el_tracker.sendCommand('driftcorrect_cr_disable = OFF')
    # el_tracker.sendCommand('online_dcorr_refposn %d,%d' % (int(scn_width/2.0),
    #                                                        int(scn_height/2.0)))
    # el_tracker.sendCommand('online_dcorr_button = ON')
    # el_tracker.sendCommand('normal_click_dcorr = OFF')
        
    # Step 4: set up a graphics environment for calibration
    # get the native screen resolution used by PsychoPy
    scn_width, scn_height = win.size

    # Pass the display pixel coordinates (left, top, right, bottom) to the tracker
    # see the EyeLink Installation Guide, "Customizing Screen Settings"
    el_coords = "screen_pixel_coords = 0 0 %d %d" % (scn_width - 1, scn_height - 1)
    el_tracker.sendCommand(el_coords)

    # Write a DISPLAY_COORDS message to the EDF file
    # Data Viewer needs this piece of info for proper visualization, see Data
    # Viewer User Manual, "Protocol for EyeLink Data to Viewer Integration"
    dv_coords = "DISPLAY_COORDS  0 0 %d %d" % (scn_width - 1, scn_height - 1)
    el_tracker.sendMessage(dv_coords)

    # Configure a graphics environment (genv) for tracker calibration
    genv = EyeLinkCoreGraphicsPsychoPy(el_tracker, win)
    print(genv)  # print out the version number of the CoreGraphics library

    # Set background and foreground colors for the calibration target
    # in PsychoPy, (-1, -1, -1)=black, (1, 1, 1)=white, (0, 0, 0)=mid-gray
    foreground_color = (1, 1, 1)
    background_color = win.color
    genv.setCalibrationColors(foreground_color, background_color)

    # Set up the calibration target
    #
    # The target could be a "circle" (default), a "picture", a "movie" clip,
    # or a rotating "spiral". To configure the type of calibration target, set
    # genv.setTargetType to "circle", "picture", "movie", or "spiral", e.g.,
    genv.setTargetType('circle')
    #
    # Use gen.setPictureTarget() to set a "picture" target
    # genv.setPictureTarget(os.path.join('images', 'fixTarget.bmp'))
    #
    # Use genv.setMovieTarget() to set a "movie" target
    # genv.setMovieTarget(os.path.join('videos', 'calibVid.mov'))

    # Use a picture as the calibration target
    # genv.setTargetType('picture')
    # genv.setPictureTarget(os.path.join('stimuli', 'fixTarget.bmp'))

    # Configure the size of the calibration target (in pixels)
    # this option applies only to "circle" and "spiral" targets
    genv.setTargetSize(24)

    # Beeps to play during calibration, validation and drift correction
    # parameters: target, good, error
    #     target -- sound to play when target moves
    #     good -- sound to play on successful operation
    #     error -- sound to play on failure or interruption
    # Each parameter could be ''--default sound, 'off'--no sound, or a wav file
    genv.setCalibrationSounds('', '', '')

    # Request Pylink to use the PsychoPy window we opened above for calibration
    pylink.openGraphicsEx(genv)

### EYELINK HELPER FUNCTIONS ###
def clear_screen(win):
    """ clear up the PsychoPy window"""
    win.fillColor = genv.getBackgroundColor()
    win.flip()

def show_msg(win, text, wait_for_keypress=True):
    """ Show task instructions on screen"""
    msg = visual.TextStim(win, text, color=genv.getForegroundColor(), wrapWidth=scn_width/2)
    clear_screen(win)
    msg.draw()
    win.flip()
    # wait indefinitely, terminates upon any key press
    if wait_for_keypress:
        event.waitKeys()
        clear_screen(win)

def terminate_task():
    """ Terminate the task gracefully and retrieve the EDF data file

    file_to_retrieve: The EDF on the Host that we would like to download
    win: the current window used by the experimental script
    """
    el_tracker = pylink.getEYELINK()

    if el_tracker.isConnected():
        # Terminate the current trial first if the task terminated prematurely
        error = el_tracker.isRecording()
        if error == pylink.TRIAL_OK:
            abort_trial()

        # Put tracker in Offline mode
        el_tracker.setOfflineMode()

        # Clear the Host PC screen and wait for 500 ms
        el_tracker.sendCommand('clear_screen 0')
        pylink.msecDelay(500)

        # Close the edf data file on the Host
        el_tracker.closeDataFile()

        # Show a file transfer message on the screen
        msg = 'EDF data is transferring from EyeLink Host PC...'
        show_msg(win, msg, wait_for_keypress=False)

        # Download the EDF data file from the Host PC to a local data folder
        # parameters: source_file_on_the_host, destination_file_on_local_drive
        local_edf = os.path.join(sub_dir, '%s.EDF' % expInfo['run'])
        try:
            el_tracker.receiveDataFile(edf_file, local_edf)
        except RuntimeError as error:
            print('ERROR:', error)

        # Close the link to the tracker.
        el_tracker.close()

    # close the PsychoPy window
    win.close()

    # quit PsychoPy
    core.quit()
    sys.exit()
    
def abort_trial():
    """Ends recording """

    el_tracker = pylink.getEYELINK()

    # Stop recording
    if el_tracker.isRecording():
        # add 100 ms to catch final trial events
        pylink.pumpDelay(100)
        el_tracker.stopRecording()

    # clear the screen
    clear_screen(win)
    # Send a message to clear the Data Viewer screen
    bgcolor_RGB = (116, 116, 116)
    el_tracker.sendMessage('!V CLEAR %d %d %d' % bgcolor_RGB)

    # send a message to mark trial end
    el_tracker.sendMessage('TRIAL_RESULT %d' % pylink.TRIAL_ERROR)

    return pylink.TRIAL_ERROR

if eyelink_use:
    # put tracker in idle/offline mode before recording
    el_tracker.setOfflineMode()

    # Start recording, at the beginning of a new run
    # arguments: sample_to_file, events_to_file, sample_over_link,
    # event_over_link (1-yes, 0-no)
    try:
        el_tracker.startRecording(1, 1, 1, 1)
    except RuntimeError as error:
        print("ERROR:", error)
        terminate_task()

    # Allocate some time for the tracker to cache some samples
    pylink.pumpDelay(100)
recording_starttime = globalClock.getTime()


wait_trigger_stim_1.draw()          # Automatically draw every frame
win.flip()      
bids_data = []  # Start a new BIDS data collection array for each run

event.waitKeys(keyList='z')
win.fillColor = 'black'
win.flip()
run_starttime = globalClock.getTime()
run_starttime_ntp = ntp_c.request('time.windows.com', version=3)
run_start_actT = time.ctime(run_starttime_ntp.tx_time)[4:-5]
run_start_ntp = run_starttime_ntp.tx_time
if eyelink_use:
    el_tracker.sendMessage('run starts')

onset = run_starttime - recording_starttime
print("%s run starts" % expInfo['run'])

ongoing_run_msg_stim.draw()          # Automatically draw every frame
win.flip()

event.waitKeys(keyList = 'e')
run_ends = globalClock.getTime()
run_endtime_ntp = ntp_c.request('time.windows.com', version=3)
run_end_actT = time.ctime(run_endtime_ntp.tx_time)[4:-5]
run_end_ntp = run_endtime_ntp.tx_time
if eyelink_use:
    el_tracker.sendMessage('run ends')

dur = run_ends - run_starttime
print("%s run ends" % expInfo['run'])

end_msg_stim.draw()          # Automatically draw every frame
win.flip()     

bids_data.append((expInfo['run'], onset, dur, run_start_actT, run_start_ntp, run_end_actT, run_end_ntp))    
bids_run_filename = sub_dir + os.sep + u'imensa_sub%03d_sess%01d_%s_%s.tsv' % (int(expInfo['subject number']), int(expInfo['visit']), expName, expInfo['run'])
bids_data = pd.DataFrame(bids_data, columns = ['run', 'onset', 'duration', 'run starts', 'run start ntp', 'run ends', 'run end ntp'])
bids_data.to_csv(bids_run_filename, sep="\t")
print("run type %s duration is %d" %(expInfo['run'], dur))
# logging.flush()

if eyelink_use:
    # stop recording; add 100 msec to catch final events before stopping
    pylink.pumpDelay(100)
    el_tracker.stopRecording()
    # Step 7: disconnect, download the EDF file, then terminate the task
    terminate_task()
    
core.wait(1)
win.close()  # close the window
core.quit()