#!/usr/bin/env python
import unittest
import os
import sys
import signal
import subprocess
import platform
import datetime
import logging
import time
import tempfile
import json
import traceback

abs_file = os.path.abspath(__file__)
abs_dir = os.path.dirname(abs_file)

sys.path.append(abs_dir + '/..')
sys.path.append(abs_dir + '/../../')

from easy_py_messaging import apiLoggerInit
from easy_py_messaging.utils import bcolors
from easy_py_messaging.utils import cycle_priority
from easy_py_messaging import logFilter
from easy_py_messaging import logConfig
from easy_py_messaging import utils
from easy_py_messaging import logCollector
from easy_py_messaging import loggingSpeedTest
from easy_py_messaging import loggingClientTask
from easy_py_messaging import listeningPort

# Name/Directory service - both client and server
from easy_py_messaging import dirSvc
from easy_py_messaging import dirClient


# Single test example:
#    python -n unittest testLogging.RunTests.testNaming



def fcnName(func):
    """Decorator to print function name before running test."""
    def wrapper(*func_args, **func_kwargs):
        print('=== test fcn: ' + func.__name__)
        return func(*func_args, **func_kwargs)
    return wrapper

class RunTests(unittest.TestCase):

    @fcnName
    def testConfigSettings(self):
        """
        Spawn the server and client loggers
        in their own separate procsses.
        """
        abs_path_server = os.path.abspath(logCollector.__file__)
        abs_path_app = os.path.abspath(loggingClientTask.__file__)

        log_filename = os.path.abspath('./logs.log')
        print '***** log_filename:%s' % log_filename

        # Remove existing log file
        # Other tests will test for append mode.
        if os.path.exists(log_filename) and os.path.isfile(log_filename):
            os.remove(log_filename)

        print 'starting collector'
        argv_collector = ['python',
                           abs_path_server,
                           '--log-file', log_filename,
                           '-t']
        proc_collector = subprocess.Popen(argv_collector)
        print ' '.join(argv_collector)
        print (bcolors.BGGREEN +
            ('proc_collector pid: %d' % proc_collector.pid) +
            bcolors.ENDC)

        argv_client = ['python',
                        abs_path_app, '123']
        print 'starting loggingClientTask:' + ' '.join(argv_client)
        proc_app = subprocess.Popen(argv_client,
            stderr=subprocess.STDOUT)
        print (bcolors.BGGREEN +
                ('proc_app pid: %d' % proc_app.pid) +
                bcolors.ENDC)

        # Allow some time to process.
        seconds_to_sleep = 5
        print '%d seconds to process subprocs' % seconds_to_sleep
        time.sleep(seconds_to_sleep)

        # Kill both processes: collector and log generator
        os.kill(proc_app.pid, signal.SIGINT)
        os.kill(proc_collector.pid, signal.SIGINT)

        # Set the log level to log everything == NOTSET
        logging.basicConfig(level=logging.NOTSET)

        # Now read the log file and make sure expected logs exist.
        # The messages from logginClientTask.main() get logged.
        log_fh = open(log_filename, 'r')
        log_lines = log_fh.read()

        # Junk messages. The output logs will be inspected for
        # the presense of these messages.
        warning_msg = 'msg=Warning,a=n,stuff=yuck,floor=ceiling'
        error_msg = 'status=3,warn=continue,babble=yes,reason=testing'
        debug_msg = 'msg=debug,details=yes'
        critical_msg = 'msg=critical,reason=meltdown'
        info_msg = 'status=1,msg=info,reason=nothing important'

        # FIXME TODO - make this a real unit test!
        msgs = [warning_msg,
                error_msg,
                debug_msg,
                critical_msg,
                info_msg,
               ]
        """ TODO FIXME - get a real unit test!
        for msg in msgs:
            print 'Testing:' + msg
            self.failUnless(msg in log_lines)
        """

    @fcnName
    def testLoggingSpeed(self):
        """How many messages per second?"""
        abs_path_server = os.path.abspath(logCollector.__file__)
        abs_path_app = os.path.abspath(loggingSpeedTest.__file__)

        log_filename = os.path.abspath('/dev/null')
        print '***** log_filename:%s' % log_filename

        # Remove existing log file
        # Other tests will test for append mode.
        if os.path.exists(log_filename) and os.path.isfile(log_filename):
            os.remove(log_filename)

        print 'starting collector'
        argv_collector = ['python',
                          abs_path_server,
                          '--log-file', log_filename,
                          '-t']
        proc_collector = subprocess.Popen(argv_collector)
        print ' '.join(argv_collector)
        print (bcolors.BGGREEN +
            ('proc_collector pid: %d' % proc_collector.pid) +
            bcolors.ENDC)

        # Allow the collector to start
        time.sleep(1)

        print bcolors.BGRED + 'starting speed app' + bcolors.ENDC + \
                abs_path_app
        speed_app_args = ['python', abs_path_app, '456']
        speed_app = subprocess.Popen(speed_app_args)
        print ' '.join(speed_app_args)
        print (bcolors.BGGREEN +
                ('speed_app pid: %d' % speed_app.pid) +
                bcolors.ENDC)

        # Allow some time to process.
        # Since the speed tests sends 100,000 messages,
        # The writes on the logCollector side may take
        # some time to send these to a disk file.
        # A possibly more accurate test would send the
        # logs to /dev/null to eliminate I/O time.
        seconds_to_sleep = 10
        print '%d seconds to process subprocs' % seconds_to_sleep
        time.sleep(seconds_to_sleep)

        # Kill both processes
        os.kill(speed_app.pid, signal.SIGINT)
        os.kill(proc_collector.pid, signal.SIGINT)


