#!/usr/bin/env python
import client_create_class

if __name__ == '__main__':
    # Default values for configuration.
    config = {
        #'node': 'localhost',
        #'port': 5590,
    }
    client = client_create_class.ClientCreateClass(config)
    client.start()

    msg1 = 'Hello world!'
    msg2 = 'The second message'
    msg3 = 'abcdefghijklmnopqrstuvwxyz'
    msg4 = 'numbers: 0123456789'
    msg5 = 'qwerty keyboard'
    for msg in [msg1, msg2, msg3, msg4, msg5]:
        print 'Sending : "%s"' % msg
        response = client.send(msg)
        print 'Response: "%s"\n' % response
    client.join()

