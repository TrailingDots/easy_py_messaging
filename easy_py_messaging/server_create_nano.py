#!/bin/env python
import server_create_class
def handle_request(ident, msg):
    return ident, msg + '_resp'
config = { 'in_fcn': handle_request }
server = server_create_class.ServerCreateClass(config)
server.start()
while True:
    server.join(1)
