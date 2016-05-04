#!/bin/env python
#
#  Lazy Pirate client
#  Use zmq_poll to do a safe request-reply
#
# port_request module
#

import sys
import platform
import loggingClientTask
import logConfig
import utils
import zmq

import logConfig

NOISY = False   # Set to True for debug messages

REQUEST_TIMEOUT = 2500
REQUEST_RETRIES = 1000  # Wait a long time for the server
port = logConfig.get_directory_port()
SERVER_ENDPOINT = "tcp://127.0.0.1:%d" % port

if NOISY: print("I: Connecting to server... port %d" % port)

context = zmq.Context(1)
client = context.socket(zmq.REQ)
client.connect(SERVER_ENDPOINT)
poll = zmq.Poller()
poll.register(client, zmq.POLLIN)

def port_request(name):
    """
    Given a name, ask the directory service for the
    associated port.

    REFACTOR ME! Too damn long and complicated.
    """
    global client
    global context
    global poll
    global NOISY

    retries_left = REQUEST_RETRIES
    while retries_left:
        request = str(name)
        if NOISY: print("I: Sending (%s)" % request)
        client.send(request)

        expect_reply = True
        while expect_reply:
            socks = dict(poll.poll(REQUEST_TIMEOUT))
            if socks.get(client) == zmq.POLLIN:
                reply = client.recv()
                if not reply:
                    break
                if NOISY: print("I: Server replied (%s)" % reply)
                return reply

            else:
                if NOISY: print("W: No response from server, retrying...")
                # Socket is confused. Close and remove it.
                client.setsockopt(zmq.LINGER, 0)
                client.close()
                poll.unregister(client)
                retries_left -= 1
                if retries_left == 0:
                    if NOISY: print("E: Server seems to be offline, abandoning")
                    break
                if NOISY: print("I: Reconnecting and resending (%s)" % request)
                # Create new connection
                client = context.socket(zmq.REQ)
                client.connect(SERVER_ENDPOINT)
                poll.register(client, zmq.POLLIN)
                client.send(request)

    context.term()


def usage():
    """Print the usage blurb and exit."""
    print 'dirSvc [--help] [--port] [--memory-file=memory_filename]'
    print '\t\t[--clear]'
    print '\t--help         = This blurb'
    print '\t--port=aport   = Port to expect queries.'
    print '\t--noisy        = Noisy reporting. Echo progress.'
    print '\t--memory-file=memory_filename   = File to persist names'
    print '\t\tDefault: ./dirSvc.data'
    print '\t--clear        = Clear memory-file upon starting.'
    print '\t\tDefault: False, do not clear but load memory-file'
    print ''
    sys.exit(1)
       
def main():
    """
    Command line code to drive dirSvc.
    Run a single request and exit.
    Both logCollector and dirSvc must be running.
    """
    global NOISY
    import getopt
    try:
        opts, args = getopt.gnu_getopt(
            sys.argv[1:], 'cpmnh',
            ['port=',           # Port # to expect messages
             'memory-file=',    # Which file to persist names
             'noisy',           # Noisy reporting
             'help',            # Help blurb
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
            'port': str(logConfig.PORT),
            }
    for opt, arg in opts:
        if opt in ['-h', '--help']:
            usage()
            continue
        elif opt in ['-n', '--noisy']:
            NOISY = True
            shift_out += 1
            continue
        elif opt in ['p', '--port']:
            try:
                # Ensure a valid integer port
                int_port = int(arg)
            except Exception as err:
                sys.stdout.write(str(err) + '\n')
                usage()
            config['port'] = arg
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

    for request in sys.argv[1:]:
        sys.stdout.write(str(request) + ' ')
        response = port_request(request)
        sys.stdout.write(str(response) + '\n')
    sys.exit(0)

if __name__ == '__main__':
    """Command line for mapping name to port."""
    main()
