#!/usr/binenv python
#
# This demonstate a simple basic example that creates clients to send messages
# and receive a response.
#
# This sends simple messages and prints the responses.
#

import sys
import os
import platform

import client_create_class

def main():
    """
    Basic mainline for basic demo of messaging..
    Simply sends a few strings, prints responses.

    This demo *must* be used with server_create_basic.py
    or server_create_test.py.

    The responses have been wired in and the
    code below checks for responses.
    """

    # Default values for configuration.
    config = {
        'node': 'localhost',
        'port': 5590,
        'id_name': platform.node(),
    }
    client = client_create_class.ClientCreateClass(config)
    if client is None:
        sys.stderr.write('Cannot create ClientClass!\n')
        sys.exit(1)
    config = client.config
    client.start()

    sys.stdout.write('Started client, pid %d port %s node %s\n' %
            (os.getpid(), str(config['port']), config['node']))

    # A list of messages that get sent and responses logged.
    msg1 = 'Hello world!'
    msg2 = 'The seond message'
    msg3 = 'abcdefghijklmnopqrstuvwxyz'
    msg4 = 'numbers: 0123456789'
    msg5 = 'qwerty'
    for msg in [msg1, msg2, msg3, msg4, msg5]:
        print 'Sending : "%s"' % msg
        response = client.send(msg)
        print 'Response: "%s"' % response
        print ''

    client.join()

if __name__ == '__main__':
    main()

