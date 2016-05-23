#!/usr/binenv python
#
# Class that creates clients to send
# messages and receive a response.
#

import sys
import os
import zmq
import threading
import time
import traceback
import logConfig
import platform
import apiLoggerInit

# Default port
PORT = 5590

class ClientCreateClass(threading.Thread):
    """
    Create a client class that sends requests and
    receives server responses.
    """

    def __init__(self, config):
        """
        config as a dictionary describes the client configuration.
        All but id_name keywords are required.

        id_name = These names appear in
                the log entry as an identifier of the source
                of the log entry.

        port = port to use for communications.

        host = name of host. For servers, this may commonly be '*'
                For clients, this may be localhost or a node name.

        scheme = Typically 'tcp' or 'udp'.

        """

        def demandKey(key):
            """Insist that key be in the config dict.
            Return the valid in the config dict."""
            if config[key] is None:
                sys.stdout.write('"%s" required, not found in ClientCreateClass.\n'
                        % key)
                traceback.print_exc()
                sys.exit(1)
            else:
                return config[key]


        try:
            self.port = int(demandKey('port'))
        except ValueError as err:
            sys.stdout.write('port "%s" must be an integer.\n' % 
                    str(config['port']))
            sys.exit(1)
        self.id_name = demandKey('id_name')
        self.host = demandKey('host')
        self.scheme = demandKey('scheme')

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
        app_socket = '%s://%s:%d' % (self.scheme, self.host, self.port)
        try:
            self.socket.connect(app_socket)
        except zmq.ZMQError as err:
            sys.stdout.write('connect ZMQError: "%s": %s\n' % (app_socket, str(err)))
            sys.exit(1)
        except Exception as err:
            sys.stdout.write('connect Exception: %s: %s\n' % (app_socket, str(err)))
            sys.exit(1)


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
        #response = self.socket.recv_multipart()
        response = self.socket.recv()
        return response


def main():
    """
    Dummy mainline for simple testing.
    Simply send strings, print responses
    """
    global PORT

    import timeit

    # =========================
    # Standard initialization
    # =========================
    client = ClientCreateClass({
        'scheme': 'tcp',
        'host': 'localhost',
        'port':PORT,
        'id_name': platform.node()
    })
    if client is None:
        sys.stderr.write('Cannot create ClientClass!\n')
        sys.exit(1)
    client.start()

    print 'Started client, pid %d port %s' % (os.getpid(), PORT)

    response = client.send('type=client,greeting=Hello world')
    print response

    response = client.send('type=client,greeting=Hello again')
    print response

    # Get a timing
    iterations = 10000     # send/recv this many messages
    start_time = timeit.default_timer()
    for ndx in range(iterations):
        client.send('ndx=%d' % ndx) # Ignore response
    elapsed = timeit.default_timer() - start_time
    sys.stdout.write('%d logs, elapsed time: %f\n' % (iterations, elapsed))
    sys.stdout.write('Timed at %d messages per second\n' %
            int(iterations/elapsed))
    print '%d logs, elapsed time: %f' % (iterations, elapsed)
    print '%d messages per second' % int(iterations/elapsed)

    response = client.send('@EXIT') # kill the server
    print response

    client.join()

if __name__ == '__main__':
    main()

