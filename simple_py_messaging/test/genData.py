#!/bin/env python
"""
    Prog to create test log data.
"""
import sys
import utils


def genHappyPath(sep_char=utils.PAYLOAD_CONNECTOR,
        key_val_sep=utils.KEY_VALUE_SEPARATOR):
    """
    Generate happy path data with  payload separator
    and key/value separator chars.
    """
    test_data = ''
    test_data += '2016-03-10T11:00:39.697\tDEBUG\ta=b&temp=34.5&item=Good Stuff\n'
    test_data += '2016-03-10T11:01:39.697\tWARNING\ta=b&temp=74.5&item=cool\n'
    test_data += '2016-03-10T11:02:39.697\tDEBUG\ta=b&temp=82.5&item=funny\n'
    test_data += '2016-03-10T11:03:39.697\tCRITICAL\ta=b&temp=99.34.5&item=Stupid Stuff'
    test_data = test_data.replace('=', key_val_sep)
    test_data = test_data.replace('&', sep_char)
    return test_data


def genMissingData(sep_char=utils.PAYLOAD_CONNECTOR,
        key_val_sep=utils.KEY_VALUE_SEPARATOR):
    """
    Generate data with some emtpy values
    and key/value separator chars.
    """
    test_data = ''
    # Good line
    test_data += '2016-03-10T11:00:39.697\tDEBUG\ta=b&temp=&item=Good Stuff\n'
    # Doubled &&
    test_data += '2016-03-10T11:01:39.697\tWARNING\ta=b&&item=cool\n'
    # key=value=value problem(?)
    test_data += '2016-03-10T11:02:39.697\tDEBUG\ta=b=c&temp=82.5&item=funny\n'
    test_data += '2016-03-10T11:03:39.697\tCRITICAL\ta=&temp=99.34.5&item=Stupid Stuff\n'
    # & at end of line
    test_data += '2016-03-10T11:03:39.697\tCRITICAL\t=b&temp=99.34.5&item=Stupid Stuff&\n'
    # duplicated keyword "temp"
    test_data += '2016-03-10T11:03:39.697\tCRITICAL\ta=b&temp=99.34.5&temp=999.999&item=Stupid Stuff&\n'
    test_data = test_data.replace('=', key_val_sep)
    test_data = test_data.replace('&', sep_char)
    return test_data


