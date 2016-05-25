#!/bin/env python
#
# Example of server receiving messages and sending responses.
#


import sys
import os
import time
import zmq
import platform
from send_recv_task import SendRecvTask

NOISY = True

# The port used for communicatingcommunicating.
PORT = 5590

def main():
    """
    Main processing loop.
    The ZeroMQ pattern is The Lazy Pirate
    """
    global PORT

    host = '120.0.0.1'
    context = zmq.Context(1)
    server = context.socket(zmq.REP)
    port = PORT
    try:
        # Listen to all traffic both local and remote on this port.
        end_point = "tcp://%s:%s" % (host, str(port))
        sys.stdout.write('connect to endpoint %s\n' % end_point)
        server.connect(end_point)
    except zmq.ZMQError as err:
        sys.stderr.write('ZMQError: %s\n' % err)
        sys.stderr.write('Please kill other instances of this program.\n')
        sys.stderr.write('Or: another program may be using port %s\n' %
            str(port))
        sys.exit(1)

    sys.stdout.write('client started. pid %s port %s\n' %
        (str(os.getpid()), str(port)))

    config = {
        'port': 5590,
        'id_name': platform.node(),
    }
    send_recv = SendRecvTask(config)

    sequence = 0
    while True:
        # Wait for a port naming request.
        # Notice this recv waits forever. This implies
        # a dirty directory will not get cleared.
        # Should a timeout change this logic?
        if NOISY: print("I: wait for msg port: %s)" % port)
        msg = send_recv.recv()
        if NOISY: print("I: Normal msg (%s)" % msg)
        if str(msg) == '@EXIT':
            break
        sequence += 1
        send_recv.send('%s : processed' % msg)

    # Shut down ZeroMQ sockets in an orderly manner.
    server.close()
    context.term()

if __name__ == '__main__':
    main()
