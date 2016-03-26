#!/bin/bash

#
# The following prerequesites must exist for proper
# operations of this script:
#   pyflakes
#   coverage
# Install these python package in the normal way.
#

#
# Recommended way to operate:
#   script                  # Start collecting all output
#   ./runTests.sh ; exit    # run this script then exit script shell
#   vim typescript          # Default output of "script" goes into typescript
#
# Some errors are expected! However, there should be no tracebacks.
#
# An unfortunate reason that this script runs so many test rests in the
# inability of coverage to handle subprocesses properly!
# Much time was spent attempting to encapsulate the repetitious
# nature of these test into python scripts. 


# Uncomment next two lines for debugging and tracing of this script.
#set -x
#PS4='$LINENO: '

# function to echo command and then execute it.
# Do NOT try to start backgrounded commands with this function.
CMD () {
    # BASH_LINENO is an array. Use the top of the stack == 0
    echo
    echo "CMD ${BASH_LINENO[0]}: $*"
    $1
}

# function to simply echo with a line number
ECHO () {
    # BASH_LINENO is an array. Use the top of the stack == 0
    echo "ECHO ${BASH_LINENO[0]}: $*"
}

echo Run pyflakes on all python code
CMD "pyflakes $(find . -name '*.py' -type f)"

# Env var for tracking subprocesses
# Ref: http://coverage.readthedocs.org/en/coverage-4.0.3/subprocess.html
export COVERAGE_PROCESS_START=$PWD/.coveragerc
ECHO " export COVERAGE_PROCESS_START=$COVERAGE_PROCESS_START"

export CPS=$COVERAGE_PROCESS_START
ECHO "CPS=$CPS"

export PYTHONPATH=$PYTHONPATH:$PWD/test:$PWD/.
ECHO "PYTHONPATH=$PYTHONPATH"

#echo COVERAGE_PROCESS_START=$CPS

#./wc.sh     # How big is this getting?

export BASE_DIR=$PWD
ECHO "BASE_DIR=$BASE_DIR"

export LIB_DIR=$BASE_DIR/lib
ECHO "LIB_DIR=$LIB_DIR"

export TOOLS_DIR=$BASE_DIR/../tools
ECHO "TOOLS_DIR=$TOOLS_DIR"

export TEST_DIR=$BASE_DIR/test
ECHO "TEST_DIR=$TEST_DIR"

export GEN_DATA=$TEST_DIR/genData.py
ECHO "GEN_DATA=$GEN_DATA"

ECHO Remove all logs.log
ECHO "rm $(find . -name logs.log)"

ECHO Remove all .coverage.*
rm $(find . -name '.coverge.*' -type f)

