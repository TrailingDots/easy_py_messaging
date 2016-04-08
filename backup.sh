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

#set -x             # Uncomment for debugging
#PS4='$LINENO: '    # Uncomment for debugging


############# Clean up excess work files

# Get rid of any stray log files. Ignore any error messages.
/usr/bin/rm $(find . -name '*.log') 2> /dev/null

# Get rid of generated python files
/usr/bin/rm $(find . -name '*.pyc' ) 2> /dev/null
/usr/bin/rm $(find . -name '*.pyo' )  2> /dev/null

# Coverage files not needed. Ignore any "missing operand" msgs.
/usr/bin/rm -rf $(find . -name .coverage_html -type d) 2> /dev/null
/usr/bin/rm $(find . -name .coverage  -type f) 2> /dev/null

############# Backup everything left

DATE=$(date '+%y%m%d-%H%M%S')
APP=$(basename $PWD)

(cd ..; \
    tar czf $APP-$DATE.tgz $APP; \
    cd $APP)


