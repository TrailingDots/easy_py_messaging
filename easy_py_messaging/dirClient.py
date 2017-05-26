#!/bin/env python
#
#  Lazy Pirate client
#  Use zmq_poll to do a safe request-reply
#
# port_request module
#

import sys
import platform
import zmq

import apiLoggerInit
import logConfig
import loggingClientTask


class DirClient(object):
    """
    Class that encapsulates sending names to the
    directory service. This client sends a port
    name to  dirSvc. dirSvc looks up the name and
    replies with the port for that name.
    If no port exists for that name, dirSvc
    assigns a new port and returns the port number.
    """
    default_config = {
        'clear': False,
        'memory_filename': './dirSvc.data',
        'port': str(logConfig.DIR_PORT),
        'noisy': False,
    }

    def __init__(self, in_config=default_config.copy()):
        self.zmq = zmq
        self.request_timeout = 2500
        self.request_retries = 1000  # Wait a long time for the server
        self.config = DirClient.default_config.copy()

        if 'port' in in_config:
            self.config['port'] = in_config['port']
        if 'memory_filename' in in_config:
            self.config['memory_filename'] = in_config['memory_filename']
        if 'clear' in in_config:
            self.config['clear'] = in_config['clear']
        self.server_endpoint = logConfig.getDirAppSocket()
        self.context = self.zmq.Context(1)
        self.client = self.context.socket(self.zmq.REQ)

        try:
            self.client.connect(self.server_endpoint)
        except zmq.ZMQError as err:
            sys.stderr.write('Server endpoint: %s  Error:%s\n' %
                    (self.server_endpoint, str(err)))
            sys.stderr.write('Likely an invalid node designation\n')
            sys.exit(1)     # Cannot continue  - invalid endpoint!

        self.poll = self.zmq.Poller()
        self.poll.register(self.client, self.zmq.POLLIN)
        if self.config['noisy']: print("I: Connecting to server... port %s" %
            str(self.config['port']))
        self.loggingClient = self.logCollectorSetup()
        self.loggingClient.info('app=DirClient,status=starting')

    def logCollectorSetup(self):
        """Perform operations to start logging."""
        global loggingClient

        apiLoggerInit.loggerInit()
        loggingClient = loggingClientTask.LoggingClientClass(platform.node())
        if loggingClient is None:
            sys.stderr.write('Cannot create LoggingClientClass!\n')
            sys.exit(1)
        loggingClient.start()
        loggingClient.info('app=dirClient,status=started-inited')
        return loggingClient

    def port_request(self, name):
        """
        Given a name, ask the directory service for the
        associated port.

        REFACTOR ME! Too damn long and complicated.
        """
        retries_left = self.request_retries
        while retries_left:
            request = str(name)
            if self.config['noisy']: print("I: Sending (%s)" % request)
            self.loggingClient.debug('app=dirClient,request=%s' % name)
            self.client.send(request)

            expect_reply = True
            while expect_reply:
                socks = dict(self.poll.poll(self.request_timeout))
                if socks.get(self.client) == self.zmq.POLLIN:
                    reply = self.client.recv()
                    if not reply:
                        break
                    if self.config['noisy']: print("I: Server replied (%s)" % reply)
                    self.loggingClient.debug('app=dirClient,request=%s,reply=%s' %
                            (str(request), str(reply)))
                    return reply

                else:
                    if self.config['noisy']: print("W: No response from server, retrying...")
                    # Socket is confused. Close and remove it.
                    self.client.setsockopt(self.zmq.LINGER, 0)
                    self.client.close()
                    self.poll.unregister(self.client)
                    retries_left -= 1
                    if retries_left == 0:
                        if self.config['noisy']: print("E: Server seems to be offline, abandoning")
                        break
                    if self.config['noisy']: print("I: Reconnecting and resending (%s)" % request)
                    # Create new connection
                    self.client = self.context.socket(self.zmq.REQ)
                    self.client.connect(self.server_endpoint)
                    self.poll.register(self.client, self.zmq.POLLIN)
                    self.client.send(request)

        self.context.term()


def usage():
    """Print the usage blurb and exit."""
    print 'dirSvc [--help] [--port] [--memory-file=memory_filename]'
    print '\t\t[--clear]'
    print '\t--help         = This blurb'
    print '\t--port=aport   = Port to expect queries.'
    print '\t--node=node_name = On which nodes is dirSvc running?'
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

    import getopt
    try:
        opts, _ = getopt.gnu_getopt(
            sys.argv[1:], 'cpmnh',
            ['port=',           # Port # to expect messages
             'memory-file=',    # Which file to persist names
             'node=',           # On which node is dirSvc runnnig.
             'noisy',           # Noisy reporting
             'help',            # Help blurb
             'clear'            # If set, clean memory-file at start
            ]
        )
    except getopt.GetoptError as err:
        print str(err)
        usage()

    # Number leading args to shift out
    shift_out = 0
    config = DirClient.default_config.copy()
    for opt, arg in opts:
        if opt in ['-h', '--help']:
            usage()
        elif opt in ['--node']:
            logConfig.DEFAULT_SERVER = arg
            logConfig.APP_HOST = arg
            break
        elif opt in ['-n', '--noisy']:
            config['noisy'] = True
            shift_out += 1
            continue
        elif opt in ['p', '--port']:
            try:
                # Ensure a valid integer port
                _ = int(arg)
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
    for _ in range(shift_out):
        del sys.argv[1]

    dir_client = DirClient(config)

    if config['noisy']:
        print 'options: %s' % str(config)

    for request in sys.argv[1:]:
        sys.stdout.write(str(request) + ' ')
        response = dir_client.port_request(request)
        sys.stdout.write(str(response) + '\n')
    sys.exit(0)

if __name__ == '__main__':
    """Command line for mapping name to port."""
    main()

