#!/bin/env python

import zmq
import sys
import os
import threading
import time
import signal

import pdb


signal.signal(signal.SIGINT, signal.SIG_DFL)
signal.signal(signal.SIGTERM, signal.SIG_DFL)


class ServerCreateClass(threading.Thread):
    """
    Create a server class that receives requests and
    sends server responses.
    Modeled after asyncsrv.py in the ZeroMQ zguide.
    """

    def __init__(self, config):
        """
        config as a dictionary describes the client configuration.
        All but id_name keywords are required.

        id_name = These names appear in the log entry as 
            an identifier of the source
            of the log entry.

        port = port to use for communications.

        host = name of host. For servers, this may commonly be '*'
            For clients, this may be 'localhost' or a node name.

        scheme = Typically 'tcp' or 'udp'.
        """

        threading.Thread.__init__(self)
        self.config = config
        self.workers = []   # Thread the workers are on.
        self.is_noisy = self.config['noisy']


    def demandIntKey(self, key):
        """Insist that key be in the config dict.
        Return the valid in the config dict."""
        if self.config[key] is None:
            sys.stdout.write('"%s" required, not found in ClientCreateClass.\n'
                    % key)
            traceback.print_exc()
            sys.exit(1)

        # Insist the key is an integer
        try:
            port = int(self.config['port'])
        except ValueError as err:
            sys.stdout.write('port "%s" must be an integer.\n' % 
                    str(self.config['port']))
            sys.exit(1)
        return port

    def run(self):
        context = zmq.Context()
        frontend = context.socket(zmq.ROUTER)
        port = self.demandIntKey('port')
        endpoint = '%s://*:%s' % (self.config['scheme'], str(port))
        print 'endpoint: "%s" noisy=%s\n' % (endpoint, self.is_noisy)
        frontend.bind(endpoint)

        backend = context.socket(zmq.DEALER)
        backend.bind('inproc://backend')

        self.config['context'] = context

        # Spawn some worker threads
        for i in range(5):
            worker = ServerWorker(self.config)
            worker.start()
            self.workers.append(worker)

        zmq.proxy(frontend, backend)

        frontend.close()
        backend.close()
        context.term()

class ExitException(Exception):
    pass

is_alive = True

class ServerWorker(threading.Thread):
    """ServerWorker"""
    def __init__(self, config):
        threading.Thread.__init__(self)
        self.context = config['context']
        self.config = config
        self.is_noisy = self.config['noisy']

    def run(self):
        global is_alive
        worker = self.context.socket(zmq.DEALER)
        worker.connect('inproc://backend')
        while is_alive:
            ident, msg = worker.recv_multipart()
            if self.is_noisy: print 'recv ident: %s msg: %s' %(ident, msg)
            response = self.config['in_fcn'](ident, msg)
            ident, resp_msg = response
            worker.send_multipart([ident, resp_msg])
            if self.is_noisy: print 'respond ident: %s msg: %s' %(ident, resp_msg)
            if '@EXIT' in resp_msg:
                is_alive = False
                time.sleep(1)   # Some time to send response.
                break

        worker.close()
        os.kill(os.getpid(), signal.SIGINT)


# ============================================================
# ============================================================
# The code from here onward exists ONLY as a command line
# driver to test for code coverage and as a convenience
# in using this class as a command line utility.
# ============================================================
# ============================================================

def handle_request(ident, msg):
    """
    Handler for incoming messages.
    This processes the client message and forms
    a response. In this test case, the response
    mostly echos the request.
    ident must *not* be changed.
    msg may become transformed into whatever.
    """
    return ident, msg + '_resp'


def usage():
    """Print the usage blurb and exit."""
    print 'server_create_class.py [--help] [--port]'
    print '\t\t[--noisy]'
    print '\t--help         = This blurb'
    print '\t--port=aport   = Port to expect queries.'
    print '\t--noisy        = Noisy reporting. Echo progress.'
    print ''
    sys.exit(1)


def getopts(config):
    """
    Read runtime options. Override defaults as necessary.
    """
    import getopt
    try:
        opts, args = getopt.gnu_getopt(
                sys.argv[1:], '',
                ['port=',       # Port to expect messages
                 'noisy',       # If present, noisy trail for debug
                 'help',        # Help blurb
                ])
    except getopt.GetoptError as err:
        print str(err)
        usage()

    for opt, arg in opts:
        if opt in ['--help']:
            usage()
        elif opt in ['--noisy']:
            config['noisy'] = True
            continue
        elif opt in ['--port']:
            try:
                # Insist on a valid integer for a port #
                int_port = int(arg)
            except ValueError as err:
                sys.stdout.write(str(err) + '\n')
                usage()
            config['port'] = arg
            continue

    return config


def main():
    """main function"""
    global is_alive
    import platform
    # Default port for this dummy test.
    port = 5590
    config = {
        'scheme': 'tcp',
        'host': 'localhost',
        'port': port,
        'in_fcn': handle_request,
        'id_name': platform.node(),
        'noisy': False,
    }

    config = getopts(config)

    server = ServerCreateClass(config)
    server.start()

    while is_alive:
        server.join(1)


if __name__ == "__main__":
    main()
