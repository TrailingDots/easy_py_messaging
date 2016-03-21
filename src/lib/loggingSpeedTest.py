#!/usr/bin/env python
"""
    A logging task that sends lots of logs to the
    log controller to get a speed test in terms
    of max logs per second.
"""
import loggingClientTask
import os
import sys
import platform
import apiLoggerInit
import logging
import utils
from utils import bcolors
import timeit

import atexit
def exiting(exit_msg):
    print(exit_msg + '\n')

import signal
def signalHandler(signum, frame):
    print ('loggingSpeedTask: signalHandler called with %d\n' % (signum))
    #sys.exit(0)

signal.signal(signal.SIGTERM, signalHandler)
signal.signal(signal.SIGHUP, signalHandler)
signal.signal(signal.SIGINT, signal.SIG_DFL)

def main():
    print bcolors.BGRED + \
        ('>>> loggingSpeedTest: pid %d' % os.getpid()) + \
        bcolors.ENDC
    atexit.register(exiting, 'loggingSpeedTest')
    apiLoggerInit.loggerInit('loggingSpeedTest')
    logging.basicConfig(level=logging.NOTSET)   # Log everything
    client = loggingClientTask.LoggingClientClass(platform.node())
    client.start()

    startTime = timeit.default_timer()
    iterations = 100000
    for ndx in range(iterations):
        client.info('ndx=%d' % ndx)
    elapsed = timeit.default_timer() - startTime
    client.info('%d logs, elapsed time: %f' % (iterations, elapsed))
    client.info('Timed at %d messages per second' % int(iterations/elapsed))
    print '%d logs, elapsed time: %f' % (iterations, elapsed)
    print '%d messages per second' % int(iterations/elapsed)


if __name__ == '__main__':
    main()

