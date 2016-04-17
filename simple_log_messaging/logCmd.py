#!/usr/bin/env python
"""
    A logging task that sends a log from the command line
    to logCollector.

    Simple, but potentially useful at times.

    The log collector must be running.
    All defaults taken from logConfig.py
"""
import os
import sys
import platform
import logging
import loggingClientTask
import utils

import signal
signal.signal(signal.SIGTERM, signal.SIG_DFL)
signal.signal(signal.SIGHUP, signal.SIG_DFL)
signal.signal(signal.SIGINT, signal.SIG_DFL)


def main():
    print 'in logCmd.py'
    import pdb; pdb.set_trace()
    logging.basicConfig(level=logging.NOTSET)   # Log everything
    client = loggingClientTask.LoggingClientClass(platform.node())
    client.start()

    msg = ' '.join(sys.argv[1:])
    client.info(msg)

