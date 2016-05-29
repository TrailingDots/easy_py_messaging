#!/usr/bin/env python
"""
    A logging task that sends lots of logs to the
    log controller to get a speed test in terms
    of max logs per second.
"""
import platform
import timeit
import loggingClientTask


# Allow Ctrl-C to kill this program.
import signal
signal.signal(signal.SIGTERM, signal.SIG_DFL)
signal.signal(signal.SIGHUP, signal.SIG_DFL)
signal.signal(signal.SIGINT, signal.SIG_DFL)


def main():
    """
    Create and start a simple logger with the current platform's node
    name.
    """
    client = loggingClientTask.LoggingClientClass(platform.node())
    client.start()

    # Time the sending of 100,000 messages to the remote logger.
    startTime = timeit.default_timer()

    # Send the messages
    iterations = 100000
    for ndx in range(iterations):
        client.warning('ndx:%d' % ndx)

    elapsed = timeit.default_timer() - startTime
    client.info('%d logs, elapsed time: %f' % (iterations, elapsed))
    client.info('Timed at %d messages per second' %
            int(iterations/elapsed))
    print '%d logs, elapsed time: %f' % (iterations, elapsed)
    print '%d messages per second' % int(iterations/elapsed)


if __name__ == '__main__':
    main()

