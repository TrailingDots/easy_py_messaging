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
import loggingClientTask

def main():
    client = loggingClientTask.LoggingClientClass(platform.node())
    client.start()

    msg = ' '.join(sys.argv[1:])
    return client.info(msg)

if __name__ == '__main__':
    sys.exit(main())
