#!/bin/env python
#
# Example of sending messages to server_sync and handling responses.
#
import sys
import os
import zmq

import platform
from server_create_class import ServerCreateClass

# Set to True to observe chatter, False for silence.
NOISY = True

# The port used for communicating.
PORT = 5590

def main():
    """
    Main processing loop.
    The ZeroMQ pattern is The Lazy Pirate
    """
    global PORT

    context = zmq.Context(1)
    server = context.socket(zmq.REP)
    port = PORT
    try:
        # Listen to all traffic both local and remote on this port.
        server.bind("tcp://*:%s" % str(port))
        sys.stdout.write('bound to port %d\n' % port)
    except zmq.ZMQError as err:
        sys.stderr.write('ZMQError: %s\n' % err)
        sys.stderr.write('Please kill other instances of this program.\n')
        sys.stderr.write('Or: another program may be using port %s\n' %
            str(port))
        sys.exit(1)

    sys.stdout.write('client_sync started. pid %s port %s\n' %
        (str(os.getpid()), str(port)))

    config = {
        'port': 5590,
        'id_name': platform.node(),
    }
    send_recv = ServerCreateClass(config)

    sequence = 0
    while True:
        # Wait for a port naming request.
        # Notice this recv waits forever. This implies
        # a dirty directory will not get cleared.
        # Should a timeout change this logic?
        if NOISY: print("I: Normal send/recv port: %s)" % port)
        request = 'Msg %d' % sequence
        response = send_recv.send(request)
        if NOISY: print("I: Normal response (%s:%s)" % (request, response))
        if str(response) == '@EXIT':
            break
        sequence += 1

    # Shut down ZeroMQ sockets in an orderly manner.
    server.close()
    context.term()

if __name__ == '__main__':
    main()