def genMixedData(sep_char=utils.PAYLOAD_CONNECTOR,
        key_val_sep=utils.KEY_VALUE_SEPARATOR):
    """
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

    test_data = ''
    # A periodic reading of water and temperature from several instruments
    test_data += '2016-03-14T08:00:00.000\tINFO\tdevice=water01&state=OFF&host=hydro1\n'
    test_data += '2016-03-14T08:00:00.000\tINFO\tdevice=tempIN&temp=72.3&host=hydro1\n'
    test_data += '2016-03-14T08:00:00.000\tINFO\tdevice=tempOUT&temp=69.2&host=hydro1\n'
    # Water level has gone too low
    test_data += '2016-03-14T08:00:07.325\tERROR\tdevice=water01&state=LOW&host=hydro1\n'
    # Pump started to raise water level. A command was sent
    # pump01 request to start.
    test_data += '2016-03-14T08:00:09.876\tINFO\tcmd=req&tag=xyz=pump01&state=ON&host=hydro1\n'
    # Command started, remote sends reply. Note use of "tag"
    test_data += '2016-03-14T08:00:09.876\tINFO\tcmd=rep&tag=xyz&host=hydro1\n'
    # Water level back to normal and turn pump1 off.
    test_data += '2016-03-14T08:05:05.325\tINFO\tdevice=water01&state=OK&host=hydro1\n'
    # Pump turns off
    test_data += '2016-03-14T08:05:15.876\tINFO\tcmd=req&tag=abc&pump01=OFF&host=hydro1\n'
    # Pump starting to off state.
    test_data += '2016-03-14T08:05:15.876\tINFO\tcmd=rep&tag=abc&host=hydro1\n'
    # Periodic temperature readings
    # More likely would be one reading per device.
    test_data += '2016-03-14T08:10:00.000\tINFO\tdevice=water01&state=OK&pump01=OFF&temp04=70.1&temp03=69.0&host=hydro1\n'
    test_data += '2016-03-14T08:10:01.000\tINFO\tdevice=pump01&device=temp04&temp=70.1&temp03=69.0&host=hydro1\n'
    test_data += '2016-03-14T08:10:02.000\tINFO\tdevice=pump01&device=temp03&temp=69.0&host=hydro1\n'
    # pump03, pump04 and fan02 have suddenly stopped working! Notice UNKNOWN state.
    test_data += '2016-03-14T08:10:04.000\tERROR\tdevice=pump03&state=UNKNOWN&host=hydro1\n'
    test_data += '2016-03-14T08:10:04.121\tERROR\tdevice=fan02&state=UNKNOWN&host=hydro1\n'
    test_data += '2016-03-14T08:10:04.425\tERROR\tdevice=pump04&state=UNKNOWN&host=hydro1\n'
    #
    # BROKEN - FIXME - need one device per request! "circulation" is a macro
    # Normal circulation started on command. Notice multiple devices turned on.
    test_data += '2016-03-14T08:12:14.734\tINFO\tcmd=req&tag=circulation&water01=OK&pump01=ON&circulation=ON&host=hydro1\n'
    # Circulation started
    test_data += '2016-03-14T08:12:14.734\tINFO\tcmd=rep&tag=circulation&&host=hydro1\n'
    # Normal circulation finished. Simply status indicating state of devices.
    test_data += '2016-03-14T08:22:14.739\tINFO\twater01=OK&pump01=OFF&circulation=OFF&host=hydro1\n'

    test_data = test_data.replace('=', key_val_sep)
    test_data = test_data.replace('&', sep_char)
    return test_data


baseFilter = """{
    'end': '9999-01-01T00:00.000', # HUGE date for everything
    'in_file': 'base.data',
    'level': 'ERROR',
    #'out_file': None,      # Output to stdout
    'start': 0,         # Start of epoch
    }"""

csvFilter = """{
    'end': '9999-01-01T00:00.000', # HUGE date for everything
    'in_file': 'csv.data',
    'level': 'ERROR',
    #'out_file': None,      # Output to stdout
    'out_format': 'CSV',    # CSV formatted output
    'start': None,
    }"""

datedFilter = """{
    # Gives start and end dates for the "mixed" genData logs
    # Several devices has suddenly stopped working between the
    # start and end times. Problem in the "mixed" logs
    'start': '2016-03-14T08:00:00.000',
    'in_file': 'mixed.data',
    'level': 'ERROR',
    #'out_file': None,      # Output to stdout
    'out_format': 'JSON',   # default JSON formatted outupt
    }"""


filters = {
    'baseFilter': baseFilter,
    'csvFilter': csvFilter,
    'datedFilter': datedFilter,
}


def genConfigs(filter_name):
    """Given a filter name, output the code for that filter."""
    if filter_name not in filters.keys():
        sys.stderr.write('Unknown config filter request: "%s"\n' % filter_name)
        sys.stderr.write('Please provide a proper filter name\n')
        sys.stderr.write('Valid filter names: %s\n' % str(filters.keys()))
        usage()

    filter_code = filters[filter_name]
    return filter_code


def usage():
    """Print help message and exit."""
    help_str = """
Usage: ./genData [--happy] [--missing] [--mixed] [--configs=<filter_name>]
Generate various data files.
No options writes all logs to stdout.
No options runs as if --happy, --missing and --mixed were all present.

    --help    => This message
    --happy   => Logs common to status readings.
    --missing => Logs similar to "happy" but with deliberate errors
    --mixed   => Logs more common to SCADA logs with a single device
                 per logs containing both commands and readings.
    --config=name  => Outputs multiple files with examples of
                 configuration files. These files provide
                 a start to configuring logFilterApp.
                Valid config names:
                    baseFilter  = General happy base filtering. JSON output.
                    csvFilter   = CSV file output of everything.
                    datedFilter = A date span with devices dropping out.
    """
    sys.stderr.write(help_str)
    sys.exit(1)


def main():
    import getopt

    try:
        opts, args = getopt.gnu_getopt(
                sys.argv[1:], '',
                ['help',
                 'happy',
                 'missing',
                 'mixed',
                 'config='
                ])
    except getopt.GetoptError as err:
        sys.stderr.write(str(err) + '\n')
        usage()

    logs_dumped = False
    for opt, arg in opts:
        if opt in ['--help']:
            usage()
        elif opt in ['--happy']:
            print genHappyPath()
            logs_dumped = True
            continue
        elif opt in ['--missing']:
            print genMissingData()
            logs_dumped = True
            continue
        elif opt in ['--mixed']:
            print genMixedData()
            logs_dumped = True
            continue
        elif opt in ['--config']:
            print genConfigs(arg)
            logs_dumped = True      # Don't dump any logs
            continue
        else:
            sys.stderr.write('Unknown option:' + opt + '\n')
            usage()

    if not logs_dumped:
        print genHappyPath()
        print genMissingData()
        print genMixedData()

    return 0

if __name__ == '__main__':
    main()
