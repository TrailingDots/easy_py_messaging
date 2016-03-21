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


ALREADY_INITED = False  # Allow multiple calls without penalty

def loggerInit(appName):
    """
    Initialize the logger, but only once.

    The default logging level is INFO. To log everything,
    change the level at any time:
        logger.basicConfig(level=logging.NOTSET)

    Set level to warning and above:
        logger.basicConfig(level=logging.WARNING)

    """
    global ALREADY_INITED

    if ALREADY_INITED:
        return

    # Embed the app name in the log
    logging.basicConfig(filename='logs.log',
                        format='%(asctime)s.%(msecs)03d\t%(levelname)s' +
                        '\t%(message)s',
                        datefmt='%Y-%m-%dT%H:%M:%S',
                        level=logging.NOTSET)   # NOTSET is EVERYTHING!
    if logConfig.TESTING:
        # If testing, echo logs to stdout as well as logfile.
        log = logging.getLogger('')
        log.addHandler(logging.StreamHandler(sys.stdout))
        logging.info('Logging Started')
    ALREADY_INITED = True

if __name__ == '__main__':
    logConfig.TESTING = True
    loggerInit('testing APILoggerInit')
    # Call again to make sure the init flag works.
    loggerInit('testing APILoggerInit-again')
