#!/usr/binenv python
#
# Class that creates clients to send
# messages and receive a response.
#

import sys
import os
import zmq
import threading
import traceback
import logConfig
import platform

import pdb

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

        node = name of node. For servers, this may commonly be '*'
                For clients, this may be localhost or a node name.

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
            sys.stdout.write('port "%s" must be an integer. %s\n' % 
                    (str(config['port']), str(err)))
            sys.exit(1)

        self.config = config
        self.id_name = demandKey('id_name')
        self.node = demandKey('node')
        self.scheme = 'tcp'     # udp, etc. later
        self.node = demandKey('node')

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


def usage():
    """Print the usage blurb and exit."""
    print 'client_create_class.py [--help] [--port]'
    print '\t\t[--noisy] [--timing] [arg1 arg2 arg3 ...]'
    print '\t--help         = This blurb'
    print '\t--port=aport   = Port to expect queries.'
    print '\t--node=anode   = Node name or IP address of server_create_class.'
    print '\t\tDefault is localhost'
    print '\t--noisy        = Noisy reporting. Echo progress.'
    print '\t--timing       = Run timing loop only.'
    print '\targ1 ...       = Arbitrary message string'
    print ''
    sys.exit(1)


def getopts(config):
    """
    Read runtime options. Override defaults as necessary.
    """
    import getopt
    try:
        opts, _ = getopt.gnu_getopt(
                sys.argv[1:], '',
                ['port=',       # Port to expect messages
                 'noisy',       # If present, noisy trail for debug
                 'node=',       # Node name of server_create_class.
                 'timing',      # Run timing loop only
                 'help',        # Help blurb
                ])
    except getopt.GetoptError as err:
        print str(err)
        usage()

    # Number of loading args to shift out
    shift_out = 0
    for opt, arg in opts:
        if opt in ['--help']:
            usage()
        elif opt in ['--noisy']:
            config['noisy'] = True
            shift_out += 1
            continue
        elif opt in ['--port']:
            try:
                # Insist on a valid integer for a port #
                _ = int(arg)
            except ValueError as err:
                sys.stdout.write(str(err) + '\n')
                usage()
            config['port'] = arg
            shift_out += 1
            continue
        elif opt in ['--node']:
            config['node'] = arg
            shift_out += 1
            continue
        elif opt in ['--timing']:
            config['timing'] = True
            shift_out += 1
            continue

    # Create a message out of remaining args
    for ndx in range(shift_out):
        del sys.argv[1]
    config['message'] = ' '.join(sys.argv[1:])

    return config


def do_timings(client):
    """Perform timings test"""
    import timeit
    iterations = 10000     # send/recv this many messages
    start_time = timeit.default_timer()
    for ndx in range(iterations):
        data = 'ndx=%d' % ndx
        response = client.send(data)
        if data not in response:
            pdb.set_trace()
    elapsed = timeit.default_timer() - start_time
    sys.stdout.write('%d logs, elapsed time: %f\n' % (iterations, elapsed))
    sys.stdout.write('Timed at %d messages per second\n' %
            int(iterations/elapsed))
    print '%d logs, elapsed time: %f' % (iterations, elapsed)
    print '%d messages per second' % int(iterations/elapsed)


def main():
    """
    Dummy mainline for simple testing.
    Simply send strings, print responses

    This driver *must* be used with server_create_class.py
    because the responses have been wired in and the
    code below checks for responses.
    """
    global PORT

    # =========================
    # Standard initialization
    # =========================

    # Default values for configuration
    config = getopts({
        'node': 'localhost',
        'port': PORT,
        'noisy': False,
        'timing': False,
        'id_name': platform.node(),
        'message': '',
    })
    client = ClientCreateClass(config)
    if client is None:
        sys.stderr.write('Cannot create ClientClass!\n')
        sys.exit(1)
    config = client.config
    client.start()

    sys.stdout.write('Started client, pid %d port %s node %s\n' %
            (os.getpid(), str(config['port']), config['node']))

    if config['timing']:
        do_timings(client)
    else:
        response = client.send(config['message'])
        sys.stdout.write(response + '\n')

    client.join()

if __name__ == '__main__':
    main()

