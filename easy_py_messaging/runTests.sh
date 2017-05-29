#!/bin/bash

#
# The following prerequesites must exist for proper
# operations of this script:
#   pyflakes
#   coverage
#   lizard      # For cyclomatic complexity.
#               # https://github.com/terryyin/lizard
#
# Install the above python packages in the normal way.
#
#
# Recommended way to operate:
#   script                  # Start collecting all output
#   ./runTests.sh ; exit    # run this script then exit script shell
#   vim typescript          # Default output of "script" goes into typescript
#
# Errors are expected! The get noted as CMD_FAIL commands.
# However, there should be no tracebacks.
#
# An unfortunate reason that this script runs so many test rests in the
# inability of coverage to handle subprocesses properly!
# Much time was spent attempting to encapsulate the repetitious
# nature of these test into python scripts. 
#
# The fantastic coverage utility does not accurately catch all
# coverage. In the output reports I can see some code noted as
# not covered when in fact I do know for a fact the code
# *was* covered. Thus, the coverage reports a lower value
# that the actual coverge.
#
# The output uses the following bash functions to provide
# feedback on progress:
#   ECHO "..."  - The string simply gets echoed. Just a comment.
#   CMD "..."   - The command gets run. The exit status does not matter.
#   CMD_PASS "..." - A 0 status code indicates a successful execution.
#   CMD_FAIL "..." - A non-zero status code indicates a successful execution.
# On all these the line number provides a convenient link to where
# the commands get executed.
#
# Notice that programs started in background do not get handled with
# CMD-style tracking. This is OK.
# All background processes get killed with an "@EXIT" from the processes
# that send messages.
#
# TODO:
#   Provide stricter checking of these commands!
#   Just because a zero status indicates success does NOT mean
#   the output was correct. LOTS more validation work for this
#   to become really solid.
#
#   When a test fails, place the line number on a fail stack
#   so it may be more easily found.
#

# Uncomment next two lines for debugging and tracing of this script.
#set -x
#PS4='$LINENO: '

# Start a timer for this entire script. The end produces a duration.
SECONDS=0

# Future versions may use python3?
alias python=/usr/bin/python2.7
export PYTHON=/usr/bin/python2.7

# Function to echo a command and then execute it.
# Do NOT try to start backgrounded commands with this function.
CMD () {
    # BASH_LINENO is an array. Use the top of the stack == 0
    echo
    echo "CMD ${BASH_LINENO[0]}: $*"
    $1
    ret_code=$?
    echo return code $ret_code
    return $ret_code
}

trap "echo +++ signal received +++; exit" SIGHUP SIGINT SIGTERM

# Total number of tested commands
TEST_COUNT=0

# Total count of errors
ERROR_COUNT=0
EXPECTED_PASS_BUT_FAIL=0
EXPECTED_FAIL_BUT_PASS=0

#
# The site-packages to omit in coverage runs
SITE=/usr/lib/python2.7/site-packages/six.py

# function to echo command and then execute it.
# Expect the command to pass with return code 0
declare -a expect_pass_but_fail=()
CMD_PASS () {
    (( TEST_COUNT = TEST_COUNT + 1 ))
    # BASH_LINENO is an array. Use the top of the stack == 0
    echo
    echo "CMD_PASS ${BASH_LINENO[0]}: $*"
    $1
    return_code=$?
    if [ $return_code -ne 0 ]
    then
        echo "+++ERROR: Expected 0 return code, got $return_code"
        (( ERROR_COUNT = ERROR_COUNT + 1 ))
        (( EXPECTED_PASS_BUT_FAIL = EXPECTED_PASS_BUT_FAIL + 1 ))
        expect_pass_but_fail+=" ${BASH_LINENO[0]}"
    fi
}


