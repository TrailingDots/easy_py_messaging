# Miscellaneous utilities that are short routines
# useful in multiple places.
#
import sys
import os
import logging
import logConfig
import datetime
import time

class bcolors:
    """
    Simple names for highlighting colors.
    Use as:
        print (bcolors.BGGREEN + 
            ('proc_collector pid: %d' % proc_collector.pid) +
            bcolors.ENDC)
    """
    BGRED = '\033[101m'
    BGGREEN = '\033[102m'
    BGBLUE = '\033[94m'
    BGGRAY = '\033[47m'
    ENDC = '\033[0m'

# The log levels get used in multiple places.
# The connection to logging gets used ONLY in logCollector.
# All the log levels in the logger must use these on the log
# collector side because the standard python logger class emits the logs.
#
# Remote loggers MUST use the routines in logComponents and use the
# keys in LOG_LEVEL to determine valid log levels.
LOG_LEVELS = {'DEBUG': logging.debug,
              'INFO': logging.info, 
              'WARNING': logging.warning, 
              'ERROR': logging.error, 
              'CRITICAL': logging.critical}

# Priority of logging. Used in filter routines.
LOG_PRIORITY = {
                'DEBUG': 0,
                'INFO': 1,
                'WARNING': 2,
                'ERROR': 3,
                'CRITICAL': 4,
                }
def filterPriority(initial_level):
    """
    initial_level: a string representing the log level.
    Given an initial_level, answer a list of
    log levels at and above this level.

    If the level is bogus, return all levels.
    """
    if initial_level not in LOG_PRIORITY.keys():
        return LOG_PRIORITY.keys()
    else:
        initial = LOG_PRIORITY[initial_level]
        filteredPriorities = {}
        for level, priority in LOG_PRIORITY.items():
            if priority >= initial:
                filteredPriorities[level] = priority
        return filteredPriorities


"""
A log message contains a date, a log level and a payload
separated by the separation character.
"""
SEPARATION_CHAR = '\t'

# The payload consists of name=value pairs separated
# by the PAYLOAD_CONNECTOR character.
PAYLOAD_CONNECTOR = ','
KEY_VALUE_SEPARATOR = '='

# ------------------------------------------------------------
# May use either a file log output or a database.
# ------------------------------------------------------------

# This may change depending on prog invocation run time flags.
APPEND_TO_LOG = True


# ============================================================
# Time conversion utilities.
# ============================================================
#
# The "start of the epoch" is defined as the start of the
# computer age == Jan 1, 1970 at 00:00 hours. The very first
# second of that decade.
#
# See: https://en.wikipedia.org/wiki/Unix_time
#
# ============================================================

# How time gets formatted
TIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'

def timeNow():
    """
    Returns a floating point number as seconds since
    start of the epoch. This number has microseconds in it,
    but is not guaranteed to be that accurate. More likely
    the accuracy is to the nearest millisecond or so.
    The exact accuracy depends upon your system.
    How accurate do we need this value? Likely to the
    nearest tenth of a second, or even to the nearest second.
    """
    return time.time()

def timeNowISO8601():
    """
    Return the current time in ISO 8601 format
    """
    secsStr = secondsToISO8601(timeNow())
    return secsStr

def secondsToISO8601(seconds):
    """
    Given time in seconds, return an ISO 8601 string
    representation of that time.
    """
    timeDT = datetime.datetime.fromtimestamp(seconds)
    return timeDT.strftime(TIME_FORMAT)

def ISO8601ToSeconds(iso8601):
    """
    Given an ISO 8601 string in our format,
    convert to seconds.
    """
    try:
        isoTuple = datetime.datetime.strptime(iso8601, TIME_FORMAT)
        seconds = time.mktime(isoTuple.timetuple()) + isoTuple.microsecond/1000000.0
    except ValueError as err:
        sys.stderr.write('%s: %s\n' % (str(err), str(iso8601)))
        return None

    return seconds