@fcnName
def gen_happy_path(sep_char=utils.PAYLOAD_CONNECTOR,
        key_val_sep=utils.KEY_VALUE_SEPARATOR):
    """
    WARNING: DO NOT LIGHTLY CHANGE THESE TEST LOGS! Unit test uses these!

    Generate happy path data with  payload separator
    and key/value separator chars.
    """
    testData = ''
    testData += '2016-03-10T11:00:39.697\tDEBUG\ta=b&temp=34.5&item=Good Stuff\n'
    testData += '2016-03-10T11:00:39.697\tCMD\ta=b&temp=34.5&item=Good Stuff\n'
    testData += '2016-03-10T11:01:39.697\tWARNING\ta=b&temp=74.5&item=cool\n'
    testData += '2016-03-10T11:01:39.697\tERROR\ta=blah&temp=999&item=cool\n'
    testData += '2016-03-10T11:02:39.697\tDEBUG\ta=b&temp=82.5&item=funny\n'
    testData += '2016-03-10T11:03:39.697\tCRITICAL\ta=b&temp=99.34.5&item=Stupid Stuff'
    testData = testData.replace('=', key_val_sep)
    testData = testData.replace('&', sep_char)
    return testData


@fcnName
def gen_missing_data(sep_char=utils.PAYLOAD_CONNECTOR,
        key_val_sep=utils.KEY_VALUE_SEPARATOR):
    """
    WARNING: DO NOT LIGHTLY CHANGE THESE TEST LOGS! Unit test uses these!

    Generate data with some emtpy values
    and key/value separator chars.
    """
    testData = ''
    # Good line
    testData += '2016-03-10T11:00:39.697\tDEBUG\ta=b&temp=&item=Good Stuff\n'
    # Doubled &&
    testData += '2016-03-10T11:01:39.697\tWARNING\ta=b&&item=cool\n'
    # key=value=value problem(?)
    testData += '2016-03-10T11:02:39.697\tDEBUG\ta=b=c&temp=82.5&item=funny\n'
    testData += '2016-03-10T11:03:39.697\tCRITICAL\ta=&temp=99.34.5&item=Stupid Stuff\n'
    testData += '2016-03-10T11:02:39.697\tCMD\ta=b=c&temp=82.5&item=funny\n'
    # & at end of line
    testData += '2016-03-10T11:03:39.697\tCRITICAL\t=b&temp=99.34.5&item=Stupid Stuff&\n'
    # duplicated keyword "temp"
    testData += '2016-03-10T11:03:39.697\tCRITICAL\ta=b&temp=99.34.5&temp=999.999&item=Stupid Stuff&\n'
    testData = testData.replace('=', key_val_sep)
    testData = testData.replace('&', sep_char)
    return testData

