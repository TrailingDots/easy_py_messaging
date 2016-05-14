#!/bin/bash

set -x
PS4='$LINENO: '

TEST_COUNT=0
ERROR_COUNT=0
# function to echo command and then execute it in the background.
# Return the pid of the backgrounded process.
CMD_BG () {
    (( TEST_COUNT = TEST_COUNT + 1 ))
    # BASH_LINENO is an array. Use the top of the stack == 0
    echo
    echo "CMD_BG PID=${BASH_LINENO[0]}: $($*)&"
    $1
    return_code=$?
    if [ $return_code -eq 0 ]
    then
        echo "+++ERROR: Expected != 0 return code, got $return_code"
        (( ERROR_COUNT = ERROR_COUNT + 1 ))
    fi
    return $PID
}

#PID=$(CMD_BG "coverage run --branch --parallel-mode ./dirSvc.py ")
echo coverage run --branch --parallel-mode ./dirSvc.py \&
coverage run --branch --parallel-mode ./dirSvc.py &
apid=$!
echo apid=$apid
echo sleeping... $apid
#sleep 10
#kill $apid

