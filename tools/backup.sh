#!/usr/bin/bash
#
# Script to create a compressed tar backup of the
# files in an application directory.
#
# The backup name uses the top level directory
# as the application name.
#
# A backup filename appears as:
#   myApp-160226-091730.tgz
# where:
#   myApp   = application name
#   160226  = 2016 Feb 26 
#             Notice this sorts "ls myApp*" backups alphabetically.
#   091730  = 9:16 Hours 30 seconds. This is in 24 hour notation.
#

############# Clean up excess work files

# Get rid of any stray log files.
find . -name '*.log' | xargs /usr/bin/rm

# Get rid of generated python files
find . -name '*.pyc' | xargs /usr/bin/rm

# Coverage files not needed. Ignore any "missing operand" msgs.
find . -name .coverage_html | xargs /usr/bin/rm -rf
find . -name .coverage      | xargs /usr/bin/rm -rf

############# Backup everything left

DATE=$(date '+%y%m%d-%H%M%S')
APP=$(basename $PWD)

(cd ..; \
    tar czf $APP-$DATE.tgz $APP; \
    cd $APP)


