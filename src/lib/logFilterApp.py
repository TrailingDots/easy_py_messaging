#!/bin/env python
import sys
sys.path.append('./')
sys.path.append('../lib')
import utils
import logFilter


def usage():
    sys.stderr.write('logs2JSON [--out-file=outfile] [--in-file=infile]\n' + \
            '\t[--start=<ISO8601 start date>] [--end=>iso8601 end date]\n' + \
            '\t[--JSON] [--CSV] [--help]\n' + \
            '\t[--level=<level name>]')
    sys.stderr.write('--out-file=output file # output goes here\n')
    sys.stderr.write('--in-file=input file   # output goes here\n')
    sys.stderr.write('--start=<iso8601 start date> # start date iso formatted\n')
    sys.stderr.write('--end=<iso8601 end date>     # end date   iso formatted\n')
    sys.stderr.write('     If start with no end, continue to present time.\n')
    sys.stderr.write('--level=LEVEL      # Handle only from LEVEL up.\n')
    sys.stderr.write('     DEBUG,CMD,INFO,WARNING,ERROR,CRITICAL are the levels.\n')
    sys.stderr.write('--JSON             # output format is JSON (default)\n')
    sys.stderr.write('--CSV              # Output format is CSV\n')
    sys.stderr.write('--help             # This message\n')
    sys.exit(1)


def run_CSV(params):
    """
    Output format is CSV.
    Write a header line with a list of keywords from the 
    first line of input.
    Then write the data lines with just the values.
    """
    def filter_CSV(log_dict, line_number):
        """
        This function provides a simple pass-thru. In the next
        release expands into a more useful operation.

        filter_CSV takes a single line of an input log entry for CSV processing.
        The parsed log_entry gets passed as a dictionary.  If the data
        should be included, return the rearranged dictionary.  Items in
        log_dict may be deleted, modified, etc.

        If the data should be ignored, return None.
        """
        return log_dict

    in_fh = params['in_file_handle']
    out_fh = params['out_file_handle']

    csv_filter = logFilter.LogFilterCSV(params, filter_fcn=filter_CSV)

    in_lines = in_fh.read()
    lines = in_lines.split('\n')
    if len(lines) <= 1:
        return
    if lines[-1] == '':     # If file termed in '\n', remove last entry
        del lines[-1]

    # Process header line
    header_line = lines[0]
    csv = csv_filter.parse_log_entry(header_line)
    if csv != None:
        out_fh.write(csv_filter.log_keys() + '\n')
    else:
        # TODO FIXME Suppose the 1st line gets filtered out?
        sys.stderr.write('ERROR: Invalid header line ignored for CSV file:"%s"' % \
                header_line)

    line_number = 0
    for line in lines:
        line_number += 1
        line = line.strip('\n')
        csv = csv_filter.parse_log_entry(line)
        if csv != None:
            # Input line is acceptable
            # If csv == None, csv_filter eliminated the line.
            out_fh.write(csv_filter.log_data() + '\n')
    out_fh.write('\n')
    out_fh.flush()
    out_fh.close()
    params['out_filter_handle'] = None


def run_JSON(params):
    """
    Output format is JSON.
    The JSON contains an array of objects.
    Each object expresses a single line of data.
    """
    in_fh = params['in_file_handle']
    out_fh = params['out_file_handle']

    def filter_JSON(log_entry_dict, line_number):
        """An example: only host=hydro1 gets returned.
        Later this gets expanded!
        if 'host' in log_entry_dict:
            if log_entry_dict['host'] == 'hydro1':
                return log_entry_dict
        else:
            return None
        """
        # For now pass everything
        return log_entry_dict

    lf = logFilter.LogFilterJSON(params, filter_fcn=filter_JSON)
    json_data = lf.log_file_2_JSON_handler(in_fh)
    out_fh.write(json_data)
    out_fh.write('\n')
    out_fh.flush()
    out_fh.close()
    params['out_filter_handle'] = None


def main():
    import getopt

    try:
        opts, args = getopt.gnu_getopt(
            sys.argv[1:], '',
            ['config=',     # config file
             'in-file=',    # input log file.
             'out-file=',   # Output file
             'end-date=',   # iso8601 end date
             'start-date=', # iso8601 start date
             'level=',      # filter from this level up
             'JSON',        # Output is JSON (default)
             'CSV',         # Output is CSV
             'help',        # help message
            ]
        )
    except getopt.GetoptError as err:
        sys.stderr.write( str(err) + '\n' )
        usage()

    params = logFilter.LogFilters;

    for opt, arg in opts:
        if opt in ['--help']:
            usage()

        elif opt in ['--config']:
            try:
                conf_fh = open(arg, 'r')
                config_lines = conf_fh.read()
                # Evaluate the contents of config_lines
                params = eval(config_lines)
            except Exception as err:
                sys.stderr.write(str(err))
                usage()
        elif opt in ['--level']:
            if arg not in utils.LOG_LEVELS:
                sys.stderr.write(('%s: Invalid log level. '
                    'Use: DEBUG,CMD,INFO,WARNING,ERROR,CRITICAL\n') % arg)
                usage()
            params['level'] = arg
            continue

        elif opt in ['--JSON']:
            params['out_format'] = 'JSON'
            continue

        elif opt in ['--CSV']:
            params['out_format'] = 'CSV'
            continue

        elif opt in ['--in-file']:
            params['in_file'] = arg
            continue

        elif opt in ['--out-file']:
            params['out_file'] = arg
            continue

        elif opt in ['--start-date']:
            sd = utils.ISO8601ToSeconds(arg)
            if sd == None:
                sys.stderr.write('--start-date:"%s" is not a valid ISO8601 date' % arg)
                usage()
            params['start_secs'] = sd
            params['start'] = arg
            continue

        elif opt in ['--end-date']:
            sd = utils.ISO8601ToSeconds(arg)
            if sd == None:
                sys.stderr.write('--end-date:"%s" is not a valid ISO8601 date' % arg)
                usage()
            params['end_secs'] = sd
            params['end'] = arg
            continue

        else:
            # Should never happen. getopt should catch this!
            sys.stderr.write('Unknown option:' + opt + '\n')
            usage()

    # If a start date with no end date, make the end date now.
    if 'end' not in params.keys():
        now_secs = utils.time_now()
        params['end_secs'] = now_secs
        params['end'] = utils.secondsToISO8601(now_secs)

    # Verify input and output files.
    in_file = params.get('in_file', None)
    if in_file == None:
        params['in_file_handle'] = sys.stdin
        params['in_file'] = 'sys.stdin'
    else:
        try:
            fh = open(in_file, 'r')
        except IOError as err:
            sys.stderr.write('--in-file: "%s": %s\n' % (in_file, str(err)))
            usage()
        params['in_file_handle'] = fh

    out_file = params.get('out_file', None)
    if out_file == None:
        params['out_file_handle'] = sys.stdout
        params['out_file'] = 'sys.stdout'
    else:
        try:
            fh = open(out_file, 'w')
        except IOError as err:
            sys.stderr.write('--out-file: "%s": %s\n' % (out_file, str(err)))
            usage()
        params['out_file_handle'] = fh

    if params['out_format'] == 'CSV':
        run_CSV(params)
    elif params['out_format'] == 'JSON':
        run_JSON(params)
    else:   # Should never happen. getopt should catch this.
        sys.stderr('Invalid output option: "%s"\n' % params['out_format'])
        usage()


if __name__ == '__main__':
    main()


