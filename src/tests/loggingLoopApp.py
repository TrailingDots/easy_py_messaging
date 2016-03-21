#!/usr/bin/env python
"""
    Sample code of an app logging data.
"""
import zmq
import os
import sys
import time
import threading
sys.path.append('./')
sys.path.append('../lib')
import logConfig
import signal


class ClientTask(threading.Thread):
    """ClientTask"""
    def __init__(self, id, max_cnt):
        self.id = str(id)
        self.max_cnt = int(max_cnt)
        threading.Thread.__init__(self)

    def run(self):
        import time     # TODO FIXME - does this work? Have had runtime problems...
        context = zmq.Context()
        socket = context.socket(zmq.DEALER)
        identity = u'worker-%s' % self.id
        socket.identity = identity.encode('ascii')
        socket.connect(logConfig.APP_SOCKET)
        print('loggingApp: Client %s started' % (identity))
        poll = zmq.Poller()
        poll.register(socket, zmq.POLLIN)
        for reqs in range(self.max_cnt):
            thisMsg = 'request #%d' % reqs
            print('Req #%d sent "%s"' % (reqs, thisMsg))
            socket.send_string(thisMsg)
            time.sleep(1)
        socket.close()
        context.term()


def main():
    print '>>> loggingApp: pid %d' % os.getpid()
    name = 'RaspPi' + str(os.getpid())

    # How many messages to output. If not provided, then
    # send 1M (infinite).
    max_cnt = sys.argv[1] if len(sys.argv) > 1 else '1000000'

    # Unit tests must usually kill this process
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    signal.signal(signal.SIGTERM, signal.SIG_DFL)
    
    client = ClientTask(name, max_cnt)
    client.start()


if __name__ == "__main__":
    main()
