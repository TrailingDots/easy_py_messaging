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

NOISY = True   # Set to True for debug messages

REQUEST_TIMEOUT = 2500
REQUEST_RETRIES = 1000  # Wait a long time for the server
port = logConfig.get_directory_port()
SERVER_ENDPOINT = "tcp://127.0.0.1:%d" % port

print("I: Connecting to server... port %d" % port)

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


if __name__ == '__main__':
    """Stupid sanity test"""
    names = ['pump01', 'pump01', 'temp01', 'temp02', 
            'pump02', 'pump01']

    for aname in names + names + names + names:
        port = port_request(aname)
        print('%s: %s' % (aname, str(port)))

