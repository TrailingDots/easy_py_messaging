#!/usr/binenv python
#
# Class that creates clients to send
# messages and receive a response.
#

import sys
import zmq
import threading
import traceback
import platform


class ClientCreateClass(threading.Thread):
    """
    Create a client class that sends requests and
    receives server responses.
    """

    def __init__(self, config):
        """
        config as a dictionary describes the client configuration.
        All but id_name keywords are required.

        id_name = These names appear in the log entry as the 
                identifier of the source of the log entry.

        port = port to use for communications.

        node = name of node. For servers, this may commonly be '*'
                For clients, this may be localhost or a node name.

        """

        def demandKey(key, default):
            """Insist that key be in the config dict.
            Return the valid in the config dict."""
            if key not in config:
                config[key] = default
            return config[key]

        try:
            self.port = int(demandKey('port', 5590))
        except ValueError as err:
            sys.stdout.write('port "%s" must be an integer. %s\n' % 
                    (str(config['port']), str(err)))
            sys.exit(1)     # No real way to recover!

        self.config = config
        self.id_name = demandKey('id_name', platform.node())
        self.scheme = 'tcp'     # udp, etc. later
        self.node = demandKey('node', 'localhost')

        self.context = None
        self.socket = None
        self.poll = None
        self.reqs = 0       # Count of message requests
        threading.Thread.__init__(self)

    def run(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.DEALER)
        identity = u'%s' % str(self.id_name)
        self.socket.identity = identity.encode('ascii')
        app_socket = '%s://%s:%d' % (self.scheme, self.node, self.port)
        try:
            self.socket.connect(app_socket)
        except zmq.ZMQError as err:
            sys.stdout.write('connect ZMQError: "%s": %s\n' % (app_socket, str(err)))
            sys.exit(1)
        except Exception as err:
            sys.stdout.write('connect Exception: %s: %s\n' % (app_socket, str(err)))
            sys.exit(1)
        sys.stdout.write('Connected: %s\n' % app_socket)

        self.poll = zmq.Poller()
        self.poll.register(self.socket, zmq.POLLIN)

    def send(self, astr):
        """Send astr as a fully formed message.
        Return True  for successful send.
               False for failure.
        """
        try:
            self.socket.send_string(astr)
        except zmq.ZMQError as err:
            sys.stderr.write('ERROR in send_string:%s\n' % err)
            return 1    # Non-zero status == problems

        response = self.recv()
        return response

    def recv(self):
        """Receive a message."""
        response = self.socket.recv()
        return response

