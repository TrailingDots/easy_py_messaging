#!/usr/binenv python
#
# Example of an app that sends logs to a
# logCollector.
#
# Log entries provided only for demo purposes.
#

import sys
import zmq
import threading
import time
import platform


# These setting would normally come from a
# configuration file of some sort.
SCHEME = 'tcp'
APP_HOST = 'localhost'  # For testing and easy demo
PORT = 5570             # Port for communications

def getAppSocket():
    """ 
    Connect socket string
    Likely to change only the HOST and PORT
    See: https://en.wikipedia.org/wiki/Uniform_Resource_Locator#Syntax
    The socket names the applications should use.
    The application should use this for the socket.
    """
    global SCHEME
    global APP_HOST
    global PORT

    app_socket = '%s://%s:%d' % (SCHEME, APP_HOST, PORT)
    return app_socket

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
        threading.Thread.__init__(self)

    def run(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.DEALER)
        identity = u'%s' % str(self.id_name)
        self.socket.identity = identity.encode('ascii')
        self.socket.connect(getAppSocket())
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
        msg = level + ': ' + payload
        return self._send_string(msg)


    def info(self, payload):
        """ Send an info message to the log server.  """
        return self._compose_msg('INFO', payload)


def main():
    """
    Simply send strings of logs to the logCollector.
    """

    # Initialization
    client = LoggingClientClass(platform.node())
    if client is None:
        sys.stderr.write('Cannot create LoggingClientClass!\n')
        sys.exit(1)
    client.start()

if __name__ == '__main__':
    main()

