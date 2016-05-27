#!/bin/env python
import server_create_class
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)
signal.signal(signal.SIGTERM, signal.SIG_DFL)

def handle_request(ident, msg):
    return ident, msg + '_resp'

if __name__ == "__main__":
    config = {
        #'port': 5590,
        'noisy': True,
        'in_fcn': handle_request,
    }

    server = server_create_class.ServerCreateClass(config)
    server.start()

    while True:
        server.join(1)
