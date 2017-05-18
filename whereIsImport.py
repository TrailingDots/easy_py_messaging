#!/bin/env
#
# Use the sys.path to determine all instances
# of an import.
#

import sys
import os

def whereIsImport(filename):
    for dir in sys.path:
        if os.path.isfile(dir + '/' + filename):
            print dir + '/' + filename
        else:
            print dir

if __name__ == "__main__":
    whereIsImport(sys.argv[1])



