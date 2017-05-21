#!/bin/env python
#
# Demo socket program.
#
# This program listens to a socket and writes
# any input to standard out.
#
# Kill this program with Ctrl-C
#
# Reference:
#   https://docs.python.org/2/howto/sockets.html
#

import sys
import socket

import pdb

DEFAULT_PORT = 5570

def usage():
    print """
    demoSocket.py [port]
    port = The port to listen to. If omitted, the port is 5570.
    """
    sys.exit(0)

def main():
    port = DEFAULT_PORT
    print "sys.argv:" + str(sys.argv)
    print 'len(sys.argv):' + str(len(sys.argv))
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    print 'Listening on port ' + str(port)

    # Create an INET, STREAMing socket
    serversocket = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM)
    # bind the socket to a public host,
    # and a well-known port
    serversocket.bind((socket.gethostname(), port))
    # Become a server socket.
    # Allow up to 5 connections.
    serversocket.listen(5)

    # Now that we have a "server" socket, listening on 
    # a port, we can enter the mainloop:
    while 1:
        # Accept connections from outside
        (clientsocket, address) = serversocket.accept()
        # Now do something with the clientsocket
        # in this case, pretend this is a threaded server
        ct = client_thread(clientsocket)
        ct.run()

if __name__ == "__main__":
    main()

