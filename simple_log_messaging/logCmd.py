#!/usr/bin/env python
"""
    A logging task that sends a log from the command line
    to logCollector.

    Simple, but useful at times.

    The log collector must be running.
    All defaults taken from logConfig.py
    Therefore, set the proper port in logConfig.py .
"""
import sys
import platform
import logging
import loggingClientTask

def main():
    logging.basicConfig(level=logging.NOTSET)   # Log everything
    client = loggingClientTask.LoggingClientClass(platform.node())
    client.start()

    msg = ' '.join(sys.argv[1:])
    client.info(msg)

