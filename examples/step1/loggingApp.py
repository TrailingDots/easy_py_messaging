"""
    Execute as:
        python loggingApp.py 123
    The "123" is a unique identifier that should
    be distinct for each logging app.
    Use a different number for each logging device.

    A common application requiring logging.
    The logs are, of course, fabricated.


"""
import sys
import time
import loggingClientTask

# ============================================================
# Standard initialization sequence.
# ============================================================
appLog = loggingClientTask.LoggingClientClass();
appLog.start()

# Start sending a log entry once a second until interupted
appLog.info('Starting endless logs. Ctl-C to stop this')
ndx = 0

# If user does not enter a site, supply the site as "123"
site = "123"
if len(sys.argv) > 1:
    site = sys.argv[1]

# Loop once a second to send messages
while True:
    ndx += 1
    msg = 'ndx=%d %s' % (ndx, site)
    print msg
    appLog.info(msg)    # Send info only messages for now.
    time.sleep(1)       # Don't flood the logging service. 1 per second.

# Should never get here
print 'done'


