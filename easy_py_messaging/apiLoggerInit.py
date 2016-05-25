#!/bin/env python
"""
    Initialize the logging environment.
"""

#
# A simple logger for the name server
#
import sys
import logging
import logConfig


"""
 Look in the current directory for .logcollectorrc .  If not there, look in
 $HOME/.logcollectorrc Any user flags will override config file settings.

 The config parameters will look similar to:
    {
        append: True,    # Append logs to existing file. Creates if not existing.
        log_file:"/home/me/simple/logs.log",  # Name of log file.
        noisy:  False,   # Echo all collected logs to console. Used in debugging.
        port:   5570,    # Port to listen for messages.
    }

"""
DEFAULT_COLLECTOR_CONFIG_FILE = '.logcollectorrc'

ALREADY_INITED = False  # Allow multiple calls without penalty


def loggerInit():
    """
    Initialize the logger, but only once.
    """
    global ALREADY_INITED

    if ALREADY_INITED:
        return

    # Embed the app name in the log
    logging.basicConfig(filename=logConfig.LOG_FILENAME,
                        format='%(asctime)s.%(msecs)03d\t%(levelname)s' +
                        '\t%(message)s',
                        datefmt='%Y-%m-%dT%H:%M:%S',
                        level=logging.NOTSET)   # NOTSET means log EVERYTHING!
    if logConfig.TESTING:
        # If testing, echo logs to stdout as well as logfile.
        log = logging.getLogger('')
        log.addHandler(logging.StreamHandler(sys.stdout))
        logging.info('Logging Started')
    ALREADY_INITED = True

if __name__ == '__main__':
    logConfig.TESTING = True
    loggerInit()
    # Call again to make sure the init flag works.
    loggerInit()
