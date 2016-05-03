#!/usr/bin/env python
"""
    A logging task that sends a log from the command line
    to logCollector.

    Simple, but useful at times.

    The log collector must be running.
    All defaults taken from logConfig.py
    Therefore, set the proper port in logConfig.py .
"""
import sys
import platform
import loggingClientTask
import logConfig
import utils

def usage():
    """Print the usage blurb."""
    print 'logCmd [--port=<port#>] --level=<level>'
    print '    --port = port to send to logCollector'
    print '    --level = <level> where <level> is one of:'
    print '          DEBUG, INFO, WARNING, CMD, ERROR, CRITICAL'
    sys.exit(1)


def parseOpts():
    import getopt

    try:
        opts, args = getopt.gnu_getopt(
            sys.argv[1:], 'ahnqt',
            ['port=',     # Port # to send message
             'level=',    # level of msg
             'help'       # Help blurb
            ]
        )
    except getopt.GetoptError as err:
        print err
        usage()
        return 1

    # Number leading args to shift out
    shift_out = 0
    for opt, arg in opts:
        if opt == '--help':
            usage()
            continue
        elif opt == '--port':
            logConfig.PORT = int(arg)
            shift_out += 1
            continue
        elif opt == '--level':
            if arg not in utils.LOG_LEVELS:
                print 'Invalid log level: %s' % arg
                usage()
            shift_out += 1
            logConfig.LOG_LEVEL = arg
            continue
    for ndx in range(shift_out):
        del sys.argv[1]

def level_name_to_fcn(client):
    """Map a level name to the client send function. """
    # All the log levels in the remote logger
    REMOTE_LOG_LEVELS = {
        'DEBUG': client.debug,
        'CMD': client.cmd,
        'INFO': client.info,
        'WARNING': client.warning,
        'ERROR': client.error,
        'CRITICAL': client.critical}
    client_fcn = REMOTE_LOG_LEVELS[logConfig.LOG_LEVEL]
    return client_fcn

def main():
    parseOpts()
    client = loggingClientTask.LoggingClientClass(platform.node())
    client.start()

    msg = ' '.join(sys.argv[1:])
    client_fcn = level_name_to_fcn(client)
    return client_fcn(msg)

if __name__ == '__main__':
    sys.exit(main())