@fcnName
def gen_mixed_data(sep_char=utils.PAYLOAD_CONNECTOR,
        key_val_sep=utils.KEY_VALUE_SEPARATOR):
    """
    WARNING: DO NOT LIGHTLY CHANGE THESE TEST LOGS! Unit test uses these!

    Even in our simple Raspberry Pi hydroponic system,
    a bit of thought placed into logging concepts
    will absolutely serve us well. Just logging
    for logging sakes does not provide an incentive
    to log. Having these logs provide a usable history
    and alarm system incentivises our logging structure.

    Think of logging as an integral part of our SCADA system.
    SCADA = Supervisory Control and Data Acquisition.
    SCADA gets used in remote monitoring and control
    systems that operates with coded signals
    over communications channels. <a href="https://en.wikipedia.org/wiki/SCADA">
    Wikipedia: SCADA</a>

    Some logs that an elementary SCADA system could generate.
    The model is, once again, a hydroponics system. The
    hydroponics system has 2 Raspberry Pis controlling various
    devices and this logs to a desktop. The desktop may
    send control commands. Various logs from both systems
    get sent to the logger to monitor and track events
    in these systems.

    Assume "hydro1" and "hydro2" are systems in a remote
    hydroponics garden with various measurement
    instrumentations. This remote system logs to a
    desktop inside the home.

    Commands the remote uses to start pumps and switchs
    get logged as well. This used "cmd=true&pump1=ON&host=hydro1"
    meaning this is a command that turns pump1 on and
    the host is hydro1.

    Generate data that would look like more ordinary
    data. This includes:
        A named switch changing values ON/OFF.
        An instrument reporting temperature reading.
        A water level indicator reading too low or to high.
        A moisture level too low has triggered.
        A periodic report of temperature
    and key/value separator chars.

    Notice the keywords:
    --------------------
    device = Device name
    state = Value for descrete devices: ON, OFF, UNKNOWN
    temp = Temperature reading for analog temperature
    host = Which system sent this data
    cmd=req = A command request was sent. host=system performing req
                cmd=req&tag=xyz...&host=central

    cmd=rep = A command reply indicates acknowledgement. host=sys performing command.
              A reply sends the tag of the command. Optionally the entire
              original command may populate the command.
              cmd=rep&tag=xyz&host=hygro1

    Devices in this example:
      pump01 = A water pump to maintain proper levels.
      water01 = A flotation switch that detects water levels too high or too low.
      tempIN, tempOUT = analog temperature measurements.

    All analog and discrete devices may send "UNKNOWN" as a connection could
    have dropped, power lost, wiring problems, ...
    """

    testData = ''
    # A periodic reading of water and temperature from several instruments
    testData += '2016-03-14T08:00:00.000\tINFO\tdevice=water01&state=OFF&host=hydro1\n'
    testData += '2016-03-14T08:00:00.000\tINFO\tdevice=tempIN&temp=72.3&host=hydro1\n'
    testData += '2016-03-14T08:00:00.000\tINFO\tdevice=tempOUT&temp=69.2&host=hydro1\n'
    # Water level has gone too low
    testData += '2016-03-14T08:00:07.325\tERROR\tdevice=water01&state=LOW&host=hydro1\n'
    # Pump started to raise water level. A command was sent
    # pump01 request to start.
    testData += '2016-03-14T08:00:09.876\tINFO\tcmd=req&tag=xyz=pump01&state=ON&host=hydro1\n'
    # Command started, remote sends reply. Note use of "tag"
    testData += '2016-03-14T08:00:09.876\tINFO\tcmd=rep&tag=xyz&host=hydro1\n'
    # Water level back to normal and turn pump1 off.
    testData += '2016-03-14T08:05:05.325\tINFO\tdevice=water01&state=OK&host=hydro1\n'
    # Pump turns off
    testData += '2016-03-14T08:05:15.876\tINFO\tcmd=req&tag=abc&pump01=OFF&host=hydro1\n'
    # Pump starting to off state.
    testData += '2016-03-14T08:05:15.876\tINFO\tcmd=rep&tag=abc&host=hydro1\n'
    # Periodic temperature readings
    # More likely would be one reading per device.
    testData += '2016-03-14T08:10:00.000\tINFO\tdevice=water01&state=OK&pump01=OFF&temp04=70.1&temp03=69.0&host=hydro1\n'
    testData += '2016-03-14T08:10:00.000\tINFO\tdevice=pump01&device=temp04&temp=70.1&temp03=69.0&host=hydro1\n'
    testData += '2016-03-14T08:10:00.000\tINFO\tdevice=pump01&device=temp03&temp=69.0&host=hydro1\n'
    #
    # BROKEN - FIXME - need one device per request! "circulation" is a macro
    # Normal circulation started on command. Notice multiple devices turned on.
    testData += '2016-03-14T08:12:14.734\tINFO\tcmd=req&tag=circulation&water01=OK&pump01=ON&circulation=ON&host=hydro1\n'
    # Circulation started
    testData += '2016-03-14T08:12:14.734\tINFO\tcmd=rep&tag=circulation&&host=hydro1\n'
    # Normal circulation finished. Simply status indicating state of devices.
    testData += '2016-03-14T08:22:14.739\tINFO\twater01=OK&pump01=OFF&circulation=OFF&host=hydro1\n'

    testData = testData.replace('=', key_val_sep)
    testData = testData.replace('&', sep_char)
    return testData


