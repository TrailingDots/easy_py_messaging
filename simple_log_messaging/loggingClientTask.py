#!/usr/binenv python
#
# Example of an app that sends logs to the
# logCollector.
#
# Log entries are simply made up.
#

import sys
import zmq
import threading
import time
import logConfig
import platform
import apiLoggerInit
import logging
import logComponents


class LoggingClientClass(threading.Thread):
    """
    Remote clients wishing to send logs to a server will create an instance of
    this class and call to send log messages to the server.
    """

    def __init__(self, id_name=platform.node()):
        """
        id_name = These names appear in
                the log entry as an indentifier of the source
                of the log entry.
        """

        self.context = None
        self.id_name = str(id_name)
        self.socket = None
        self.poll = None
        self.reqs = 0       # Count of messages
        logging.basicConfig(level=logging.NOTSET)   # Log everything
        apiLoggerInit.loggerInit()
        threading.Thread.__init__(self)

    def run(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.DEALER)
        identity = u'%s' % str(self.id_name)
        self.socket.identity = identity.encode('ascii')
        self.socket.connect(logConfig.getAppSocket())
        self.poll = zmq.Poller()
        self.poll.register(self.socket, zmq.POLLIN)

    def _send_string(self, astr):
        """Send astr as a fully formed log message.
        Return True  for success
               False for failure.
        """
        try:
            dummy = 0
            while self.socket is None:  # TODO FIXME Potential hang!!!
                dummy += 1
                if dummy > 200:
                    # Sometimes the socket "disappears" for awhile.
                    sys.stderr.write('Cannot get self.socket!')
                    raise Exception('Cannot obtain self.socket')
                time.sleep(0.1)
            self.socket.send_string(astr)
        except zmq.ZMQError as err:
            sys.stderr.write('ERROR in send_string:%s\n' % err)
            return 1    # Non-zero status == problems
        return 0        # Zero status == msg sent

    def _compose_msg(self, level, payload):
        """ From the pieces, create a full message and send it.  """
        log_components = logComponents.LogComponents(level, payload)
        msg = str(log_components)
        return self._send_string(msg)

    def debug(self, payload):
        """ Send a debug message to the log server.  """
        return self._compose_msg('DEBUG', payload)

    def cmd(self, payload):
        """ Send a command message to the log server.  """
        return self._compose_msg('CMD', payload)

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
    Simply send strings of logs to the logCollector.
    """

    # =========================
    # Standard initialization
    # =========================
    apiLoggerInit.loggerInit()
    client = LoggingClientClass(platform.node())
    if client is None:
        sys.stderr.write('Cannot create LoggingClientClass!\n')
        sys.exit(1)
    client.start()

    # All the log levels in the remote logger
    REMOTE_LOG_LEVELS = {
        'DEBUG': client.debug,
        'CMD': client.cmd,
        'INFO': client.info,
        'WARNING': client.warning,
        'ERROR': client.error,
        'CRITICAL': client.critical}

    info_msg = 'status=1,msg=info,reason=nothing important'
    warning_msg = 'msg=Warning,a=n,stuff=yuck,floor=ceiling'
    error_msg = 'status=3,warn=continue,babble=yes,reason=testing'
    debug_msg = 'msg=debug,details=yes'
    critical_msg = 'msg=critical,reason=meltdown'

    # Do NOT change the messages below.
    # When run with the unit test code.  the unit test code checks for these
    # messages to exist in the log files after logging.
    for key, fcn in REMOTE_LOG_LEVELS.items():
        fcn('thru=%s,level=%s,using=REMOTE_LOG_LEVELS' % (key, key))

    client.warning('type=client,' + warning_msg)
    client.error('type=client,' + error_msg)
    client.debug('type=client,' + debug_msg)
    client.critical('type=client,' + critical_msg)
    client.info('type=client,' + info_msg)

    client.info('type=logging,Does logging.info(), etc. still work?')
    client.warning('type=logging,Once again - using pure logging.')
    client.warning('type=logging,Notice no "host=..." on tagged onto the logs.')

    client.warning('type=logging,' + warning_msg)
    client.error('type=logging,' + error_msg)
    client.debug('type=logging,' + debug_msg)
    client.critical('type=logging,' + critical_msg)
    client.info('type=logging,' + info_msg)

    client.debug('debugging? Sending to logCollector?')
    client.info('loggingClientTask: Done')


if __name__ == '__main__':
    main()

