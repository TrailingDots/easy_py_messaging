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
    print 'logCmd [--port=<port#>] --node=<node> --level=<level>'
    print '    --port = port to send to logCollector'
    print '    --node = Node name or IP address to send messages'
    print '    --level = <level> where <level> is one of:'
    print '          DEBUG, INFO, WARNING, CMD, ERROR, CRITICAL'
    sys.exit(1)


def parseOpts():
    """Interpret command line options."""

    import getopt

    try:
        opts, _ = getopt.gnu_getopt(
            sys.argv[1:], 'ahnqt',
            ['port=',     # Port # to send message
             'node=',     # Node to send message
             'level=',    # level of msg
             'help'       # Help blurb
            ]
        )
    except getopt.GetoptError as err:
        print err
        usage()

    # Number leading args to shift out
    shift_out = 0
    for opt, arg in opts:
        if opt == '--help':
            usage()
        elif opt == '--node':
            logConfig.DEFAULT_SERVER = arg
            logConfig.APP_HOST = arg
            shift_out += 1
            break
        elif opt == '--port':
            try:
                logConfig.PORT = int(arg)
            except ValueError as err:
                print 'Invalid port: %s' % str(err)
                usage()
            shift_out += 1
            continue
        elif opt == '--level':
            if arg not in utils.LOG_LEVELS:
                print 'Invalid log level: %s' % arg
                usage()
            shift_out += 1
            logConfig.LOG_LEVEL = arg
            continue
    for _ in range(shift_out):
        del sys.argv[1]


def level_name_to_fcn(client, level=None):
    """Map a level name to the client send function. """
    if level is None:
        level = logConfig.LOG_LEVEL
    # All the log levels in the remote logger
    REMOTE_LOG_LEVELS = {
        'DEBUG': client.debug,
        'CMD': client.cmd,
        'INFO': client.info,
        'WARNING': client.warning,
        'ERROR': client.error,
        'CRITICAL': client.critical}
    client_fcn = REMOTE_LOG_LEVELS[level]
    return client_fcn


def main():
    parseOpts()
    client = loggingClientTask.LoggingClientClass(platform.node())
    client.start()

    msg = ' '.join(sys.argv[1:])
    return level_name_to_fcn(client, logConfig.LOG_LEVEL)(msg)

if __name__ == '__main__':
    sys.exit(main())
