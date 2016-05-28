#!/bin/env python
import zmq
import sys
import threading
import time


class ServerCreateClass(threading.Thread):
    """
    Create a server class that receives requests and
    sends server responses.
    Modeled after asyncsrv.py in the ZeroMQ zguide.
    """

    def __init__(self, config):
        """
        config as a dictionary describes the client configuration.
        All but id_name keywords are required.

        id_name = These names appear in the log entry as
            an identifier of the source
            of the log entry.

        port = port to use for communications.
        """

        super(ServerCreateClass, self).__init__()
        self.config = config
        self.workers = []   # Thread the workers are on.
        self.is_noisy = self.config.get('noisy', False)


    def demandIntPort(self):
        """Insist that key be in the config dict.
        Return the valid in the config dict."""
        port = self.config.get('port', 5590)

        # Insist the key is an integer
        try:
            port = int(port)
        except ValueError as err:
            sys.stdout.write('port "%s" must be an integer. %s\n' %
                    (str(port), str(err)))
            sys.exit(1)
        return port

    def run(self):
        context = zmq.Context()
        frontend = context.socket(zmq.ROUTER)
        port = self.demandIntPort()
        scheme = self.config.get('scheme', 'tcp')
        endpoint = '%s://*:%s' % (scheme, str(port))
        sys.stdout.write('endpoint: "%s" noisy=%s\n' % (endpoint, self.is_noisy))
        frontend.bind(endpoint)

        backend = context.socket(zmq.DEALER)
        backend.bind('inproc://backend')

        self.config['context'] = context

        # Spawn some worker threads
        for _ in range(5):
            worker = ServerWorker(self.config)
            worker.start()
            self.workers.append(worker)

        zmq.proxy(frontend, backend)

        frontend.close()
        backend.close()
        context.term()


class ExitException(Exception):
    """Exception that indicates an exit."""
    pass

is_alive = True


class ServerWorker(threading.Thread):
    """ServerWorker"""

    def __init__(self, config):
        super(ServerWorker, self).__init__()
        from os import kill, getpid
        from signal import SIGINT
        self.kill = kill
        self.getpid = getpid
        self.SIGINT = SIGINT

        self.context = config['context']
        self.config = config
        self.is_noisy = self.config.get('noisy', False)

    def run(self):
        global is_alive
        worker = self.context.socket(zmq.DEALER)
        worker.connect('inproc://backend')
        while is_alive:
            ident, msg = worker.recv_multipart()
            if self.is_noisy: print 'recv ident: %s msg: %s' %(ident, msg)
            response = self.config['in_fcn'](ident, msg)
            ident, resp_msg = response
            worker.send_multipart([ident, resp_msg])
            if self.is_noisy: print 'respond ident: %s msg: %s' %(ident, resp_msg)
            if '@EXIT' in resp_msg:
                is_alive = False
                time.sleep(1)   # Some time to send response.
                break

        worker.close()
        self.kill(self.getpid(), self.SIGINT)