class TestLogs2CSV(unittest.TestCase):
    # python -m unittest testLogging.TestLogs2CSV
    @fcnName
    def testHappyPath_1(self):
        print 'testHappyPath'
        testData = gen_happy_path()
        lines = testData.split('\n')

        # Check the keyword header line in CSV
        try:
            csv = logFilter.LogFilterCSV({})
        except Exception as err:
            sys.stderr.write('Invalid configuration file:%s\n' % err)
            return 1
        csv.parse_log_entry(lines[0])
        print csv.log_keys()     # Sorted keys matching data

        self.failUnless('date' in csv.log_dict)
        self.failUnless('level' in csv.log_dict)
        self.failUnless(csv.log_dict['level'] == 'DEBUG')
        self.failUnless('a' in csv.log_dict)
        self.failUnless(csv.log_dict['a'] == 'b')
        self.failUnless('item' in csv.log_dict)
        self.failUnless(csv.log_dict['item'] == 'Good Stuff')

    @fcnName
    def testHappyPath_Warning(self):
        print 'testHappyPath_Warning'
        testData = gen_happy_path()
        lines = testData.split('\n')

        # Check the keyword header line in CSV
        try:
            csv = logFilter.LogFilterCSV({})
        except Exception as err:
            sys.stderr.write('Invalid configuration file:%s\n' % err)
            return 1
        log_dict = csv.parse_log_entry(lines[1])

        self.failUnless('date' in log_dict)
        self.failUnless('level' in log_dict)
        self.failUnless(log_dict['level'] == 'CMD')
        self.failUnless('a' in log_dict)
        self.failUnless(log_dict['a'] == 'b')
        self.failUnless('item' in log_dict)
        self.failUnless(log_dict['item'] == 'Good Stuff')

    @fcnName
    def testMissingData(self):
        print 'testMissingData'
        testData = gen_missing_data()
        lines = testData.split('\n')

        # Check the keyword header line in CSV
        try:
            lf = logFilter.LogFilterCSV({})
        except Exception as err:
            sys.stderr.write('Invalid configuration file:%s\n' % err)
            return 1
        log_dict = lf.parse_log_entry(lines[0])

        self.failUnless('date' in log_dict)
        self.failUnless('level' in log_dict)
        self.failUnless(log_dict['level'] == 'DEBUG')
        self.failUnless('a' in log_dict)
        self.failUnless(log_dict['a'] == 'b')
        self.failUnless('item' in log_dict)
        self.failUnless(log_dict['item'] == 'Good Stuff')

    @fcnName
    def testMixedData(self):
        print 'testMixedData'
        testData = gen_mixed_data()
        lines = testData.split('\n')

        # select only WARNING or higher
        log_filters = logFilter.LogFilters.copy()   # don't zap original!
        log_filters['level'] = 'WARNING'
        try:
            lf = logFilter.LogFilterCSV(log_filters)
        except Exception as err:
            sys.stderr.write('Invalid configuration file:%s\n' % err)
            return 1

        log_dict = lf.parse_log_entry(lines[0])
        self.failUnless(log_dict is None)

        log_dict = lf.parse_log_entry(lines[3])
        self.failUnless(log_dict != None)
        self.failUnless(log_dict['level'] == 'ERROR')
        self.failUnless('date' in log_dict)


