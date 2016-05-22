#!/bin/env python
# Async Client/server pattern - p. 111

import zmq
import sys
import os
import threading
import time
from random import randint, random

HOST = '127.0.0.1'
PORT = 5590

def get_endpoint(host, port):
    return 'tcp://%s:%s' % (host, str(port))

def tprint(msg):
    """like print, but won't get newlines confused with multiple threads"""
    sys.stdout.write(msg + '\n')
    sys.stdout.flush()

class ClientTask(threading.Thread):
    """ClientTask"""
    def __init__(self, id):
        self.id = id
        threading.Thread.__init__ (self)

    def run(self):
        context = zmq.Context()
        socket = context.socket(zmq.DEALER)
        identity = u'worker-%d' % self.id
        socket.identity = identity.encode('ascii')
        socket.connect(get_endpoint(HOST, PORT))
        print('Client %s started' % (identity))
        poll = zmq.Poller()
        poll.register(socket, zmq.POLLIN)
        reqs = 0
        while True:
            reqs = reqs + 1
            request = 'req_%d' % reqs
            print('Req #%s sent..' % (reqs))
            socket.send_string(u'%s' % (request))
            for i in range(5):
                sockets = dict(poll.poll(1000))
                if socket in sockets:
                    msg = socket.recv()
                    tprint('Client %s received: %s' % (identity, msg))
                elif len(sockets) != 0: 
                    tprint('Client cannot find socket. %s' % str(sockets))
                else:
                    # Ignore if poller has no responses, yet.
                    pass

        socket.close()
        context.term()

def main():
    """main function"""
    global HOST
    global PORT
    print('Client %s started: host %s port %s' %
            (os.getpid(), HOST, PORT))
    client = ClientTask(os.getpid())
    client.start()


if __name__ == "__main__":
    main()