# Expect a specific return code, i.e., RC
# function to echo command and then execute it.
# CMD_RC expected_RC cmd
# Expect the command to pass with return code
function CMD_RC () {
    (( TEST_COUNT = TEST_COUNT + 1 ))
    echo
    # BASH_LINENO is an array. Use the top of the stack == 0
    echo "CMD_RC ${BASH_LINENO[0]}: $*"
    EXPECTED=$1
    shift
    $1
    RETURN_CODE=$?
    if [ $RETURN_CODE -ne $EXPECTED ]
    then
        echo "+++ERROR: Expected $EXPECTED return code, got $RETURN_CODE"
        (( ERROR_COUNT = ERROR_COUNT + 1 ))
        (( EXPECTED_PASS_BUT_FAIL = EXPECTED_PASS_BUT_FAIL + 1 ))
        expect_pass_but_fail+=" ${BASH_LINENO[0]}"
    fi
}

# function to echo command and then execute it.
# Expect the command to fail with return code != 0
declare -a expect_fail_but_pass=()
CMD_FAIL () {
    (( TEST_COUNT = TEST_COUNT + 1 ))
    # BASH_LINENO is an array. Use the top of the stack == 0
    echo
    echo "CMD_FAIL ${BASH_LINENO[0]}: $*"
    $1
    return_code=$?
    if [ $return_code -eq 0 ]
    then
        echo "+++ERROR: Expected != 0 return code, got $return_code"
        (( ERROR_COUNT = ERROR_COUNT + 1 ))
        (( EXPECTED_FAIL_BUT_PASS = EXPECTED_FAIL_BUT_PASS + 1 ))
        expect_fail_but_pass+=" ${BASH_LINENO[0]}"
    fi
}

# function to simply echo with a line number
ECHO () {
    # BASH_LINENO is an array. Use the top of the stack == 0
    echo "ECHO ${BASH_LINENO[0]}: $*"
}

LISTENING=\"$(/usr/bin/env listening)\"
if [ -z $LISTENING ] ; then
    echo Cannot find the listening utility.
    echo "listening" must be installed as a prerequesite.
    echo clone https://github.com/TrailingDots/ListeningPort
    echo and copy listeningPort.py to somewhere in your $PATH.
    echo  A common location is in $HOME/bin
    exit 1
fi
ECHO "LISTENING found at $(which listening)"

# Run various python metric utilities
# Comment out any utilities not wanted
CMD "pyflakes *.py "
CMD "pep8 *.py "
#CMD "pylint *.py "        # pylint gets "Inconsistent hierarchy"
CMD "lizard -l python . "
# End of utilities that examine the source code.

# Environmental varable for tracking subprocesses
# Ref: http://coverage.readthedocs.org/en/coverage-4.0.3/subprocess.html
export COVERAGE_PROCESS_START=$PWD/.coveragerc
ECHO " export COVERAGE_PROCESS_START=$COVERAGE_PROCESS_START"

export CPS=$COVERAGE_PROCESS_START
ECHO "CPS=$CPS"

export PYTHONPATH=$PYTHONPATH:$PWD
ECHO "PYTHONPATH=$PYTHONPATH"

../wc.sh     # How big is this getting?

export BASE_DIR=$PWD
ECHO "BASE_DIR=$BASE_DIR"

export LIB_DIR=$BASE_DIR
ECHO "LIB_DIR=$LIB_DIR"

export TOOLS_DIR=$BASE_DIR
ECHO "TOOLS_DIR=$TOOLS_DIR"

export TEST_DIR=$BASE_DIR/test
ECHO "TEST_DIR=$TEST_DIR"

export DATA_DIR=$BASE_DIR/data
ECHO "DATA_DIR=$DATA_DIR"

export GEN_DATA=$TEST_DIR/genData.py
ECHO "GEN_DATA=$GEN_DATA"

ECHO Remove all logs.log
ECHO "rm $(find . -name logs.log)"

ECHO Remove all .coverage.*
/usr/bin/rm $(find . -name '.coverage.*' -type f)

