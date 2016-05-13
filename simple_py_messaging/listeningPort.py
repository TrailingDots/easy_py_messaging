#!/bin/env python

# Documentation: Please see the usage() function!

import sys
import subprocess
import platform

# Default ZeroMQ port
PORT = 5570


def is_listening(port):
    """
    More proper boolean operator for easier
    reading.
    return 1    # Indicate a found listener
    return 0    # Indicates nobody listening
    """
    return not listening(port)


def listening(port,
        shortened=False,
        pid_only=False,
        proc_only=False):
    """
    The return code seems to be reversed, but
    it exists for the common command line version:
    return 0    # Indicate a found listener
    return 1    # Indicates nobody listening
    """
    if platform.system() != 'Linux':
        sys.stderr.write('listeningPort available only under Linux!\n')
        sys.exit(127)

    proc = subprocess.Popen('/usr/sbin/fuser %s/tcp' %
            str(port),
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
    line = proc.stdout.readline()
    items = line.split()
    if len(items) == 0:
        sys.stdout.write('Port %s : Nobody listening\n' % str(port))
        return 1
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
    status = 0
    for line in out:
        items = line.split()
        if items[0] != pid:     # Ignore all but requested pid
            continue
        # Branch on requested output
        if shortened:
            sys.stdout.write('%s %s %s\n' % (str(port), pid, ' '.join(items[5:])))
        elif pid_only:
            sys.stdout.write('%s\n' % pid)
        elif proc_only:
            sys.stdout.write('%s\n' % ' '.join(items[4:]))
        else:
            sys.stdout.write('Port %s : listening thru pid %s named %s\n' %
                    (str(port), pid, ' '.join(items[5:])))
        status += 1    # Indicate a found listener

    return status


def usage():
    """Write a usage statment and exit."""

    sys.stderr.write("""
    List the processes that are listening to a port.
    Defaults to ZeroMQ port of 5570.

    Use by:
      listeningPort [--help] [--short | --pid | --proc] <port> [<port> ...]
    e.g.:
      listeningPort 5570             # The ZeroMQ default port
      listeningPort 5570 5571 5572   # Multiple ports may be checked
      listeningPort --short 5570

    For the case of a free port, output similar to:
      Port 5571 : Nobody listening

    --help = this message

    Only one of the following can be supplied:
    --short = Output consists of only three space separated fields:
        <port> <pid of listener> <process name of listener>
    --pid  = Output consists only of a pid
    --proc = Output consists only of process names

    Return codes:
      0 = Someone is listening. stdout has details.
      !0 = Nobody listening to <port> or invalid cmd line args.
    \n
    NOTICE: This routine does NOT work on OSX!
    Replace this with:
        lsof -i<port> | awk '{ print $2; }' | head -2
        PID
        18101
    This prints only the pid of the process using this port.
    Now use "ps" to find the process:
        ps ax | grep 18191 | grep -v grep
        10191 s001  S+    0:00.00 /usr/bin/python /usr/local/bin/logCollector
    """)
    sys.exit(1)


def main():
    """
    Process run-time args.
    Based on the args, run the program.
    Return the number of listeners for all
    provided ports. 100 == error for port #
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
            for aport in remainder:
                port_int = int(aport)
        else:
            remainder = []
            remainder.append(PORT)
    except ValueError as err:
        sys.stderr.write('port number must be all numeric:%s\n' %
                str(remainder))
        return 100
    ret_code = 0
    for aport in remainder:
        ret_code += not listening(aport, shortened, pid_only, proc_only)

    return ret_code

if __name__ == '__main__':
    sys.exit(main())

