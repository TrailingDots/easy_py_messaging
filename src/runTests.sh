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
# nature of these tests into python scripts. 


# Uncomment next two lines for debugging and tracing of this script.
#set -x
#PS4='$LINENO: '

# function to echo command and then execute it.
# Do NOT try to start backgrounded commands with this function.
CMD () {
    # BASH_LINENO is an array. Use the top of the stack == 0
    echo "CMD: ${BASH_LINENO[0]} $*"
    $1
}

echo Run pyflakes on all python code
CMD "pyflakes $(find . -name '*.py' -type f)"

# Env var for tracking subprocesses
# Ref: http://coverage.readthedocs.org/en/coverage-4.0.3/subprocess.html
export COVERAGE_PROCESS_START=$PWD/.coveragerc
export CPS=$COVERAGE_PROCESS_START
# coverage wants sitecustomize.py in its path for subprocesses
export PYTHONPATH=$PYTHONPATH:$PWD/tests:$PWD/.
echo COVERAGE_PROCESS_START=$CPS

#./wc.sh     # How big is this getting?

export BASE_DIR=$PWD
export LIB_DIR=$BASE_DIR/lib
export TEST_DIR=$BASEDIR/tests

echo Remove all logs.log
rm $(find . -name logs.log)
echo Remove all .coverage.*
rm $(find . -name '.coverge.*' -type f)
echo Remove tests/.coverage_html/*
(cd tests; rm -rf .coverage_html)

#
# Before starting, make sure the logCollector is running.
CMD "./tests/listeningPort.py 5570"
if [ $? -ne 0 ]
then
    # Determine the pid holding this port. Then error out.
    echo >&2
    echo >&2 =============================================================================
    echo >&2
    echo >&2 Port 5570 is already instantiated. kill $(./tests/listeningPort.py --pid 5570)
    echo >&2 $(./tests/listeningPort.py 5570)
    echo >&2
    echo >&2 =============================================================================
    echo >&2
    exit 1
fi

#
# Run a coverage report on unit tests
#
CMD "cd tests "
export COVERAGE=1 
CMD "coverage erase "
CMD "coverage run --branch --parallel-mode --source=../tests,../$LIB_DIR testLogging.py"
CMD "echo last run status: $? "
CMD "sleep 5 "

# Generate a "standard" log of data used in testing.
CMD "./genData.py >../$LIB_DIR/data.log"


# Need to get a timed alarm in case the collector does not start.
# Problems with logCollector - Need to get a proper term to close the coverage files.
CMD "echo starting logCollector"
coverage run --branch --parallel-mode $LIB_DIR/logCollector.py & 
COL_PID=$! 

CMD "coverage run --branch --parallel-mode $LIB_DIR/loggingClientTask.py "

CMD "coverage run --branch --parallel-mode $LIB_DIR/loggingSpeedTest.py  "
CMD "coverage run --branch --parallel-mode ./loggingLoopApp.py 10   "
CMD "coverage run --branch --parallel-mode ./testLogging.py "
CMD "coverage run --branch --parallel-mode ./genData.py >/dev/null "
CMD "coverage run --branch --parallel-mode ./genData.py --happy   "
CMD "coverage run --branch --parallel-mode ./genData.py --missing "
CMD "coverage run --branch --parallel-mode ./genData.py --mixed   "
CMD "coverage run --branch --parallel-mode ./genData.py --help    "
CMD "coverage run --branch --parallel-mode ./genData.py --config=datedFilter "
CMD "coverage run --branch --parallel-mode ./genData.py --config=csvFilter "
CMD "coverage run --branch --parallel-mode ./genData.py --config=baseFilter "
CMD "coverage run --branch --parallel-mode ./genData.py --config=bogusFilter "
echo An invalid filter
CMD "coverage run --branch --parallel-mode ./genData.py ----config=bogusFilter "    # An invalid filter

echo Coverage for apiLoggerInit
CMD "coverage run --branch --parallel-mode $LIB_DIR/apiLoggerInit.py "

# Test the listening port utility
CMD "coverage run --branch --parallel-mode ./listeningPort.py --help "
CMD "coverage run --branch --parallel-mode ./listeningPort.py 5570 "
CMD "coverage run --branch --parallel-mode ./listeningPort.py --short 5570 "
CMD "coverage run --branch --parallel-mode ./listeningPort.py --short  "
CMD "coverage run --branch --parallel-mode ./listeningPort.py --pid 5570 "
CMD "coverage run --branch --parallel-mode ./listeningPort.py --pid  "
CMD "coverage run --branch --parallel-mode ./listeningPort.py --proc  "
CMD "coverage run --branch --parallel-mode ./listeningPort.py --proc 5570 "
CMD "coverage run --branch --parallel-mode ./listeningPort.py --proc 6666 "
CMD "coverage run --branch --parallel-mode ./listeningPort.py --bogus 6666 "
CMD "coverage run --branch --parallel-mode ./listeningPort.py bogus-port "

CMD "coverage run --branch --parallel-mode ../$LIB_DIR/apiLoggerInit.py "

echo Multiple runs passing various flags both valid and bogus.
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --in-file=../lib/data.log --JSON "
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --in-file=../lib/data.log --JSON --level=ERROR "
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --in-file=../lib/data.log --CSV "
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --in-file=../lib/data.log --CSV --level=ERROR "
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --Xin-file=../lib/data.log --CSV --level=ERROR "
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --help "
echo
echo Expect ERRORs
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --in-file=bogus_file --CSV --level=ERROR "
echo Expect ERRORs - bogus log level
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --in-file=bogus_file --CSV --level=Bogus "
echo
echo Expect ERRORs
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --in-file=/dev/null --CSV --level=ERROR "
echo
echo Expect ERRORs
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --in-file=/dev/null --JSON --level=ERROR "

echo No infile. Reads from stdin
cat happy.data | coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py 

echo
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --out-file=/dev/null --in-file=../lib/data.log --JSON "
echo
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --start-date=1970-01-01T00:00:00.000 --out-file=/dev/null --in-file=../lib/data.log --JSON "
echo
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --start-date=1970-01-01T00:00:00.000 --end-date=2020-01-01T00:00:00.000 --out-file=/dev/null --in-file=../lib/data.log --JSON "
echo 
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --end-date=2020-01-01T00:00:00.000 --out-file=/dev/null --in-file=../lib/data.log --JSON "
echo 
echo Syntax error on end date
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --end-date=2017-01-01:00:00:00.000 --out-file=/dev/null --in-file=../lib/data.log --JSON "
echo
echo Permission denied on output file.
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --out-file=/ --in-file=../lib/data.log --JSON "
echo
echo Permission denied on input file.
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --out-file=/dev/null --in-file=/var/log/messages --JSON "

echo
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --out-file=/dev/null --in-file=../lib/data.log --CSV "
echo
echo Permission denied on output file.
echo
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --out-file=/ --in-file=../lib/data.log --CSV "
echo
echo Permission denied on input file.
echo
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --out-file=/dev/null --in-file=/var/log/messages --CSV "

echo
echo Filter on dates as well.
echo These tests depend on the dates as set in ./tests/getData.py and the ./lib/data.log file
echo start only
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --in-file=../lib/data.log --JSON --start-date=2016-03-14T08:00:00.000 "
echo Syntax Error for start only
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --in-file=../lib/data.log --JSON --start-date=2016-03-14:08:00:00.000 "
echo
echo start and end dates
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --in-file=../lib/data.log --JSON --start-date=2016-03-14T08:00:00.000 end=2016-03-14T08:05:15.876 "

echo
echo Log Filter with configuration file. Notice in-file override
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --config=mixed.conf --in-file=mixed.data "

echo
echo Log Filter with configuration file. Read from stdin
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --config=mixed.conf < happy.data "

echo
echo Log Filter with invalid configuration file. Has bad syntax
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --config=bad --in-file=mixed.data "

echo
echo Log Filter with configuration file. Uses invalid in-file.
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --config=mixed.conf --in-file=does_not_exist.data "

echo
echo Log Filter with non-existent configuration file. 
CMD "coverage run --branch --parallel-mode $LIB_DIR/logFilterApp.py --config=does-not-exist.conf "

echo
echo Log Filter with configuration file. Uses out_file.
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
    

echo
echo Same outfile, but with CSV
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

echo Paste into browser for details: file://$PWD/.coverage_html/index.html

#(cd tests; python testLogging.py)
