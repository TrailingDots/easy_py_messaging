#!/usr/bin/env python
"""
    Sample code of an app logging data.
"""
import zmq
import os
import sys
import time
import timeit
import threading
sys.path.append('./')
sys.path.append('../lib')
import logConfig
import signal

def my_sleep(secs):
    time.sleep(secs)

class ClientTask(threading.Thread):
    """ClientTask"""
    def __init__(self, id_name, iterations):
        self.context = None
        self.id_name = id_name
        self.iterations = int(iterations)
        threading.Thread.__init__(self)

    def run(self):
        self.context = zmq.Context()
        socket = self.context.socket(zmq.DEALER)
        identity = u'worker-%s' % self.id_name
        socket.identity = identity.encode('ascii')
        socket.connect(logConfig.APP_SOCKET)
        print('loggingApp: Client %s started' % (identity))
        poll = zmq.Poller()
        poll.register(socket, zmq.POLLIN)

        start_time = timeit.default_timer()

        for reqs in range(self.iterations):
            thisMsg = 'request #%d' % reqs
            #print('Req #%d sent "%s"' % (reqs, thisMsg))
            socket.send_string(thisMsg)

        elapsed = timeit.default_timer() - start_time
        print '%d logs, elapsed time: %f' % (self.iterations, elapsed)
        print '%d messages per second' % int(self.iterations/elapsed)

        socket.close()
        self.context.term()


def main():
    print '>>> loggingApp: pid %d' % os.getpid()
    name = 'RaspPi' + str(os.getpid())

    # How many messages to output. If not provided, then
    # send 1M (infinite).
    iterations = sys.argv[1] if len(sys.argv) > 1 else '1000000'
    iterations = int(iterations)

    # Unit tests must usually kill this process
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    signal.signal(signal.SIGTERM, signal.SIG_DFL)
    
    client = ClientTask(name, iterations)

    client.start()


if __name__ == "__main__":
    main()
