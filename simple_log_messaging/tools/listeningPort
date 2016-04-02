#!/bin/env python

# Documentation: Please see the usage() function!

import sys
import subprocess

# Default ZeroMQ port
PORT = 5570


def listening(port, shortened, pid_only, proc_only):
    proc = subprocess.Popen('/usr/sbin/fuser %d/tcp' % port,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
    line = proc.stdout.readline()
    items = line.split()
    if len(items) == 0:
        print 'Port %d : Nobody listening' % port
        return 0
    pid = items[-1]
    proc.wait()

    # "pid" now has the PID of the process listening to the port.
    # Map that to a process name.
    # procName = subprocess.Popen('ps x %s' % pid, shell=True,
    out, err = subprocess.Popen('/usr/bin/ps x | /usr/bin/grep %s' % pid,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT).communicate()
    if err and len(err):
        sys.stderr.write(err + '\n')
    out = out.splitlines()
    for line in out:
        items = line.split()
        if items[0] != pid:
            continue
        if shortened:
            sys.stdout.write('%d %s %s\n' % (port, pid, items[-1]))
        elif pid_only:
            sys.stdout.write('%s\n' % pid)
        elif proc_only:
            sys.stdout.write('%s\n' % items[-1])
        else:
            sys.stdout.write('Port %d : listening thru pid %s named %s\n' %
                    (port, pid, items[-1]))
        return 0    # Indicate a found listener

    # Nobody listening. fuser should have found this, but be careful.
    return 1


def usage():
    """Write a usage statment and exit."""

    sys.stderr.write("""
    Give a port that defaults to ZeroMQ of 5570,
    list the processes that are listening to that port.

    Use by:
      listening [--help] [--short] <port>
    e.g.:
      listening 5570      # The ZeroMQ default port
    --help = this message
    --short = Output consists of only three space separated fields:
        <port> <pid of listener> <process name of listener>

    Return codes:
      0 = Someone is listening. stdout has details.
      !0 = Nobody listening to <port> or invalid cmd line args.
    \n""")
    sys.exit(1)


def main():
    """
    Process run-time args.
    Based on the args, run the program.
    """

    import getopt

    try:
        options, remainder = getopt.getopt(
            sys.argv[1:], '',
            ['help',     # Print usage msg, exit
             'short',    # Output is shortened
             'pid',      # Output only pid of listenig process
             'proc',     # Output only process name of listening port
            ]
        )
    except getopt.GetoptError as err:
        sys.stderr.write(str(err) + '\n')
        usage()

    shortened = False
    pid_only = False
    proc_only = False
    for opt, arg in options:
        if opt in ['--help']:
            usage()
        elif opt in ['--short']:
            shortened = True
        elif opt in ['--pid']:
            pid_only = True
        elif opt in ['--proc']:
            proc_only = True
        else:
            # Should never happen. getopt() will catch this.
            sys.stderr.write('Unhandled option:"%s"\n' % opt)
            usage()

    try:
        if len(remainder):
            port_int = int(remainder[0])
        else:
            port_int = PORT
    except ValueError as err:
        sys.stderr.write('port number must be all numeric:%s\n' %
                str(remainder))
        return 2
    ret_code = listening(port_int, shortened, pid_only, proc_only)
    return ret_code

if __name__ == '__main__':
    sys.exit(main())

