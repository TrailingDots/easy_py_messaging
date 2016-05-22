#!/bin/env python
#
# Example of reseiver of messages and sending responses.
#


import sys
import os
import time
import zmq
import json
import pickle
import atexit

import platform
from send_recv_task import SendRecvTask

NOISY = True

# The port used for communicatingcommunicating.
PORT = 5590

'''
def usage():
    """Print the usage blurb and exit."""
    print 'dirSvc [--help] [--port] [--memory-file=memory_filename]'
    print '\t\t[--clear]'
    print '\t--help         = This blurb'
    print '\t--port=aport   = Port to expect queries.'
    print '\t--memory-file=memory_filename   = File to persist names'
    print '\t\tDefault: ./dirSvc.data'
    print '\t--clear        = Clear memory-file upon starting.'
    print '\t\tDefault: False, do not clear but load memory-file'
    print ''
    sys.exit(1)


def parseOpts():
    import getopt
    global NOISY
    global PORT

    try:
        opts, args = getopt.gnu_getopt(
            sys.argv[1:], 'cpmh',
            ['port=',           # Port # to expect messages
             'memory-file=',    # Which file to persist names
             'help',            # Help blurb
             'noisy',           # Turn noise on
             'clear'            # If set, clean memory-file at start
            ]
        )
    except getopt.GetoptError as err:
        print err
        usage()

    # Number leading args to shift out
    shift_out = 0
    config = {
            'clear': False,
            'memory_filename': './dirSvc.data',
            'port': str(PORT),
            }
    for opt, arg in opts:
        if opt in ['-h', '--help']:
            usage()
        elif opt in ['--noisy']:
            NOISY = True
            continue
        elif opt in ['p', '--port']:
            try:
                # Ensure a valid integer port
                int_port = int(arg)
            except Exception as err:
                sys.stdout.write(str(err) + '\n')
                usage()
            config['port'] = arg
            PORT = int_port
            shift_out += 1
            continue
        elif opt in ['m', '--memory-file']:
            shift_out += 1
            config['memory_filename'] = arg
            continue
        elif opt in ['c', '--clear']:
            shift_out += 1
            config['clear'] = True
            continue
    # pass the remaining args to the rest of the program.
    for ndx in range(shift_out):
        del sys.argv[1]

    return config
'''

def main():
    """
    Main processing loop.
    The ZeroMQ pattern is The Lazy Pirate
    """
    global PORT

    #config = parseOpts()
    #host = config['host']
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
