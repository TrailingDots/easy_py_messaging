#!/usr/binenv python
#
# Class that creates clients to send
# messages and receive a response.
#

import sys
import os
import platform

import client_create_class

# Default port
PORT = 5590


def usage():
    """Print the usage blurb and exit."""
    print 'client_create_test.py [--help] [--port]'
    print '\t--help         = This blurb'
    print '\t--port=aport   = Port to expect queries.'
    print '\t--node=anode   = Node name or IP address of server_create_class.'
    print '\t\tDefault is localhost'
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
            pdb.set_trace() # Should not happen
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

    # =========================
    # Standard initialization
    # =========================
    port = 5590

    # Default values for configuration
    config = getopts({
        'node': 'localhost',
        'port': port,
        'timing': False,
        'id_name': platform.node(),
        'message': '',
    })
    client = client_create_class.ClientCreateClass(config)
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

