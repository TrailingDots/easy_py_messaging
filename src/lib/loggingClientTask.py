#!/usr/bin/env python
#
# Example of an app that sends logs to the
# logCollector.
#
# Log entries are simply made up.
#

import os
import sys
import zmq
import threading
sys.path.append('./')
sys.path.append('../lib')
import logConfig
import platform
import apiLoggerInit
import logging
import utils
import logComponents

class LoggingClientClass(threading.Thread):
    """
    Remote clients wishing to send logs to a server will create an instance of
    this class and call to send log messages to the server.
    """

    def __init__(self, id):
        """id = name of this class. These names appear in
                the log entry as an indentifier of the source
                of the log entry.
        """

        self.id = id
        self.socket = None
        self.poll = None
        self.reqs = 0       # Count of messages
        threading.Thread.__init__(self)

    def run(self):
        context = zmq.Context()
        self.socket = context.socket(zmq.DEALER)
        identity = u'%s' % str(self.id)
        self.socket.identity = identity.encode('ascii')
        self.socket.connect(logConfig.APP_SOCKET)
        self.poll = zmq.Poller()
        self.poll.register(self.socket, zmq.POLLIN)

    def send_string(self, astr):
        """Send astr as a fully formed log message.
        Return True  for success
               False for failure.
        """
        try:
            self.socket.send_string(astr)
        except zmq.ZMQError as err:
            sys.stderr.write('ERROR in send_string:%s\n' % err)
            return False
        return True

    def _compose_msg(self, level, payload):
        """ From the pieces, create a full message and send it.  """
        log_components = logComponents.LogComponents(level, payload)
        msg = str(log_components)
        return self.send_string(msg)

    def debug(self, payload):
        """ Send a debug message to the log server.  """
        return self._compose_msg('DEBUG', payload)

    def info(self, payload):
        """ Send an info message to the log server.  """
        return self._compose_msg('INFO', payload)

    def warning(self, payload):
        """ Send a warning message to the log server.  """
        return self._compose_msg('WARNING', payload)

    def error(self, payload):
        """ Send an error message to the log server.  """
        return self._compose_msg('ERROR', payload)

    def critical(self, payload):
        """ Send a critical message to the log server.  """
        return self._compose_msg('CRITICAL', payload)



def main():
    """
    Simply send a string of logs to the logCollector.
    """

    # =========================
    # Standard initialization
    # =========================
    apiLoggerInit.loggerInit('loggingClientTask')
    logging.basicConfig(level=logging.NOTSET)   # Log everything
    client = LoggingClientClass(platform.node())
    client.start()

    # All the log levels in the remote logger
    REMOTE_LOG_LEVELS = {'INFO': client.info, 
                  'DEBUG': client.debug,
                  'WARNING': client.warning, 
                  'ERROR': client.error, 
                  'CRITICAL': client.critical}

    WarningMsg = 'msg=Warning,a=n,stuff=yuck,floor=ceiling'
    ErrorMsg = 'status=3,warn=continue,babble=yes,reason=testing'
    DebugMsg= 'msg=debug,details=yes'
    CriticalMsg = 'msg=critical,reason=meltdown'
    InfoMsg = 'status=1,msg=info,reason=nothing important'

    # Do NOT change the messages below.
    # When run with the unit test code.  the unit test code checks for these
    # messages to exist in the log files after logging.
    for key, fcn in REMOTE_LOG_LEVELS.items():
        fcn('thru=%s,level=%s,using=REMOTE_LOG_LEVELS' % (key, key))
        
    client.warning('type=client,' + WarningMsg)
    client.error('type=client,' + ErrorMsg)
    client.debug('type=client,' + DebugMsg)
    client.critical('type=client,' + CriticalMsg)
    client.info('type=client,' + InfoMsg)

    client.info('type=logging,' + 'Does logging.info(), etc. still work?')
    client.warning('type=logging,' + 'Once again - using pure logging.')
    client.warning('type=logging,' + 'Notice no "host=..." on tagged onto the logs.')

    client.warning('type=logging,' + WarningMsg)
    client.error('type=logging,' + ErrorMsg)
    client.debug('type=logging,' + DebugMsg)
    client.critical('type=logging,' + CriticalMsg)
    client.info('type=logging,' + InfoMsg)

    client.debug('debugging? Sending to logCollector?')
    client.info('loggingClientTask: Done')


if __name__ == '__main__':
    main()


