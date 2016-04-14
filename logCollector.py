#!/usr/bin/env python

import os
import sys
import zmq
import signal
import atexit

import logConfig
import apiLoggerInit
import utils
import logComponents


def exiting(exit_msg):
    print('logCollector: exiting:' + exit_msg)


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
        apiLoggerInit.loggerInit()
        self.frontend = self.context.socket(zmq.ROUTER)

    def signal_handler(self, signum, frame):
        SIGNALS_TO_NAMES_DICT = dict((getattr(signal, n), n)
            for n in dir(signal) if n.startswith('SIG') and '_' not in n)
        sys.stderr.write("logCollector terminated by signal %s" %
                SIGNALS_TO_NAMES_DICT[signum])
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
            sys.stderr.write('Or: another program may be using %s\n' %
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


def load_config(config_filename=None):
    """
     Read the config file is any. Look in the current
     directory for .logcollectorrc .
     If not there, look in $HOME/.logcollectorrc
     Any user flags will override config file settings.
    """
    def parse_config(file_handle):
        # Got a config file. Load and return
        config_lines = file_handle.read()
        config_params = eval(config_lines)
        return config_params

    def try_to_load_config(filename):
        try:
            file_handle = open(filename, 'r')
        except IOError as err:
            return None
        if file_handle:
            return parse_config(file_handle)

    config_dict = {}

    dir_config = None
    home_config = None
    if config_filename is None:
        config_filename = apiLoggerInit.DEFAULT_COLLECTOR_CONFIG_FILE
        dir_config = './' + config_filename
        home_config = os.getenv('HOME') + '/' + config_filename
    else:
        # User provided config filename.
        param_dict = try_to_load_config(config_filename)
        return param_dict

    file_handle = None
    param_dict = try_to_load_config(dir_config)
    if param_dict is not None:
        return param_dict

    param_dict = try_to_load_config(home_config)
    return param_dict


def load_config_file(config_filename):
    """
    User has requested a specific configuration filename to be loaded.
    """
    return load_config(config_filename)


def usage():
    print 'logCollector [--out-file=logFilename] [-a] [-t]'
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
            sys.argv[1:], 'ahnqt',
            ['out-file=',   # output file instead of stdiout
             'port=',       # Port to listen for msgs. Default in logConfig.
             'config=',     # Config filename to load.
             'noisy',       # Noisy - messages printed to console as well as on a file.
             'quiet',       # NOT Noisy - messages not printed to console
             'trunc',       # Log file to be truncated
             'help',        # help message
            ]
        )
    except getopt.GetoptError as err:
        print err
        usage()
        return 1

    # Read the config file if any. Look in the current
    # directory for .logcollectorrc .
    # If not there, look in $HOME/.logcollectorrc
    # Any user flags will override config file settings.
    config_dict = load_config()

    log_filename = None  # Default for log is stdout
    append = True
    config_filename = None  # Load and parse this config file instead of .logcollectorrc

    if config_dict is None:
        config_dict = {
            "append":True,          # Append logs to existing log file
            "out_file":'logs.log',  # Name of log file (could be absolute filename)
            "port":5570,            # Port to receive logs
            "noisy":False           # Silent. Toggle with Ctrl-D
        }

    return_dict = {}        # User provided config dict - if any.
    for opt, arg in opts:
        if opt in ['-h', '--help']:
            usage()
            continue
        elif opt in ['-a']:
            config_dict['append'] = True
            continue
        elif opt in ['-n', '--noisy']:
            config_dict['noisy'] = True
            continue
        elif opt in ['-q', '--quiet']:
            config_dict['noisy'] = False
            continue
        elif opt in ['-t', '--trunc']:
            config_dict['append'] = False
            continue
        elif opt in ['--out-file']:
            config_dict['out_file'] = arg
            continue
        elif opt in ['--config']:
            return_dict = load_config_file(arg)
            if not return_dict:
                usage()
            # Set whatever values read from config file.
            # If not provided, use the defaults.
            config_dict['append']   = return_dict.get('append', config_dict['append'])
            config_dict['out_file'] = return_dict.get('out_file', config_dict['out_file'])
            config_dict['port']     = return_dict.get('port', config_dict['port'])
            config_dict['noisy']    = return_dict.get('noisy', config_dict['noisy'])
            continue
        elif opt in ['--port']:
            try:
                port = int(arg)
            except ValueError as err:
                sys.strerr.write('Port must be numeric: %s' % str(err))
                usage()
            continue
        else:
            print 'Unknown option:' + opt
            usage()
            continue

    id_name = ''
    if len(sys.argv) > 0:
        id_name = sys.argv[0]

    logConfig.APPEND_TO_LOG = config_dict['append']
    logConfig.LOG_FILENAME  = config_dict['out_file']
    logConfig.NOISY         = config_dict['noisy']
    logConfig.PORT          = config_dict['port']

    context = zmq.Context()
    server = LogCollectorTask(context, id_name)
    server.run()

    server.join()


if __name__ == "__main__":
    main()