class TestISO8601(unittest.TestCase):
    """
    python -m unittest testLogging.TestISO8601

    Current bash date rounded to microseconds:
        date +"%s.%6N"
        1458149245.545454

    In milliseconds:
        date +%s%3N
        1458149374982

    Python:
        import time
        cur_time = int(time.time()*1000)

    Ref: https://www.gnu.org/software/coreutils/manual/html_node/Examples-of-date.html
    To convert a date string to the number of seconds since the start of the epoch
    use the '%s" format:
        date --date='1970-01-01 00:02:00 +0000' +%s
        120

    If you do not specify time zone information in the date string, date uses your
    computer's idea of the time zone:
        # local time zone used
        date --date='1970-01-01 00:02:00' +%s
        18120
    Also the --utc (-u) option:
        date --date='2000-01-01 UTC' +%s
        946684800
    To convert such an unwieldy number of seconds back to a more readable form, use
    a command like this:
        date -d @946684800 +"%F %T %z"
        1999-12-31 19:00:00 -0500
    Often it is better to output UTC-relative date and time:
        date -u -d '1970-01-01 946684800 seconds' +"%Y-%m-%d %T %z"
        2000-01-01 00:00:00 +0000
    """
    @fcnName
    def testUnixToISO8601_0(self):
        """ From unix time to external local ISO8601 """

        # date --date='2016-03-14T08:00:09.123456' +%s.%6N
        # Generally obtain from time.time()
        date_now = 1457967609.123456
        date_time_now = datetime.datetime.fromtimestamp(date_now)
        print 'date_time_now:%s' % str(date_time_now)
        self.failUnless(str(date_time_now) == '2016-03-14 08:00:09.123456')
        fmt = '%Y-%m-%dT%H:%M:%S.%f'
        now_str = date_time_now.strftime(fmt)
        print 'now_str:%s' % now_str
        self.failUnless(str(now_str) == '2016-03-14T08:00:09.123456')
        now_tuple = datetime.datetime.strptime(now_str, fmt)
        print 'now_tuple:%s' % str(now_tuple)
        self.failUnless(str(now_tuple) == '2016-03-14 08:00:09.123456')
        print 'microsecond:%s' % now_tuple.microsecond
        seconds = time.mktime(now_tuple.timetuple())
        print 'seconds:%s' % str(seconds)
        sec_epoch = time.mktime(now_tuple.timetuple()) + 1.0e-6*now_tuple.microsecond
        sec_epoch = seconds + now_tuple.microsecond/1000000.0
        print 'sec_epoch: %s' % sec_epoch
        # date -d @1457967609.123456 +%FT%T.%N
        # 2016-03-14T08:00:09.123456000
        self.failUnless(sec_epoch == date_now)

    @fcnName
    def testUnixToISO8601_1(self):
        """
            From unix time to external local ISO8601

            User needs to convert internal unix floating point
            seconds into an ISO 8601 string.
        """

        date_str = '2016-03-14T08:00:09.123456'
        # date --date='2016-03-14T08:00:09.123456' +%s.%6N

        # Generally obtain from time.time()
        secsNow = 1457967609.123456  # Unix time in seconds

        # Convert to ISO 8601
        secStr = utils.seconds_to_ISO8601(secsNow)
        self.failUnless(date_str == secStr)

    @fcnName
    def testTimeNowISO8601(self):
        """
            Can not really tell now() in a convenient testable manner.
            What to do? All this routine does in increase coverage.
        """
        secs_str = utils.time_now_ISO8601()
        print 'time_now_ISO8601=' + secs_str

    @fcnName
    def testISO8601ToSecs(self):
        """
            From ISO 8601 to unix seconds.

            App reads DATE field from log file and converts to
            internal unix floating point seconds in local time.
            """
        date_str = '2016-03-14T08:00:09.123456'
        # date --date='2016-03-14T08:00:09.123456' +%s.%6N

        # Generally obtain from time.time()
        secsNow = 1457967609.123456  # Unix time in seconds

        secs = utils.ISO8601_to_seconds(date_str)
        self.failUnless(secs == secsNow)

    @fcnName
    def testISO8601ToSecsErrors(self):
        """
            From ISO 8601 to unix seconds with errors in input

            App reads DATE field from log file and converts to
            internal unix floating point seconds in local time.
            """
        date_str = '2016-03-14T:11:00:09.123456'
        # date --date='2016-03-14T08:00:09.123456' +%s.%6N

        secs = utils.ISO8601_to_seconds(date_str)
        self.failUnless(secs is None)

    @fcnName
    def testTimeNow(self):
        """
            Simple test of time now.
        """
        the_time = utils.time_now()
        # Ignore the value as "the_time" always changes.
        self.failUnless(type(the_time) == type(1.0))

    @fcnName
    def testTimeNowISO8601(self):
        """
            Simple test of the time now in ISO8601 format
        """
        iso = utils.time_now_ISO8601()
        self.failUnless(type(iso) == type(''))

    @fcnName
    def testISOError(self):
        """
            Test error conditions.
            Pass in bogus ISO8601 formats. Should get None seconds
        """
        seconds = utils.ISO8601_to_seconds('2016-XX-01T00:00:00.000')
        self.failUnless(seconds is None)

        seconds = utils.ISO8601_to_seconds('2016-99-01T00:00:00.000')
        self.failUnless(seconds is None)

        seconds = utils.ISO8601_to_seconds('2016-03-01T30:00:00.000')
        self.failUnless(seconds is None)

        seconds = utils.ISO8601_to_seconds('2016-03-01X00:00:00.000')
        self.failUnless(seconds is None)

        seconds = utils.ISO8601_to_seconds('2016-03-01T00:61:00.000')
        self.failUnless(seconds is None)

        seconds = utils.ISO8601_to_seconds('2016-03-01T00:00:00.abc')
        self.failUnless(seconds is None)

        seconds = utils.ISO8601_to_seconds('2016-03-01T00:00:00')
        self.failUnless(seconds is None)

        seconds = utils.ISO8601_to_seconds('2016-03-01T00:00')
        self.failUnless(seconds is None)

        # No leading 0's - OK
        seconds = utils.ISO8601_to_seconds('2016-3-01T00:00:00.000')
        self.failUnless(seconds != None)

        # No leading 0's - OK
        seconds = utils.ISO8601_to_seconds('2016-3-1T0:0:0.0')
        self.failUnless(seconds != None)


