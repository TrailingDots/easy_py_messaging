#!/bin/env python
"""
Directory services for 
    simple_log_messaging - Log messaging client and servers
    control_messaging    - Control messaging structure
"""

import sys
import os
import time
import zmq
import signal
import json
import pickle

import logConfig
import apiLoggerInit
import utils
import logComponents
import platform
import loggingClientTask

import pdb

NOISY = False   # Set to True for debug/trace

import atexit
def exiting(exit_msg):
    print('dirSvc: exiting:' + exit_msg)

class DirEntry(object):
    """A single directory entry."""

    def __init__(self, key, value):
        self.key = key
        self.value = value

    def to_JSON(self):
        return json.dumps(self)

# 
class DirOperations(object):
    """Various operations on the directory."""

    def __init__(self, config):
        # All the entries for this directory.
        # Key = name of entry
        # Value = a DirEntry
        self.directory = {}

        self.pickle_filename = config['memory_filename']
        self.clear = config['clear']

        # Start at this port.
        self.PORT = int(config['port'])

        # Seconds to start persistence unless reset
        self.DELTA_UPDATE_SECS = 5   

        # Is the in-core database dirty? 
        # (Does it need saving?)
        self.set_clean()

        # Time to persist dir. Seconds from epoch.
        self.is_dirty_persist = self.next_persist_time()

    def next_persist_time(self):
        self.is_dirty_persist = time.time() + \
                self.DELTA_UPDATE_SECS   # update time.

    def to_pickle(self):
        """Persist the names in a pickle file.
        This unconditionally persists the directory.
        This may be due to a persist command."""
        pickle.dump(self.directory,
                open(self.pickle_filename, 'wb'))
        self.set_clean()

    def from_pickle(self):
        """Load from pickle file"""
        self.directory = pickle.load(open(self.pickle_filename, 'rb'))
        self.set_clean()

    def persist_timeout_check(self):
        """On a time out, conditionally persist the dictionary 
        only if the directory  is dirty."""
        if not self.is_dirty:
            return
        # directory is dirty. Time to write out?
        if time.time() > self.is_dirty_persist:
            self.to_pickle()

    def to_JSON(self):
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
        return value

    def handle_meta(self, key):
        """
        Meta Queries - Queries that request info
        about directory services and not about ports.

        All meta queries get bracketed with '%'
        on both ends:
            %PERSIST% = Persist the dir immediately.
            %ALL_PORTS% = Reply with all ports in the dir.
            %MEMORY_FILENAME% = Reply with the name of the memory file
            
        """
        return None # key is not a meta query

    def get_port(self, key):
        """
        Get a port by name. If the name does not
        exist in the directory, then increment to the
        next port and return that.
        
        A name with a prefix of '-' means delete
        that name. If the name does not exist, ignore it.

        Returns: port associated with name.
            If the name did not exist, it gets
            stored with a new port.
        """
        if len(key) == 0:
            return 0    # bogus port - let user handle

        # Handle meta queries if any
        meta = self.handle_meta(key)
        if meta:
            return meta

        if key[0] == '-':
            return self.del_key(key[1:])

        port = self.directory.get(key, None)
        if port is None:
            self.PORT += 1
            port = self.PORT
            port = self.add_key_val(key, self.PORT)
        else:
            port = port.value
        if NOISY: print  'get_port(%s) = %s' % (key, port)
        return port

    def del_key(self, key):
        """Delete the given key.
        Returns value of delete key if any, else None"""
        if key in self.directory:
            value = self.directory[key]
            del self.directory[key]
            self.set_dirty()
            return value
        return None

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

    try:
        opts, args = getopt.gnu_getopt(
            sys.argv[1:], 'cpmh',
            ['port=',           # Port # to expect messages
             'memory-file=',    # Which file to persist names
             'help',            # Help blurb
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
            'port': str(logConfig.PORT),
            }
    for opt, arg in opts:
        if opt in ['-h', '--help']:
            usage()
            continue
        elif opt in ['p', '--port']:
            try:
                # Ensure a valid integer port
                int_port = int(arg)
            except Exception as err:
                sys.stdout.write(str(err) + '\n')
                usage()
            config['port'] = arg
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
    for ndx in range(shift_out):
        del sys.argv[1]

    return config


def main():
    """Main processing loop.
    Pattern is Lazy Pirate """
    config = parseOpts()
    context = zmq.Context(1)
    server = context.socket(zmq.REP)
    port = logConfig.get_directory_port()
    server.bind("tcp://*:%d" % port)
    print 'Directory Service on port %d' % port
    
    dir_ops = DirOperations(config)

    sequence = 0
    while True:
        dir_ops.persist_timeout_check()

        # Wait for a port naming request.
        # Notice this recv waits forever. This implies
        # a dirty directory will not get cleared.
        # Should a timeout change this logic?
        request = server.recv()

        port = dir_ops.get_port(request)
        if NOISY: print("I: Normal request (%s:%s)" % (request, str(port)))
        server.send(str(port))
        if sequence % 10 == 0:
            json_str = dir_ops.to_JSON()
            print json_str
        sequence += 1

    server.close()
    context.term()

if __name__ == '__main__':
    atexit.register(exiting, 'Exiting dirSvc')
    main()

