"""
  Miscellaneous utilities that are short routines
  useful in multiple places.
"""
import sys
import logging
import datetime
import time
import signal


class bcolors(object):
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


SIGNALS_TO_NAMES_DICT = dict((getattr(signal, n), n)
    for n in dir(signal) if n.startswith('SIG') and '_' not in n)


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
              'CMD': logging.warning,      # Pytrhon logging has no CMD!
              'ERROR': logging.error,
              'CRITICAL': logging.critical}

# Priority of logging. Used in filter routines.
# Key = priority name
# Value = index of priority
LOG_PRIORITY = {
                'DEBUG': 0,
                'INFO': 1,
                'WARNING': 2,
                'CMD': 3,       # At this level to capture all CMDs.
                'ERROR': 4,
                'CRITICAL': 5,
                }

# Key = index of priority
# Value = Name of level
LOG_PRIORITY_BY_NDX = {value: key for key, value in LOG_PRIORITY.items()}


def cycle_priority(cur_level):
    """
    Given the current log level such as WARNING,
    bump up to the next level, CMD. If at
    the top, CRITICAL, cycle to DEBUG.

    current_level = Name of the current level.

    Return: log level cycled up one level. If at
    CRITICAL, return DEBUG.
    """
    level = LOG_PRIORITY.get(cur_level, None)
    if level is None:
        return 'DEBUG'  # Bogus level name passed
    if level == LOG_PRIORITY['CRITICAL']:
        return 'DEBUG'
    return LOG_PRIORITY_BY_NDX[level + 1]


def filter_priority(initial_level):
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
        filtered_priorities = {}
        for level, priority in LOG_PRIORITY.items():
            if priority >= initial:
                filtered_priorities[level] = priority
        return filtered_priorities


#  A log message contains a date, a log level and a payload
#  separated by the separation character.
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


def time_now():
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


def time_now_ISO8601():
    """
    Return the current time in ISO 8601 format
    """
    secs_str = seconds_to_ISO8601(time_now())
    return secs_str


def seconds_to_ISO8601(seconds):
    """
    Given time in seconds, return an ISO 8601 string
    representation of that time.
    """
    timeDT = datetime.datetime.fromtimestamp(seconds)
    return timeDT.strftime(TIME_FORMAT)


def ISO8601_to_seconds(iso8601):
    """
    Given an ISO 8601 string in our format,
    convert to seconds.
    """
    try:
        iso_tuple = datetime.datetime.strptime(iso8601, TIME_FORMAT)
        seconds = time.mktime(iso_tuple.timetuple()) + \
                iso_tuple.microsecond/1000000.0
    except ValueError as err:
        sys.stderr.write('%s: %s\n' % (str(err), str(iso8601)))
        return None

    return seconds

