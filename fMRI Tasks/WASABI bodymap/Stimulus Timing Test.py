import timeit
from medocControl import *
from psychopy import core

while True:
    startTime = timeit.default_timer()
    poll_for_change('IDLE')
    # vcore.wait(5)
    sendCommand('select_tp', 170)
    if poll_for_change('RUNNING'): sendCommand('start')
    print("Selected TP at: " + str(timeit.default_timer()-startTime))
    poll_for_change('RUNNING')
    # core.wait(5)
    print("Polling prior to first trigger: " + str(timeit.default_timer()-startTime))
    startTime2 = timeit.default_timer()
    sendCommand('trigger')
    core.wait(13)
    # poll_for_change('IDLE')
    startTime3 = timeit.default_timer()
    print("Post-trigger selection latency: " + str(timeit.default_timer()-startTime2))
    sendCommand('select_tp', 170)
    if poll_for_change('RUNNING'): sendCommand('start')
    # core.wait(5)
    poll_for_change('RUNNING')
    print("Post-trigger trigger latency: " + str(timeit.default_timer()-startTime2) + ' (it took ' + str(timeit.default_timer()-startTime3) + ' )')
    sendCommand('trigger')
    print("Second Stim Trigger: " + str(timeit.default_timer()-startTime))
    core.wait(13)