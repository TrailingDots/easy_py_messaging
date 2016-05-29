#!/usr/bin/env python
"""
    Sample code of an app logging data.
"""
import os
import sys
import time
import threading
import logConfig
import signal


class ClientTask(threading.Thread):
    """ClientTask"""
    def __init__(self, id_name, iterations):
        import timeit
        import zmq
        self.context = None
        self.id_name = id_name
        self.iterations = int(iterations)

        self.timeit = timeit
        self.time = time
        self.zmq = zmq
        threading.Thread.__init__(self)

    def run(self):
        self.context = self.zmq.Context()
        socket = self.context.socket(self.zmq.DEALER)
        identity = u'worker-%s' % self.id_name
        socket.identity = identity.encode('ascii')
        socket.connect(logConfig.getAppSocket())
        print('loggingLoopApp: Client %s started' % (identity))
        poll = self.zmq.Poller()
        poll.register(socket, self.zmq.POLLIN)

        start_time = self.timeit.default_timer()

        for reqs in range(self.iterations):
            this_msg = 'request #%d' % reqs
            print('Req #%d sent "%s"' % (reqs, this_msg))
            socket.send_string(this_msg)
            self.time.sleep(1)

        elapsed = self.timeit.default_timer() - start_time
        print '%d logs, elapsed time: %f' % (self.iterations, elapsed)
        print '%d messages per second' % int(self.iterations/elapsed)

        socket.close()
        self.context.term()


def main():
    print '>>> loggingLoopApp: pid %d' % os.getpid()
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
