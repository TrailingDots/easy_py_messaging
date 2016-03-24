#!/usr/bin/env python

import os
import sys
sys.path.append('./')
sys.path.append('../lib')
import zmq
import signal
import atexit

import logConfig
import apiLoggerInit
import utils
import logComponents


def exiting(exit_msg):
    print('logCollector: atexit:' + exit_msg)


def signalUSR1Handler(signum, frame):
    """
    When a USR1 signal arrives, the NOISY debugging switch
    get toggles. This allows a dynamic way to trace incoming
    log messages. 
        kill -USR1  1234    # 1234 is the pid of logCollector.
    """
    logConfig.NOISY = not logConfig.NOISY
    print('Log tracing now %s' % ('ON' if logConfig.NOISY else 'OFF'))


class LogCollectorTask(object):
    """
    LogCollectorTask. One and only one instance of this
    class should exist. The LogCollectorTask collects logs
    from the logging client task.
    """
    def __init__(self, context, id_name):
        self.id_name = id_name
        self.context = context
        apiLoggerInit.loggerInit('logCol1')
        self.frontend = self.context.socket(zmq.ROUTER)

    def signal_handler(self, signum, frame):
        print 'custom handler, signum:"%s"' % signum
        self.frontend.close()
        self.context.term()
        sys.exit(1)

    def signal_usr1_handler(self, signum, frame):
        print 'custom usr1 handler, signum:"%s"' % signum
        logConfig.NOISY = not logConfig.NOISY

    def run(self):
        """
        SIGINT and SIGTERM kill the process.
        SIGUSR1 toggle the NOISY debug of incoming logs.
            kill -USR1 1234 # "1234" is pid of this process.
        """
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGUSR1, signalUSR1Handler)

        try:
            self.frontend.bind(logConfig.COLL_SOCKET)
        except zmq.ZMQError as err:
            sys.stderr.write('ZMQError: %s\n' % err)
            sys.stderr.write('Please kill other instances of this program.\n')
            sys.stderr.write('Or: another program may be using %s\n' % \
                    str(logConfig.COLL_SOCKET))
            sys.exit(1)

        while True:
            try:
                ident, msg = self.frontend.recv_multipart()
            except KeyboardInterrupt as err:
                sys.stderr.write('Keyboard interrupt\n')
                print 'ident:%s, msg:%s' % (str(ident), str(msg))
                exiting('keyboard interrupt')
            except Exception as err:
                sys.stderr.write('Exception: %s\n' % str(err))
                exiting('exception')

            msg += utils.PAYLOAD_CONNECTOR + \
                    ('host=%s' % ident)   # Track by hostname as well
            if logConfig.NOISY:           # User has requested echo to console?
                print msg
            log_comp = logComponents.LogComponents.msg_to_components(msg)
            if log_comp.level in utils.LOG_LEVELS:
                log_fcn = utils.LOG_LEVELS[log_comp.level]
                log_fcn(log_comp.payload)

        # Should never get here. This code stops with SIGINT or SIGTERM.
        self.frontend.close()
        self.context.term()



def usage():
    print 'logCollector [--file=logFilename] [-a] [-t]'
    print '     logFilename = name of file to place logs'
    print '     -a  Logs will be appende dto logFilename. Default'
    print '     -t  logFilename will be truncated before writing logs.'
    print '-a and -t apply only when --file specifics a valid filename.'
    print '--noisy or -n : Echo message to console. Useful for debugging.'
    print 'If logFilename does not exist, it will be created'
    print ''
    print 'logCollector [--help]'
    print '     This message'
    print ''
    print 'To toggle printing of messages received:'
    print '    kill -USR1 <pid>'
    sys.exit(1)


def main():
    """main function"""
    import getopt

    print 'logCollector: pid %d' % os.getpid()
    atexit.register(exiting, 'Exiting logCollector')

    try:
        opts, args = getopt.gnu_getopt(
            sys.argv[1:], 'ahnt',
            ['file=',   # output file instead of stdiout
             'a',       # Log file to be appended to file
             'noisy',   # Noisy - messages printed to console as well as on a file.
             't',       # Log file to be emptied
             'help',    # help message
            ]
        )
    except getopt.GetoptError as err:
        print err
        usage()
        return 1

    log_filename = None  # Default for log is stdout
    append = True
    for opt, arg in opts:
        if opt in ['-h', '--help']:
            usage()
            continue
        elif opt in ['-a']:
            append = True   # Append to log file
            continue
        elif opt in ['-n', '--noisy']:
            logConfig.NOISY = True    # Echo message to console
            continue
        elif opt in ['-t']:
            append = False  # Truncate the log file
            continue
        elif opt in ['--file']:
            # TODO: This does  NOT work!!! FIXME BUG
            log_filename = arg
            continue
        else:
            print 'Unknown option:' + opt
            usage()
            continue

    id_name = ''
    if len(sys.argv) > 0:
        id_name = sys.argv[0]
    if log_filename:
        # A log filename MUST be supplied for an append
        logConfig.APPEND_TO_LOG = append
        logConfig.LOG_FILENAME = log_filename

    context = zmq.Context()
    server = LogCollectorTask(context, id_name)
    server.run()

    server.join()


if __name__ == "__main__":
    main()
