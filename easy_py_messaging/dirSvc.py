#!/bin/env python
"""
Server:
    Directory services for
        easy_py_messaging    - easy messaging client and servers
        control_messaging    - Control messaging structure
"""

import sys
import os
import time
import zmq
import json
import pickle
import atexit

import logConfig
import platform
import loggingClientTask

NOISY = False   # Set to True for debug/trace


def exiting(exit_msg):
    print('dirSvc: exiting:' + exit_msg)


class DirEntry(object):
    """A single directory entry."""

    def __init__(self, key, value):
        self.key = key
        self.value = value

    def to_JSON(self):
        return json.dumps(self)


class DirOperations(object):
    """Various operations on the directory service."""
    def __init__(self, config):
        # All the entries for this directory.
        # Key = name of entry
        # Value = a DirEntry
        self.directory = {}

        self.pickle_filename = config['memory_filename']
        self.clear = config['clear']

        # receive requests on this port.
        self.dir_port = int(config['port'])

        # Seconds to start persistence unless reset
        self.DELTA_UPDATE_SECS = 5

        # Is the in-core database dirty?
        # (Does it need saving?)
        self.set_clean()

        self.is_dirty = False   

        # Time to persist dir. Seconds from epoch.
        self.is_dirty_persist = self.next_persist_time()

        # logCollector connection
        self.client = loggingClientTask.LoggingClientClass(platform.node())
        self.client.start()
        log_entry = 'Starting=DirectoryService,port=%d,pid=%d,memory=%s' % \
            (self.dir_port, os.getpid(), config['memory_filename'])
        self.client.info(log_entry)
        print log_entry

        # Unless clear is set, logs from memory_filename.
        self.from_pickle()

    def next_persist_time(self):
        self.is_dirty_persist = time.time() + \
                self.DELTA_UPDATE_SECS   # update time.

    def to_pickle(self):
        """Persist the names in a pickle file.
        This unconditionally persists the directory.
        This may be due to a persist command."""
        try:
            pickle.dump(self.directory,
                    open(self.pickle_filename, 'wb'))
        except Exception as err:
            err_str = 'to_pickle=cannot_open,file=%s,err=%s' % \
                    (self.pickle_filename, str(err))
            self.client.critical(err_str)
            sys.stderr.write(err_str + '\n')
            sys.exit(1)

        self.set_clean()
        self.client.debug('pickled_to=' + self.pickle_filename)
        return True

    def from_pickle(self):
        """Load from pickle file"""
        if os.path.isfile(self.pickle_filename):
            try:
                self.directory = pickle.load(open(self.pickle_filename, 'rb'))
            except EOFError:
                pass    # Ignore empty file
        else:
            self.client.critical('from_pickle=%s,status=not_found' %
                    self.pickle_filename)
            sys.stderr.write('FATAL ERROR: Cannot process memory_file: "%s"\n' % 
                    self.pickle_filename)
            sys.exit(1)

        self.set_clean()
        self.client.debug('from_pickle=%s,status=OK' %
                self.pickle_filename)

    def persist_timeout_check(self):
        """On a time out, conditionally persist the dictionary
        only if the directory  is dirty."""
        if not self.is_dirty:
            return
        # directory is dirty. Time to write out?
        if time.time() > self.is_dirty_persist:
            self.to_pickle()

    def to_JSON(self):
        self.client.debug('to_json=True')
        return json.dumps(self.directory, default=lambda x: x.__dict__)

    def add_key_val(self, key, value):
        """
        add key and value to Directory.

        What is the purpose of storing the entire
        DirEntry object into the directory?
        Because later additional data may become
        associated with this object and this makes
        extensions much easier.  (We'll see...)
        """
        if NOISY: print 'add_key_val(%s, %s)' % (str(key), str(value))
        if key not in self.directory:
            self.set_dirty()
        dir_entry = DirEntry(key, value)
        self.directory[key] = dir_entry
        self.client.info('add_key_val=%s,value=%s' % (key, value))
        return value

    def handle_meta(self, key):
        """
        Meta Queries - Queries that request info
        about directory services and not about ports.

        A delete request is the name prefixed by '~'.

        All meta queries get prefixed with '@'
        on both ends:
            @PERSIST = Persist the dir immediately.
            @DIR = Reply with all ports in the dir.
            @CLEAR = Clears the directory
            @CLEAR_DIRECTORY = Clears the directory
            @MEMORY_FILENAME = Reply with the name of the memory file
            @EXIT = Exit this program. Used for code coverage.

        Returns: None if not a meta, else non-None.
        """
        if key == '@DIR':
            # Return entire directory in JSON
            data = self.to_JSON()
            self.client.info('@DIR=%s' % str(data))
            return data
        if key == '@PERSIST':
            self.to_pickle()
            self.client.info('@PERSIST=True')
            return 'True'
        if key == '@CLEAR' or key == '@CLEAR_DIRECTORY':
            self.directory = {}
            self.client.info('@CLEAR_DIRECTORY=True')
            return True
        if key == '@MEMORY_FILENAME':
            self.client.info('@MEMORY_FILENAME=%s' % self.pickle_filename)
            return self.pickle_filename
        if key == '@EXIT':
            return '@EXIT'

        # All valid meta commands compared. If the key tags as meta by a
        # leading '@', but is not in the above list, flag as unknown meta
        # command.
        if key[0] == '@':
            self.client.error('name=%s,status=unknown_meta_command' % key)
            return '@UNKNOWN_META_COMMAND'
        return None     # No meta query found.

    def get_port(self, key):
        """
        Get a port by name. If the name does not
        exist in the directory, then increment to the
        next port and return that.

        A name with a prefix of '~' means delete
        that name. If the name does not exist, ignore it.

        Returns: port associated with name.
        """
        if len(key) == 0:
            return 0    # bogus port - let user handle

        # Handle delete request, if requested.
        if key[0] == '~':
            self.del_key(key)
            return True

        # Handle meta query if requested.
        if key[0] == '@':
            return self.handle_meta(key)

        port = self.directory.get(key, None)
        if port is None:
            port = logConfig.incDirNamePort()
            port = self.add_key_val(key, port)
        else:
            port = port.value
        self.client.info('get_port_key=%s,port=%s' % (key, port))
        if NOISY: print  'get_port(%s) = %s' % (key, port)
        return port

    def del_key(self, key):
        """
        Delete the given key.
        Returns True if key in directory, else None

        A delete request has a leading '~' char.
        """
        key = key[1:]
        if key in self.directory:
            del self.directory[key]
            self.set_dirty()
            self.client.info('del_key=%s,status=deleted' % key)
            return 'DELETED'
        self.client.info('del_key=%s,status=not_found' % key)
        return 'not_found'

    def set_dirty(self):
        """Set a time for to automatically
        persist the DB."""
        self.is_dirty = True
        self.is_dirty_persist = self.next_persist_time()

    def set_clean(self):
        """Set clean. Then set a time
        to automatically persist the DB."""
        self.is_dirty = True
        self.is_dirty_persist = self.next_persist_time()


