"""
    A common application requiring logging.
    The logs are, of course, fabricated.
    
    This code illustrates typical usage.
"""
import sys
import time
import logging
import platform

# The final app will not have this sys.path line.
# It must be here for demo purposes only!
sys.path.append('../../src/lib')

import loggingClientTask
import apiLoggerInit

# ============================================================
# "Standard" initialization sequence.
# ============================================================
apiLoggerInit.loggerInit('step1:loggingApp')
logging.basicConfig(level=logging.NOTSET)   # Log everything
appLog = loggingClientTask.LoggingClientClass(platform.node())
appLog.start()

# ============================================================
# A user application may use appLog anywhere to produce
# logs that get sent to the logCollector process
# either locally or remotely.
# ============================================================
#
# The following illustrates the use of appLog:
appLog.info('Starting examples of simple, unstructured logs')
appLog.debug('Use me when debugging')
appLog.info('Just a minor note')
appLog.warning('Start of user logging')
appLog.debug('A debug message')
appLog.error('An error has occurred!')
appLog.critical('Something critical happened')

# Dump mulitple logs all at once.
for ndx in range(10):
    appLog.info('type=temperature&ndx=%d' % ndx)

# Start ending a log entry once a second until interupted
appLog.info('Starting endless logs. Ctl-C to stop this')
ndx = 0
while True:
    ndx += 1
    msg = 'ndx=%d' % ndx
    print msg
    appLog.info(msg)
    time.sleep(1)   # Don't flood the logging service

# Should never get here
print 'done'

# Allow a little time to flush the logs.
time.sleep(1)

