#!/usr/binenv python
#
# Example of an app that sends messages
# to another task and handles the return
# message.
#
#    Kinds of messaging (with and without timeout):
#        Fire and forget
#        Fire with response - wait/no wait
#        Reliable fire and forget
#        Reliable fire with response - wait/no wait
#    Ten distinct types.
#
#   Parms:
#        fire reliable/forget
#        fire response/no response
#        response wait/no wait
#
#   Approach:
#        Write server/client for each of the ten types as examples
#        Write a readable integration of all these.


import sys
import zmq
import threading
import time
import logConfig
import platform
import apiLoggerInit

# Default port
PORT = 5590

class SendRecvTask(threading.Thread):
    """
    Remote clients wishing to send logs to a server will create an instance of
    this class and call to send log messages to the server.
    """

    def __init__(self, config):
        """
        id_name = These names appear in
                the log entry as an indentifier of the source
                of the log entry.
        """
        global PORT

        self.context = None
        self.port = int(config['port'])
        self.id_name = str(config['id_name'])
        self.socket = None
        self.poll = None
        self.reqs = 0       # Count of messages
        threading.Thread.__init__(self)

    def run(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.DEALER)
        identity = u'%s' % str(self.id_name)
        self.socket.identity = identity.encode('ascii')
        app_socket = 'TCP://*:%d' % self.port
        self.socket.connect(app_socket)
        self.poll = zmq.Poller()
        self.poll.register(self.socket, zmq.POLLIN)

    def send(self, astr):
        """Send astr as a fully formed log message.
        Return True  for successful send.
               False for failure.
        """
        try:
            dummy = 0
            while self.socket is None:  # TODO FIXME Potential hang!!!
                dummy += 1
                if dummy > 200:
                    # Sometimes the socket "disappears" for awhile.
                    sys.stderr.write('Cannot get self.socket!')
                    raise Exception('Cannot obtain self.socket')
                time.sleep(0.1)
            self.socket.send_string(astr)
        except zmq.ZMQError as err:
            sys.stderr.write('ERROR in send_string:%s\n' % err)
            return 1    # Non-zero status == problems

        # Wait for confirmation of receipt.
        response = self.recv()
        return response

    def recv(self):
        return self.server.recv()

def main():
    """
    Simply send strings 
    """
    global PORT

    import timeit

    # =========================
    # Standard initialization
    # =========================
    client = SendRecvTask(platform.node(), port=PORT)
    if client is None:
        sys.stderr.write('Cannot create LoggingClientClass!\n')
        sys.exit(1)
    client.start()

    response = client.send('type=client,greeting=Hello world')
    print response

    # Get a timing
    iterations = 100000     # send/recv this many messages
    start_time = timeit.default_timer()
    for ndx in range(iterations):
        client.send('ndx=%d' % ndx) # Ignore response
    elapsed = timeit.default_timer() - startTime
    client.info('%d logs, elapsed time: %f' % (iterations, elapsed))
    client.info('Timed at %d messages per second' %
            int(iterations/elapsed))
    print '%d logs, elapsed time: %f' % (iterations, elapsed)
    print '%d messages per second' % int(iterations/elapsed)


if __name__ == '__main__':
    main()