ECHO Remove test/.coverage_html/*
(cd test; rm -rf .coverage_html)

#
ECHO Before starting, make sure the logCollector is running.
CMD "$TOOLS_DIR/listeningPort.py 5570"
if [ $? -ne 0 ]
then
    # Determine the pid holding this port. Then error out.
    echo >&2
    echo >&2 =============================================================================
    echo >&2
    echo >&2 Port 5570 is already instantiated. kill $($TOOLS_DIR/listeningPort.py --pid 5570)
    echo >&2 $($TOOLS_DIR/listeningPort.py 5570)
    echo >&2
    echo >&2 =============================================================================
    echo >&2
    exit 1
fi

#
ECHO Run a coverage report on unit test
#
CMD "cd test "
export COVERAGE=1 
CMD "coverage erase "
CMD "coverage run --branch --parallel-mode --source=../test,../$LIB_DIR testLogging.py"
CMD "echo last run status: $? "

# Generate a "standard" log of data frequently used in testing.
export DATA_LOG=$TEST_DIR/data.data
CMD "DATA_LOG=$DATA_LOG"
CMD "$GEN_DATA >$DATA_LOG"


ECHO Need to get a timed alarm in case the collector does not start.
ECHO Problems with logCollector - Need to get a proper term to close the coverage files.
ECHO "echo starting logCollector"
coverage run --branch --parallel-mode $LIB_DIR/logCollector.py & 
COL_PID=$! 

CMD "coverage run --branch --parallel-mode $LIB_DIR/loggingClientTask.py "

CMD "coverage run --branch --parallel-mode $LIB_DIR/loggingSpeedTest.py  "
CMD "coverage run --branch --parallel-mode ./loggingLoopApp.py 10   "
CMD "coverage run --branch --parallel-mode ./testLogging.py "
CMD "coverage run --branch --parallel-mode $GEN_DATA >/dev/null "
CMD "coverage run --branch --parallel-mode $GEN_DATA --happy   "
CMD "coverage run --branch --parallel-mode $GEN_DATA --missing "
CMD "coverage run --branch --parallel-mode $GEN_DATA --mixed   "
CMD "coverage run --branch --parallel-mode $GEN_DATA --help    "
CMD "coverage run --branch --parallel-mode $GEN_DATA --config=datedFilter "
CMD "coverage run --branch --parallel-mode $GEN_DATA --config=csvFilter "
CMD "coverage run --branch --parallel-mode $GEN_DATA --config=baseFilter "
CMD "coverage run --branch --parallel-mode $GEN_DATA --config=bogusFilter "
ECHO An invalid filter
CMD "coverage run --branch --parallel-mode $GEN_DATA ----config=bogusFilter "    # An invalid filter

ECHO Coverage for apiLoggerInit
CMD "coverage run --branch --parallel-mode $LIB_DIR/apiLoggerInit.py "

ECHO Test the listening port utility
CMD "coverage run --branch --parallel-mode $TOOLS_DIR/listeningPort.py --help "
CMD "coverage run --branch --parallel-mode $TOOLS_DIR/listeningPort.py 5570 "
CMD "coverage run --branch --parallel-mode $TOOLS_DIR/listeningPort.py --short 5570 "
CMD "coverage run --branch --parallel-mode $TOOLS_DIR/listeningPort.py --short  "
CMD "coverage run --branch --parallel-mode $TOOLS_DIR/listeningPort.py --pid 5570 "
CMD "coverage run --branch --parallel-mode $TOOLS_DIR/listeningPort.py --pid  "
CMD "coverage run --branch --parallel-mode $TOOLS_DIR/listeningPort.py --proc  "
CMD "coverage run --branch --parallel-mode $TOOLS_DIR/listeningPort.py --proc 5570 "
CMD "coverage run --branch --parallel-mode $TOOLS_DIR/listeningPort.py --proc 6666 "
CMD "coverage run --branch --parallel-mode $TOOLS_DIR/listeningPort.py --bogus 6666 "
CMD "coverage run --branch --parallel-mode $TOOLS_DIR/listeningPort.py bogus-port "

CMD "coverage run --branch --parallel-mode $LIB_DIR/apiLoggerInit.py "

ECHO Multiple runs passing various flags both valid and bogus.
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --in-file=$DATA_LOG --JSON "
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --in-file=$DATA_LOG --JSON --level=ERROR "
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --in-file=$DATA_LOG --CSV "
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --in-file=$DATA_LOG --CSV --level=ERROR "
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --Xin-file=$DATA_LOG --CSV --level=ERROR "
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --help "
ECHO Expect ERRORs
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --in-file=bogus_file --CSV --level=ERROR "
ECHO Expect ERRORs - bogus log level
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --in-file=bogus_file --CSV --level=Bogus "
ECHO Expect ERRORs
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --in-file=/dev/null --CSV --level=ERROR "
ECHO Expect ERRORs
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --in-file=/dev/null --JSON --level=ERROR "
ECHO Expecte ERRORS 
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --config=./csv.conf --in-file=/dev/null --JSON --level=ERROR "
ECHO Expecte ERRORS 
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --config=./happy.conf "
ECHO Expecte ERRORS 
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --config=./mixed.conf "
ECHO Expecte ERRORS 
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --config=./bad.conf "
ECHO Expecte ERRORS 
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --config=./bad2.conf "
ECHO Expecte ERRORS 
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --config=./bad3.conf "
ECHO Expecte ERRORS 
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --config=./no_start.conf "
ECHO Expecte ERRORS 
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --config=./no_end.conf "
ECHO Expecte ERRORS 
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --config=./no_end1.conf "
ECHO Expecte ERRORS 
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --config=./no_start1.conf "
ECHO Expecte ERRORS 
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --config=./bad_start.conf "
ECHO Expecte ERRORS 
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --config=./bad_end.conf "
ECHO Expecte ERRORS 
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --config=./end_before_start.conf "

ECHO No infile. Reads from stdin
cat happy.data | coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py 

CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --out-file=/dev/null --in-file=$DATA_LOG --JSON "
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --start-date=1970-01-01T00:00:00.000 --out-file=/dev/null --in-file=$DATA_LOG --JSON "
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --start-date=1970-01-01T00:00:00.000 --end-date=2020-01-01T00:00:00.000 --out-file=/dev/null --in-file=$DATA_LOG --JSON "
ECHO 
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --end-date=2020-01-01T00:00:00.000 --out-file=/dev/null --in-file=$DATA_LOG --JSON "
ECHO Syntax error on end date
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --end-date=2017-01-01:00:00:00.000 --out-file=/dev/null --in-file=$DATA_LOG --JSON "
ECHO Permission denied on output file.
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --out-file=/ --in-file=$DATA_LOG --JSON "
ECHO Permission denied on input file.
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --out-file=/dev/null --in-file=/var/log/messages --JSON "

CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --out-file=/dev/null --in-file=$DATA_LOG --CSV "
ECHO Permission denied on output file.
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --out-file=/ --in-file=$DATA_LOG --CSV "
ECHO Permission denied on input file.
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --out-file=/dev/null --in-file=/var/log/messages --CSV "

ECHO Filter on dates as well.
ECHO These test depend on the dates as set in ./test/getData.py and the $DATA_LOG file
ECHO start only
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --in-file=$DATA_LOG --JSON --start-date=2016-03-14T08:00:00.000 "
ECHO Syntax Error for start only
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --in-file=$DATA_LOG --JSON --start-date=2016-03-14:08:00:00.000 "
ECHO start and end dates
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --in-file=$DATA_LOG --JSON --start-date=2016-03-14T08:00:00.000 end=2016-03-14T08:05:15.876 "

ECHO Log Filter with configuration file. Notice in-file override
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --config=mixed.conf --in-file=mixed.data "

ECHO Log Filter with configuration file. Read from stdin
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --config=mixed.conf < happy.data "

ECHO Log Filter with invalid configuration file. Has bad syntax
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --config=bad --in-file=mixed.data "

ECHO Log Filter with configuration file. Uses invalid in-file.
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --config=mixed.conf --in-file=does_not_exist.data "

ECHO Log Filter with non-existent configuration file. 
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --config=does-not-exist.conf "

ECHO Log Filter with configuration file. Uses out_file.
TMP=/tmp/$$.json
export TEST_DIR=$PWD
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --config=$TEST_DIR/mixed.conf --in-file=$TEST_DIR/mixed.data --out-file=$TMP "
# Should have something
[ -s $TMP ]
iszero=$?
if [ $iszero -eq 1 ]
then
    echo '==============================================================================='
    echo logFilterApp with in-file and out-file should have produced output, but did not.
    echo '==============================================================================='
fi
rm $TMP     # Clean up tmp file.
    

ECHO Same outfile, but with CSV
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --config=$TEST_DIR/mixed.conf --CSV --in-file=$TEST_DIR/mixed.data --out-file=$TMP "
# Should have something
[ -s $TMP ]
iszero=$?
if [ $iszero -eq 1 ]
then
    echo '==============================================================================='
    echo logFilterApp with in-file and out-file should have produced output, but did not.
    echo '==============================================================================='
fi
CMD "rm $TMP"     # Clean up tmp file.
    

CMD "kill -HUP $COL_PID"


CMD "coverage combine  "
CMD "coverage report -m --omit=../lib/logCollector.py "
CMD "coverage html -d .coverage_html  --omit=../lib/logCollector.py "

ECHO Paste into browser for details: file://$PWD/.coverage_html/index.html

CMD "cd $BASE_DIR"
#(cd test; python testLogging.py)