class TestLogs2JSON(unittest.TestCase):
    # python -m unittest testLogging.TestLogs2JSON
    @fcnName
    def testLogs2JSON_HappyPath(self):
        print '\ntestLogs2JSON_HappyPath'
        testData = gen_happy_path()
        f = tempfile.NamedTemporaryFile(delete=True)
        f.write(testData)
        f.flush()

        try:
            lf = logFilter.LogFilterJSON({})
        except Exception as err:
            sys.stderr.write('Invalid configuration file:%s\n' % err)
            return 1

        json_data = lf.log_file_2_JSON(f.name)
        f.close()

        # Pretty print json
        py_internal = json.loads(json_data)

        """
        print json.dumps(py_internal, sort_keys=True, indent=4,
                separators=(',', ':'))
        """

        self.failUnless(py_internal[0]['level'] == 'DEBUG')
        self.failUnless(py_internal[0]['temp'] == '34.5')

        self.failUnless(py_internal[1]['level'] == 'CMD')
        self.failUnless(py_internal[1]['temp'] == '34.5')
        self.failUnless(py_internal[1]['item'] == 'Good Stuff')

    @fcnName
    def testLogs2JSON_Mixed(self):
        print '\ntestLogs2JSON_Missing'
        testData = gen_mixed_data()
        f = tempfile.NamedTemporaryFile(delete=True)
        f.write(testData)
        f.flush()

        # Filter out to WARNING and above.
        log_filters = logFilter.LogFilters.copy()
        log_filters['level'] = 'WARNING'
        try:
            lf = logFilter.LogFilterJSON(log_filters)
        except Exception as err:
            sys.stderr.write('Invalid configuration file:%s\n' % err)
            return 1
        json_data = lf.log_file_2_JSON(f.name)
        f.close()

        # Pretty print json
        json_internal = json.loads(json_data)
        """
        print json.dumps(json_internal, sort_keys=True, indent=4,
                separators=(',', ':'))
        """

        self.failUnless(json_internal[0]['level'] == 'ERROR')
        self.failUnless(json_internal[0]['device'] == 'water01')
        self.failUnless(json_internal[0]['state'] == 'LOW')

    @fcnName
    def testLogs2JSON_Bogus_filename(self):
        print '\ntestLogs2JSON_Bogus_filename'
        log_filters = logFilter.LogFilters.copy()
        try:
            lf = logFilter.LogFilterJSON(log_filters)
        except Exception as err:
            sys.stderr.write('Invalid configuration file:%s\n' % err)
            return 1
        result = lf.log_file_2_JSON('/QQQ/ZZZ.bogus')
        self.failUnless(result is None)


@fcnName
def countKeyValueJSON(json_struct, key, value):
    """
    Count the number of keys with specified value in json_struct.
    """
    count = 0
    for item in json_struct:
        if key in item:
            if item[key] == value:
                count += 1
    return count


class TestLogLevelsPriorities(unittest.TestCase):
    # python -m unittest testLogging.TestLogLevelsPriorities

    @fcnName
    def testCycles(self):
        """Test the cycle priority changes."""
        new_level = cycle_priority('DEBUG')
        self.failUnless(new_level == 'INFO')

        new_level = cycle_priority(new_level)
        self.failUnless(new_level == 'WARNING')

        new_level = cycle_priority(new_level)
        self.failUnless(new_level == 'CMD')

        new_level = cycle_priority(new_level)
        self.failUnless(new_level == 'ERROR')

        new_level = cycle_priority(new_level)
        self.failUnless(new_level == 'CRITICAL')

        new_level = cycle_priority(new_level)
        self.failUnless(new_level == 'DEBUG')

        # Garbage level name results in DEBUG
        new_level = cycle_priority('FOO_BAR')
        self.failUnless(new_level == 'DEBUG')

        # Garbage level name results in DEBUG

    @fcnName
    def testDebugLevel(self):
        debug_dict = utils.filter_priority('DEBUG')
        self.failUnless('DEBUG' in debug_dict)
        self.failUnless('CRITICAL' in debug_dict)

    @fcnName
    def testWarningLevel(self):
        debug_dict = utils.filter_priority('WARNING')
        self.failUnless('DEBUG' not in debug_dict)
        self.failUnless('WARNING' in debug_dict)
        self.failUnless('ERROR' in debug_dict)
        self.failUnless('CRITICAL' in debug_dict)

    @fcnName
    def testERRORLevel_0(self):
        debug_dict = utils.filter_priority('ERROR')
        self.failUnless('DEBUG' not in debug_dict)
        self.failUnless('INFO' not in debug_dict)
        self.failUnless('WARNING' not in debug_dict)
        self.failUnless('ERROR' in debug_dict)
        self.failUnless('CRITICAL' in debug_dict)

    @fcnName
    def testCRITICALLevel_0(self):
        debug_dict = utils.filter_priority('CRITICAL')
        self.failUnless('DEBUG' not in debug_dict)
        self.failUnless('INFO' not in debug_dict)
        self.failUnless('WARNING' not in debug_dict)
        self.failUnless('ERROR' not in debug_dict)
        self.failUnless('CRITICAL' in debug_dict)

    @fcnName
    def testErrorLevelJSON_1(self):
        print '\ntestErrorLevelJSON - filter to >= ERROR'
        testData = gen_happy_path()
        testData += gen_missing_data();

        f = tempfile.NamedTemporaryFile(delete=True)
        f.write(testData)
        f.flush()

        log_filters = logFilter.LogFilters.copy()
        log_filters['level'] = 'ERROR'
        try:
            lf = logFilter.LogFilterJSON(log_filters)
        except Exception as err:
            sys.stderr.write('Invalid configuration file:%s\n' % err)
            return
        json_data = lf.log_file_2_JSON(f.name)
        f.close()

        json_internal = json.loads(json_data)

        """
        # Pretty print json
        print json.dumps(json_internal, sort_keys=True, indent=4,
                separators=(',', ':'))
        """

        num_debug = countKeyValueJSON(json_internal, 'level', 'DEBUG')
        self.failUnless(num_debug == 0)

        num_info = countKeyValueJSON(json_internal, 'level', 'INFO')
        self.failUnless(num_info == 0)

        num_warnings = countKeyValueJSON(json_internal, 'level', 'WARNING')
        self.failUnless(num_warnings == 0)

        num_error = countKeyValueJSON(json_internal, 'level', 'ERROR')
        self.failUnless(num_error > 0)

        num_critical = countKeyValueJSON(json_internal, 'level', 'CRITICAL')
        self.failUnless(num_critical > 0)

        self.failUnless(json_internal[0]['level'] == 'ERROR')
        self.failUnless(json_internal[0]['temp'] == '999')

    @fcnName
    def testCRITICALLevel_BogusLevel(self):
        """Test an invalid logging level"""
        bogusDict = utils.filter_priority('BOGUS')
        self.failUnless(bogusDict == utils.LOG_LEVELS.keys())


