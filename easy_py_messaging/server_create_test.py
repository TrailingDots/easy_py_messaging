#!/bin/env python
import zmq
import sys
import signal
import server_create_class

signal.signal(signal.SIGINT, signal.SIG_DFL)
signal.signal(signal.SIGTERM, signal.SIG_DFL)


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
    print 'server_create_class.py [--help] [--port] \\'
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
        sys.stdout.write(str(err) + '\n')
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
                _ = int(arg)
            except ValueError as err:
                sys.stdout.write(str(err) + '\n')
                usage()
            config['port'] = arg
            continue

    return config

is_alive = True

def main():
    """main function"""
    global is_alive
    import platform
    # Default port for this dummy test.
    port = 5590
    config = {
        'scheme': 'tcp',
        'port': port,
        'in_fcn': handle_request,
        'id_name': platform.node(),
        'noisy': False,
    }

    config = getopts(config)

    server = server_create_class.ServerCreateClass(config)
    server.start()

    while is_alive:
        server.join(1)


if __name__ == "__main__":
    main()
