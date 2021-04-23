import timeit

# from datetime import datetime
from medocControl import *
from psychopy import core
import random

while True:
    # startTime = timeit.default_timer()
    # poll_for_change('IDLE')
    # core.wait(5)
    # command = random.randint(101,171)
    command = 117
    if poll_for_change('IDLE', poll_max=-1): 
        # startTime = datetime.now()
        startTime = timeit.default_timer()
        print("Running " + str(command)) 
        sendCommand('select_tp', command)        
    # print("start time: " + str(startTime))
    # if poll_for_change('READY'): sendCommand('start'); print("First start command took: " + str(timeit.default_timer() - startTime) + "s past polling")
    # startTime2 = timeit.default_timer()
    # if poll_for_change('RUNNING'): sendCommand('start'); print("Second start command took " + str(timeit.default_timer() - startTime2) + "s past polling")
    # print("Selected TP at: " + str(timeit.default_timer()-startTime))
    if poll_for_change('RUNNING'): sendCommand('trigger')
    # print("end polling time: {}".format(datetime.now() - startTime))
    print("Stim started " + str(timeit.default_timer() - startTime) + "s past polling")
    
    # print("Stim started " + str(timeit.default_timer()-startTime) + " past polling")

    # core.wait(5)
    # print("Polling prior to first trigger: " + str(timeit.default_timer()-startTime))
    startTime2 = timeit.default_timer()
    # startTime2 = datetime.now()
    # jitter = random.randint(1,5)
    # core.wait(jitter)
    # core.wait(jitter + 13)
    # poll_for_change('IDLE')
    # startTime3 = timeit.default_timer()
    command = random.randint(101,171)
    command = 170
    if poll_for_change('IDLE', poll_max=-1):
        # print("Post-trigger selection latency: " + str(timeit.default_timer()-startTime2));
        # print("stimclock: " + str(timeit.default_timer()))        
        print("Post-stimulation selection latency: " + str(timeit.default_timer()-startTime2)); 

        # print("stimclock: {}".format(datetime.now() - startTime))
        # print("Post-stimulation selection latency {}".format(datetime.now() - startTime2) + " past polling")
        # print("Running " + str(command)); 
        sendCommand('select_tp', command)
    # if poll_for_change('READY'): sendCommand('start')
    # if poll_for_change('RUNNING'): sendCommand('start')
    # print("stimclock: " + str(timeit.default_timer()))
    print("Second stimulation begins at : " + str(timeit.default_timer()-startTime))

    # print("end time: {}".format(datetime.now() - startTime))
    # print("Second stimulation started {}".format(datetime.now() - startTime) + " past polling")
    # core.wait(5)
    # if poll_for_change('RUNNING'):
    #     print("Post-trigger trigger latency: " + str(timeit.default_timer()-startTime2) + ' (it took ' + str(timeit.default_timer()-startTime3) + ' )')
    #     sendCommand('trigger')
    #     print("Second Stim Trigger: " + str(timeit.default_timer()-startTime))
    # core.wait(13)