ECHO Remove .coverage_html/*
CMD "rm -rf .coverage_html"

ECHO "Before starting, make sure the logCollector.py exists."
CMD "listening --kill $(seq -s ' ' 5570 5580)"

#
export COVERAGE=1 
CMD "coverage erase "

# Generate a "standard" log of data frequently used in testing.
export DATA_LOG=$DATA_DIR/data.data
CMD "$GEN_DATA >$DATA_LOG"
$GEN_DATA >$DATA_LOG    # CMD does not handle redirection properly.


ECHO "================= Run client/server create_test ============"
ECHO "First - some errors with server_create_test.py"
CMD_FAIL "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/server_create_test.py --help"
CMD_FAIL "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/server_create_test.py --port=XYZ"
CMD_FAIL "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/server_create_test.py --noisy --port=XYZ"
CMD_FAIL "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/server_create_test.py --BogusOption"

ECHO ""
ECHO "Start server_create_test.py"
ECHO "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/server_create_test.py "
coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/server_create_test.py &
ECHO "server_create_test.py should have port 5590, the default port for this app"
sleep 1
CMD "listening 5590"

ECHO "Send some messages to server_create_test.py"
ECHO "Using defaults from command line"
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/client_create_test.py This is a test"
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/client_create_test.py This is a test"
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/client_create_test.py --port=5590 This is another test"
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/client_create_test.py --port=5590 --node=localhost This is another test"
# Is the following node 127.0.0.1 important?
#CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/client_create_test.py --port=5590 --node=127.0.0.1 This is a localhost node"
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/client_create_test.py --port=5590 This is a localhost node"
ECHO "The timing - slow..."
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/client_create_test.py --port=5590 --timing This is a localhost node"

ECHO " Some failures - non-numeric port"
CMD_FAIL "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/client_create_test.py --port=XYZ This is another test"
ECHO " Some failures - invalid option"
CMD_FAIL "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/client_create_test.py --foobar=XYZ This is another test"
CMD_FAIL "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/client_create_test.py --help"

# Stop that server_create_test.py
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/client_create_test.py Get out of this program: @EXIT"



ECHO "Need to get a timed alarm in case the collector does not start."
ECHO "echo ====starting logCollector.py===="
coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logCollector.py &
COL_PID=$!
ECHO "Allow the logCollector time to start"
CMD_PASS "sleep 2"
ps x | grep logCollector.py

ECHO "The logCollector.py must be running in port 5570"
CMD_RC 1 "listening --short 5570"

ECHO Dos not actually kill, just sends a signal.
ECHO "Test the operations of 'kill -USR[12] <pid>"
CMD_PASS "kill -USR1 $COL_PID"
CMD_PASS "kill -USR2 $COL_PID"
CMD_PASS "kill -USR2 $COL_PID"
CMD_PASS "kill -USR2 $COL_PID"
CMD_PASS "kill -USR2 $COL_PID"
CMD_PASS "kill -USR2 $COL_PID"
CMD_PASS "kill -USR2 $COL_PID"

ECHO "Run a few simple logs to the logCollector.py"
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/loggingClientTask.py "

# Expect return code of 1 because only port 5570 should be running.
CMD_RC 1 "listening 5570"

ECHO "kill logCollector.py and restart with output to /dev/null for Speed test"
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logCmd.py @EXIT "
ECHO " coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logCollector.py --log-file=/dev/null  " 
# Need to start background tasks easily and manageable.
$LIB_DIR/logCollector.py --log-file=/dev/null & 

CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/loggingSpeedTest.py "

ECHO "Stop logCollector.py with /dev/null output, open again with echo"
coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logCmd.py @EXIT
CMD "/usr/bin/sleep 2"

ECHO "logCollector.py still going... Should have been killed."
CMD_RC 1 "listening --short $(seq -s ' '  5570 5590)"
CMD "ps aux | grep logCollector.py"

coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logCollector.py &

CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/loggingLoopApp.py 5   "

ECHO "Passing logCmd.py"
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logCmd.py Testing a new log config option." 

ECHO Misc logCmd.py testing
CMD_FAIL "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logCmd.py --help"
CMD_FAIL "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logCmd.py --xxx stuff"
CMD_FAIL "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logCmd.py --port=XYZ stuff"
CMD_FAIL "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logCmd.py --level=XYZ"
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logCmd.py --level=DEBUG Should be at debug level"

CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $GEN_DATA "
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $GEN_DATA --happy   "
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $GEN_DATA --missing "
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $GEN_DATA --mixed   "
CMD_FAIL "coverage run --omit $SITE --branch --parallel-mode $GEN_DATA --help    "
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $GEN_DATA --config=datedFilter "
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $GEN_DATA --config=csvFilter "
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $GEN_DATA --config=baseFilter "
CMD_FAIL "coverage run --omit $SITE --branch --parallel-mode $GEN_DATA --config=bogusFilter "
ECHO An invalid filter
CMD_FAIL "coverage run --omit $SITE --branch --parallel-mode $GEN_DATA ----config=bogusFilter "    # An invalid filter

ECHO Coverage for apiLoggerInit.py
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/apiLoggerInit.py "

CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/apiLoggerInit.py "

ECHO "logCollector.py still going...\?"
CMD_RC 1 "listening --short 5570"
ECHO Multiple runs passing various flags both valid and bogus.
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logFilterApp.py --in-file=$DATA_LOG --JSON "
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logFilterApp.py --in-file=$DATA_LOG --JSON --level=ERROR "
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logFilterApp.py --in-file=$DATA_LOG --CSV "
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logFilterApp.py --in-file=$DATA_LOG --CSV --level=ERROR "
CMD_FAIL "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logFilterApp.py --Xin-file=$DATA_LOG --CSV --level=ERROR "
CMD_FAIL "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logFilterApp.py --help "
ECHO Expect ERRORs
CMD_FAIL "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logFilterApp.py --in-file=bogus_file --CSV --level=ERROR "
ECHO Expect ERRORs - bogus log level
CMD_FAIL "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logFilterApp.py --in-file=bogus_file --CSV --level=Bogus "
ECHO Expect ERRORs
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logFilterApp.py --in-file=/dev/null --CSV --level=ERROR "
ECHO Expect ERRORs
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logFilterApp.py --in-file=/dev/null --JSON --level=ERROR "
ECHO Expect ERRORS 
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logFilterApp.py --config=$DATA_DIR/csv.conf --in-file=/dev/null --JSON --level=ERROR "
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logFilterApp.py --config=$DATA_DIR/happy.conf "
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logFilterApp.py --config=$DATA_DIR/mixed.conf "

ECHO Expect ERRORS 
CMD_FAIL "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logFilterApp.py --config=$DATA_DIR/bad.conf "
ECHO Expect ERRORS 
CMD_FAIL "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logFilterApp.py --config=$DATA_DIR/bad2.conf "
ECHO Expect ERRORS 
CMD_FAIL "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logFilterApp.py --config=$DATA_DIR/bad3.conf "
ECHO Expect ERRORS 
CMD_FAIL "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logFilterApp.py --config=$DATA_DIR/no_start.conf "
ECHO Expect ERRORS 
CMD_FAIL "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logFilterApp.py --config=$DATA_DIR/no_end.conf "
ECHO Expect ERRORS 
CMD_FAIL "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logFilterApp.py --config=$DATA_DIR/no_end1.conf "
ECHO Expect ERRORS 
CMD_FAIL "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logFilterApp.py --config=$DATA_DIR/no_start1.conf "
ECHO Expect ERRORS 
CMD_FAIL "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logFilterApp.py --config=$DATA_DIR/bad_start.conf "
ECHO Expect ERRORS 
CMD_FAIL "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logFilterApp.py --config=$DATA_DIR/bad_end.conf "
ECHO Expect ERRORS 
CMD_FAIL "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logFilterApp.py --config=$DATA_DIR/end_before_start.conf "

ECHO "No infile. Reads from stdin"
cat happy.data | coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logFilterApp.py 

CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logFilterApp.py --in-file=/dev/null --in-file=$DATA_LOG --JSON "
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logFilterApp.py --start=1970-01-01T00:00:00.000 --in-file=/dev/null --in-file=$DATA_LOG --JSON "
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logFilterApp.py --start=1970-01-01T00:00:00.000 --end=2020-01-01T00:00:00.000 --in-file=/dev/null --in-file=$DATA_LOG --JSON "
ECHO 
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logFilterApp.py --end=2020-01-01T00:00:00.000 --in-file=/dev/null --in-file=$DATA_LOG --JSON "
ECHO Syntax error on end date
CMD_FAIL "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logFilterApp.py --end=2017-01-01:00:00:00.000 --in-file=/dev/null --in-file=$DATA_LOG --JSON "
ECHO Permission denied on output file.
CMD_FAIL "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logFilterApp.py --in-file=/ --out-file=$DATA_LOG --JSON "
ECHO Permission denied on input file.
CMD_FAIL "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logFilterApp.py --in-file=/dev/null --in-file=/var/log/messages --JSON "

CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logFilterApp.py --in-file=/dev/null --in-file=$DATA_LOG --CSV "
ECHO Permission denied on output file.
CMD_FAIL "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logFilterApp.py --in-file=/ --out-file=$DATA_LOG --CSV "
ECHO Permission denied on input file.
CMD_FAIL "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logFilterApp.py --in-file=/dev/null --in-file=/var/log/messages --CSV "

ECHO "Filter on dates as well."
ECHO "These test depend on the dates as set in ./test/getData.py and the $DATA_LOG file"
ECHO "start only"
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logFilterApp.py --in-file=$DATA_LOG --JSON --start=2016-03-14T08:00:00.000 "
ECHO Syntax Error for start only
CMD_FAIL "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logFilterApp.py --in-file=$DATA_LOG --JSON --start=2016-03-14:08:00:00.000 "
ECHO start and end dates
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logFilterApp.py --in-file=$DATA_LOG --JSON --start=2016-03-14T08:00:00.000 end=2016-03-14T08:05:15.876 "

ECHO "Work with dirSvc.py - Directory Service"
CMD_FAIL "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/dirSvc.py --help"
ECHO Pass invalid run time option
CMD_FAIL "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/dirSvc.py --FooBar"
ECHO Pass invalid port number
CMD_FAIL "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/dirSvc.py --clear --port=XYZ"
CMD_FAIL "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/dirSvc.py --noisy --memory-file=/ --port=1234"

# Expect port 5570 is in use
CMD_RC 1 "listening --short 5570"

# Start the directory server in the background.
ECHO coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/dirSvc.py 
coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/dirSvc.py --noisy &

# Start a logCollector.py in the background as well
coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logCollector.py --noisy &

CMD_RC 1 "listening --short 5570"

echo " If dirClient.py passes, it means it could send the params to dirSvc.py."
echo " Passing does not mean the parameter is valid!"
CMD_FAIL "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/dirClient.py --help"
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/dirClient.py --noisy foobar"
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/dirClient.py --noisy abc def ghi jkl"
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/dirClient.py --noisy @DIR"
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/dirClient.py --noisy @CLEAR"
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/dirClient.py --noisy @CLEAR_DIRECTORY"
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/dirClient.py --noisy @PERSIST"
# Ma8 18, 2017 - The tests below hangs! Why??? FIXME DEBUG TODO
# CMD_FAIL "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/dirClient.py --node=abc @PERSIST"
# CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/dirClient.py --memory-file=/ "
# CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/dirClient.py --clear "
# The command below hangs! Why???
# CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/dirClient.py --noisy @MEMORY_FILENAME"
# The cmd below hangs! WHY?
# CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/dirClient.py --noisy @DOES_NOT_EXIST"
# CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/dirClient.py --noisy --port=5599 stuff"

ECHO "Verify that abc gets deleted from the directory"
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/dirClient.py --noisy abc | grep abc"
ECHO "Delete a name from the directory"
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/dirClient.py --noisy ~abc"
CMD_PASS "$LIB_DIR/dirClient.py --noisy abc | grep abc"
STATUS=$?
if [ $STATUS -ne 0 ]
then
    ECHO 'Dir delete of abc failed.'
fi


ECHO "Try to delete a bogus name from the directory"
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/dirClient.py ~bogusName"
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/dirClient.py --noisy @DIR"

ECHO "Various commands to the driver dirClient.py for coverage purposes."
ECHO "A request for help is considered a failure"
CMD_FAIL "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/dirClient.py --help abc def"
CMD_FAIL "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/dirClient.py --port=XYZ"
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/dirClient.py --noisy --clear"
CMD_FAIL "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/dirClient.py --bogusArg"

CMD "listening --short $(seq -s ' '  5570 5580)"

# An orderly exit so coverage can collect the runs.
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/dirClient.py --noisy @EXIT"
CMD "listening --short $(seq -s ' '  5570 5580)"
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logCmd.py @EXIT"

CMD "listening --short $(seq -s ' '  5570 5580)"


ECHO Log Filter with configuration file. Notice in-file override
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logFilterApp.py --config=$DATA_DIR/mixed.conf --in-file=$DATA_DIR/mixed.data "

ECHO Log Filter with configuration file. Read from stdin
CMD "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logFilterApp.py --config=$DATA_DIR/mixed.conf < $DATA_DIR/happy.data "
coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logFilterApp.py --config=$DATA_DIR/mixed.conf < $DATA_DIR/happy.data 

ECHO Log Filter with invalid configuration file. Has bad syntax
CMD_FAIL "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logFilterApp.py --config=$DATA_DIR/bad --in-file=$DATA_DIR/mixed.data "

ECHO Log Filter with configuration file. Uses invalid in-file.
CMD_FAIL "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logFilterApp.py --config=$DATA_DIR/mixed.conf --in-file=$DATA_DIR/does_not_exist.data "

ECHO Log Filter with non-existent configuration file. 
CMD_FAIL "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logFilterApp.py --config=$DATA_DIR/does-not-exist.conf "

ECHO Log Filter with configuration file. Uses out_file.
TMP=/tmp/$$.json
export TEST_DIR=$PWD
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logFilterApp.py --config=$DATA_DIR/mixed.conf --in-file=$DATA_DIR/mixed.data --out-file=$TMP "
# Should have something
[ -s $TMP ]
iszero=$?
if [ $iszero -eq 1 ]
then
    echo '==============================================================================='
    echo logFilterApp.py with in-file and in-file should have produced output, but did not.
    echo '==============================================================================='
fi
rm $TMP     # Clean up tmp file.
    

ECHO Same outfile, but with CSV
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logFilterApp.py --config=$DATA_DIR/mixed.conf --CSV --in-file=$DATA_DIR/mixed.data --out-file=$TMP "
# Should have something
[ -s $TMP ]
iszero=$?
if [ $iszero -eq 1 ]
then
    echo '==============================================================================='
    echo logFilterApp.py with in-file and in-file should have produced output, but did not.
    echo '==============================================================================='
fi
CMD "rm $TMP"     # Clean up tmp file.
    

ECHO "Test various command line options for the logCollector.py"
ECHO "Set log file to ./abc.log"
coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logCollector.py --config=$DATA_DIR/logRC.conf --log-file=$DATA_DIR/abc.log --trunc &
CMD_PASS "$LIB_DIR/logCmd.py Testing a new log config option." 
CMD_PASS "$LIB_DIR/logCmd.py @EXIT" 

if [ -f ./abc.log ]
then
    ECHO Expected logfile exists.
    rm ./abc.log
fi

export TMP_CONF=/tmp/$$.conf    # Work configuration file
export TMP_LOG=./zzz.log        # Test log file in local dir.
ECHO  " Create a logCollector.py config file in $TMP_CONF "
cat >$TMP_CONF <<EOF
{
    "append":   True,
    "log-file": '$TMP_LOG',
    "noisy":    False,
    "port":     5570,
}
EOF

coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logCollector.py --config=$TMP_CONF &
CMD "sleep 1"   # Let the collector get started.
CMD_PASS "$LIB_DIR/logCmd.py Testing log config in $TMP_CONF " 
CMD_PASS "$LIB_DIR/logCmd.py Another testing log config in $TMP_CONF " 
CMD "sleep 1"
CMD_PASS "$LIB_DIR/logCmd.py @EXIT" 

if [ -f $TMP_LOG ]
then
    ECHO Expected logfile $TMP_LOG exists.
    CMD "cat $TMP_LOG"
    if [ -x $TMP_LOG ]
    then
        ECHO Size of $TMP_LOG is non-zero
        CMD "cat $TMP_LOG"
    else
        ECHO ERROR: Expected non-zero log size for $TMP_LOG
    fi
else
    ECHO FAIL - Expected log file at $TMP_LOG, not found
fi
CMD "rm $TMP_CONF"
CMD "rm $TMP_LOG"

CMD "listening --short $(seq -s ' '  5570 5580)"

ECHO ""
ECHO "Cover signal interrupt handlers in logCollector.py"
ECHO ""
ECHO "Use kill -INT pid"
coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logCollector.py&
PID=$!
CMD_PASS "sleep 2"  # Let the log collector start
ECHO PID logCollector.py=$PID
CMD_PASS "kill -INT $PID"


ECHO "Use kill -TERM pid"
coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logCollector.py&
PID=$!
CMD_PASS "sleep 2"  # Let the log collector start
ECHO PID logCollector.py=$PID
CMD_PASS "kill -TERM $PID"


ECHO "Use kill -USR1 pid"
coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logCollector.py&
PID=$!
CMD_PASS "sleep 2"  # Let the log collector start
ECHO PID logCollector.py=$PID
CMD_PASS "kill -USR1 $PID"
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logCmd.py @EXIT "

CMD "listening --short $(seq -s ' '  5570 5580)"

ECHO "Various options to logCollector.py"
ECHO "help option passed"
coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logCollector.py --help

coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logCollector.py -a &
PID=$!
CMD_PASS "sleep 1"  # Let the log collector start
ECHO PID logCollector.py=$PID
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logCmd.py @EXIT "

ECHO "Non-numeric port test"
coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logCollector.py --port=XYZ

ECHO "Bogus options --BOGUS"
coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logCollector.py --BOGUS=XYZ

ECHO "Bogus configuration file"
coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logCollector.py --config=/XYZ/does_not_exist
PID=$!

coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logCollector.py --quiet &
PID=$!
CMD_PASS "sleep 1"  # Let the log collector start
ECHO PID logCollector.py=$PID
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logCmd.py @EXIT "


coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logCollector.py --port=5572 &
PID=$!
CMD_PASS "sleep 1"  # Let the log collector start
ECHO PID logCollector.py=$PID
CMD_PASS "coverage run --omit $SITE --branch --parallel-mode $LIB_DIR/logCmd.py --port=5572 @EXIT "

CMD "listening --short $(seq -s ' '  5570 5580)"


CMD "coverage combine  "
CMD "coverage report -m "
CMD "coverage html -d .coverage_html  "

ECHO Paste into browser for details: file://$PWD/.coverage_html/index.html

echo
echo
echo =================================================
echo
echo Total number of tests: $TEST_COUNT
echo
echo Total error count: $ERROR_COUNT
echo
echo Count of expected to pass but failed: $EXPECTED_PASS_BUT_FAIL
echo Expected pass but failed line numbers: ${expect_pass_but_fail[*]}
echo 
echo Count of expected to fail but passed: $EXPECTED_FAIL_BUT_PASS
echo Expected fail but passed line numbers: ${expect_fail_but_pass[*]}
echo
echo =================================================

duration=$SECONDS
echo "Total elapsed time: $(($duration / 60)) minutes and $(($duration % 60)) seconds."