class TestDirectoryService(unittest.TestCase):
    """
    Test the various functions of a directory
    service.
    """
    # python -m unittest testLogging.TestDirectoryService

    # Use standard ports to allow test to
    # proceed without worrying about existing
    # logCollectors or directory services..
    LOG_PORT = logConfig.get_logging_port()
    log_collector = None    # Process for log collector

    logConfig.DIR_PORT = logConfig.get_directory_port()
    DIR_SVC_PORT = logConfig.get_directory_port()
    dir_svc = None          # Process for directory services
    
    # True if logCollector was started, else False
    LOG_COLLECTOR_STARTED = False

    # True if directory services already runing, else False
    DIRECTORY_SERVICE_STARTED = False

    @fcnName
    def setUp(self):
        """
        Start logCollector and dirSvc only it they are not
        currently running.
        """
        # Setup log collector object
        # TBD: Does this track changing ports? TODO BUG?
        self.log_client = loggingClientTask.LoggingClientClass(platform.node())
        self.log_client.start()

        log_entry = 'Starting=TestDirectoryService,log_port=%d' % \
                TestDirectoryService.LOG_PORT
        self.log_client.info(log_entry)

        if listeningPort.is_listening(TestDirectoryService.LOG_PORT):
            sys.stdout.write('logCollector already running.\n')
        else:
            sys.stdout.write('--- TestDirectoryService: setUp() port %s\n' %
                    TestDirectoryService.LOG_PORT)
            self.StartLogServer()
            sys.stdout.write('--- TestDirectoryService: logCollector setUp()\n')
            time.sleep(1)

        if listeningPort.is_listening(TestDirectoryService.DIR_SVC_PORT):
            sys.stdout.write('dirSvc already running.\n')
        else:
            sys.stdout.write('--- TestDirectoryService: dirSvc setUp() port %s\n' %
                    TestDirectoryService.DIR_SVC_PORT)
            self.StartDirService()
            sys.stdout.write('--- setUp() finished.\n')
            time.sleep(1)

        self.testDirClient = dirClient.DirClient(in_config={
            'clear': True,
            'memory_filename': './dirSvc.data',
            'port': str(logConfig.DIR_PORT),
            'noisy': True,
            })

    @fcnName
    def tearDown(self):
        sys.stdout.write('--- Kill the dirSvc before the logCollector. ---\n')
        sys.stdout.write('--- TestDirectoryService: dirSvc tearDown()')
        self.KillDirService()
        sys.stdout.write('--- TestDirectoryService: logCollector tearDown()')
        self.KillLogServer()


    @fcnName
    def StartLogServer(self):
        """
        Spawn the log server in their own 
        separate procsses.
        """
        log_port = TestDirectoryService.LOG_PORT

        print '------ LOG Collector starting ------'

        abs_log_collector = os.path.abspath(logCollector.__file__)

        log_filename = os.path.abspath('./logs.log')
        print 'log_filename:%s' % log_filename

        # Remove existing log file
        # Other tests will test for append mode.
        if os.path.exists(log_filename) and \
                os.path.isfile(log_filename):
            os.remove(log_filename)

        log_port = TestDirectoryService.LOG_PORT
        args = ['python',
                abs_log_collector,
                '--noisy',      # Echo logs to console
                '--port=%s'     % str(log_port),
                '--log-file=%s' % log_filename,
               ]
        print 'starting logCollector:%s' % ' '.join(args)
        argv_collector = args
        TestDirectoryService.log_collector = subprocess.Popen(argv_collector)
        print ' '.join(argv_collector)
        print (bcolors.BGGREEN +
            ('log_collector pid: %d' % 
                TestDirectoryService.log_collector.pid) +
                bcolors.ENDC)
        TestDirectoryService.LOG_COLLECTOR_STARTED = True


    @fcnName
    def StartDirService(self):
        """
        Start the directory service. If already
        running, ignore this request.
        """
        dir_svc_port = TestDirectoryService.DIR_SVC_PORT
       
        print '------ Directory Service starting ------'

        abs_dir_service = os.path.abspath(dirSvc.__file__)

        argv_client = ['python',
                        abs_dir_service, 
                        '--port=%s' % str(dir_svc_port),
                        '--memory-file=%s' % './logsDirSvc.log',
                        '--clear',  # Wipe out old data
                       ]
        print 'starting dirSvc:' + ' '.join(argv_client)
        TestDirectoryService.dir_svc = subprocess.Popen(argv_client,
            stderr=subprocess.STDOUT)
        print (bcolors.BGGREEN +
                ('dirSvc pid: %d' % TestDirectoryService.dir_svc.pid) +
                bcolors.ENDC)

        # Allow some time to process.
        seconds_to_sleep = 2
        print '%d seconds to process subprocs' % seconds_to_sleep
        time.sleep(seconds_to_sleep)
        TestDirectoryService.DIRECTORY_SERVICE_STARTED = True

    @fcnName
    def KillLogServer(self):
        """
        Kill the log collector only if the process
        was not started by this process.
        """
        if TestDirectoryService.LOG_COLLECTOR_STARTED:
            print 'killing logCollector at pid %d' % \
                TestDirectoryService.log_collector.pid
            #os.kill(TestDirectoryService.log_collector.pid, signal.SIGKILL)
            self.log_client.info('@EXIT')
            time.sleep(1)
        else:
            print 'Not killing pre-existing logCollector'

    @fcnName
    def KillDirService(self):
        """
        Kill the directory service only if the process
        was not started by this process.
        """
        if TestDirectoryService.DIRECTORY_SERVICE_STARTED:
            print 'killing dirSvc at pid %d' % \
                TestDirectoryService.dir_svc.pid
            self.testDirClient.port_request('@EXIT')
        else:
            print 'Not killing pre-existing dirSvc'


    @fcnName
    def testDirSvc_0(self):

        print '---- TestDirectoryService.testDirSvc_0 - starting'

        dir_svc = TestDirectoryService.dir_svc
        log_col = TestDirectoryService.log_collector

        try:
            # Clear the directory
            print '%s' % self.testDirClient.port_request('@CLEAR')
            print 'dirNameBasePort: %s' % logConfig.getDirNameBasePort()

            # Add a few names to the directory
            req0 = self.testDirClient.port_request('testDirSvc')
            req1 = self.testDirClient.port_request('abc')
            req2 = self.testDirClient.port_request('xyz')

            print 'abc req1=%s' %  str(req1)
            print 'abc port_request(abc)=%s' % str(self.testDirClient.port_request('abc'))
            print '%s' % self.testDirClient.port_request('@DIR')
            req1_again = self.testDirClient.port_request('abc')
            self.failUnless(req1 == req1_again)

            # Delete name abc
            print '~abc ' + self.testDirClient.port_request('~abc')
            print 'after ~abc @DIR: %s' % self.testDirClient.port_request('@DIR')
            # Since 'abc' was deleted, a request yields a new port
            self.failUnless(req1 != self.testDirClient.port_request('abc'))

        except Exception as err:
            sys.stderr.write(str(err) + '\n')
            traceback.print_stack()
            print '-----------'
            traceback.print_exc()


if __name__ == '__main__':

    # Standard way to initialize for logging
    apiLoggerInit.loggerInit()
    #ch = logging.StreamHandler(sys.stdout)
    #log = logging.getLogger('')
    #log.addHandler(ch)

    logging.info('Unit test started')
    #suite = unittest.TestLoader().loadTestsFromTestCase(RunTests)
    #unittest.TextTestRunner(verbosity=2).run(suite)
    unittest.main()


