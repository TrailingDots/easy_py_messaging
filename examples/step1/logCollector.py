
import zmq
import sys
import threading

class ServerTask(threading.Thread):
    """ServerTask"""
    def __init__(self):
        threading.Thread.__init__ (self)

    def run(self):
        context = zmq.Context()
        frontend = context.socket(zmq.ROUTER)
        frontend.bind('tcp://*:5570')

        backend = context.socket(zmq.DEALER)
        backend.bind('inproc://backend')

        worker = ServerCollector(context)
        worker.start()

        zmq.proxy(frontend, backend)

        frontend.close()
        backend.close()
        context.term()

class ServerCollector(threading.Thread):
    """
    Class that collects the logs.
    For now, only print to the console.
    """
    def __init__(self, context):
        threading.Thread.__init__ (self)
        self.context = context

    def run(self):
        worker = self.context.socket(zmq.DEALER)
        worker.connect('inproc://backend')
        print('Collector started')
        while True:
            ident, msg = worker.recv_multipart()
            print('Collector received "%s" from "%s"' % (msg, ident))

        worker.close()

def main():
    server = ServerTask()
    server.start()
    server.join()

if __name__ == "__main__":
    main()