def usage():
    """Print the usage blurb and exit."""
    print 'dirSvc [--help] [--port] [--memory-file=memory_filename]'
    print '\t\t[--clear]'
    print '\t--help         = This blurb'
    print '\t--port=aport   = Port to expect queries.'
    print '\t--memory-file=memory_filename   = File to persist names'
    print '\t\tDefault: ./dirSvc.data'
    print '\t--clear        = Clear memory-file upon starting.'
    print '\t\tDefault: False, do not clear but load memory-file'
    print ''
    sys.exit(1)


def parseOpts():
    import getopt
    global NOISY

    try:
        opts, args = getopt.gnu_getopt(
            sys.argv[1:], 'cpmh',
            ['port=',           # Port # to expect messages
             'memory-file=',    # Which file to persist names
             'help',            # Help blurb
             'noisy',           # Turn noise on
             'clear'            # If set, clean memory-file at start
            ]
        )
    except getopt.GetoptError as err:
        print err
        usage()

    # Number leading args to shift out
    shift_out = 0
    config = {
            'clear': False,
            'memory_filename': './dirSvc.data',
            'port': str(logConfig.DIR_PORT),
            }
    for opt, arg in opts:
        if opt in ['-h', '--help']:
            usage()
        elif opt in ['--noisy']:
            NOISY = True
            continue
        elif opt in ['p', '--port']:
            try:
                # Ensure a valid integer port
                _ = int(arg)
            except Exception as err:
                sys.stdout.write(str(err) + '\n')
                usage()
            config['port'] = arg
            logConfig.DIR_PORT = arg
            shift_out += 1
            continue
        elif opt in ['m', '--memory-file']:
            shift_out += 1
            config['memory_filename'] = arg
            continue
        elif opt in ['c', '--clear']:
            shift_out += 1
            config['clear'] = True
            continue
    # pass the remaining args to the rest of the program.
    for _ in range(shift_out):
        del sys.argv[1]

    return config


def main():
    """
    Main processing loop.
    The ZeroMQ pattern is The Lazy Pirate
    """
    config = parseOpts()
    context = zmq.Context(1)
    server = context.socket(zmq.REP)
    port = logConfig.get_directory_port()
    try:
        server.bind("tcp://*:%s" % str(port))
    except zmq.ZMQError as err:
        sys.stderr.write('ZMQError: %s\n' % err)
        sys.stderr.write('Please kill other instances of this program.\n')
        sys.stderr.write('Or: another program may be using port %s\n' %
            str(port))
        sys.exit(1)

    sys.stdout.write('dirSvc started. pid %s port %s\n' %
        (str(os.getpid()), str(port)))

    dir_ops = DirOperations(config)

    sequence = 0
    while True:
        dir_ops.persist_timeout_check()

        # Wait for a port naming request.
        # Notice this recv waits forever. This implies
        # a dirty directory will not get cleared.
        # Should a timeout change this logic?
        if NOISY: print("I: Normal receive port: %s)" % port)
        request = server.recv()

        port = dir_ops.get_port(request)
        if NOISY: print("I: Normal request (%s:%s)" % (request, str(port)))
        server.send(str(port))
        if str(port) == '@EXIT':
            break
        if sequence % 10 == 0:
            json_str = dir_ops.to_JSON()
            print json_str
        sequence += 1

    # Shut down ZeroMQ sockets in an orderly manner.
    server.close()
    context.term()

if __name__ == '__main__':
    atexit.register(exiting, 'Exiting dirSvc')
    main()

