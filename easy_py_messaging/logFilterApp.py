#!/bin/env python
import sys
import logFilter


def usage():
    sys.stderr.write('logFilterApp [--config=config_file]\n' +
            '\t[--out-file=outfile]\n[--in-file=infile]\n' +
            '\t[--start=<ISO8601 start date>]\n[--end=>iso8601 end date]\n' +
            '\t[--JSON|--CSV]\n[--help]\n' +
            '\t[--level=<level name>]\n')
    sys.stderr.write('--config=config_file   # Take parameters from config file\n')
    sys.stderr.write('--out-file=output file # output goes here. Default: stdout\n')
    sys.stderr.write('--in-file=input file   # input read from here. Default: stdin\n')
    sys.stderr.write('--start=<iso8601 start date> # start date iso formatted\n')
    sys.stderr.write('--end=<iso8601 end date>     # end date   iso formatted\n')
    sys.stderr.write('     If start with no end, continue to present time.\n')
    sys.stderr.write('--level=LEVEL   # Handle only from LEVEL up.\n')
    sys.stderr.write('     DEBUG,CMD,INFO,WARNING,ERROR,CRITICAL are the levels.\n')
    sys.stderr.write('--JSON          # output format is JSON (default)\n')
    sys.stderr.write('--CSV           # Output format is CSV\n')
    sys.stderr.write('--help          # This message\n')
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

    try:
        csv_filter = logFilter.LogFilterCSV(params, filter_fcn=filter_CSV)
    except Exception as err:
        sys.stderr.write('Invalid configuration file:%s\n' % err)
        usage()

    in_fh = params['in_file_handle']
    out_fh = params['out_file_handle']

    in_lines = in_fh.read()
    lines = in_lines.split('\n')
    if len(lines) <= 1:
        return
    if lines[-1] == '':     # If file termed in '\n', remove last entry
        del lines[-1]

    # Process header line
    header_line = lines[0]
    csv = csv_filter.parse_log_entry(header_line)
    if csv is not None:
        out_fh.write(csv_filter.log_keys() + '\n')
    else:
        sys.stderr.write('ERROR: Invalid header line ignored for CSV file:"%s"' %
            header_line)

    line_number = 0
    for line in lines:
        line_number += 1
        line = line.strip('\n')
        csv = csv_filter.parse_log_entry(line)
        if csv is not None:
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

    try:
        lf = logFilter.LogFilterJSON(params, filter_fcn=filter_JSON)
    except Exception as err:
        sys.stderr.write('Invalid configuration: %s\n' % err)
        usage()
    in_fh = params['in_file_handle']
    out_fh = params['out_file_handle']
    json_data = lf.log_file_2_JSON_handler(in_fh)
    out_fh.write(json_data)
    out_fh.write('\n')
    out_fh.flush()
    out_fh.close()
    params['out_filter_handle'] = None


def main():
    import getopt

    try:
        opts, _ = getopt.gnu_getopt(
            sys.argv[1:], 'cioeslJCh',
            ['config=',     # config file
             'in-file=',    # input log file.
             'out-file=',   # Output file
             'end=',        # iso8601 end date
             'start=',      # iso8601 start date
             'level=',      # filter from this level up
             'JSON',        # Output is JSON (default)
             'CSV',         # Output is CSV
             'help',        # help message
            ]
        )
    except getopt.GetoptError as err:
        sys.stderr.write(str(err) + '\n')
        usage()

    params = logFilter.LogFilters

    for opt, arg in opts:
        if opt in ['-h', '--help']:
            usage()

        elif opt in ['--config']:
            try:
                # The config file MUST be read now as further
                # command line args may overwrite settings.
                try:
                    conf_fh = open(arg, 'r')
                except IOError as err:
                    sys.stderr.write('ERROR:%s' % str(err))
                    usage()
                config_lines = conf_fh.read()
                # Evaluate the contents of config_lines
                params = eval(config_lines)
            except Exception as err:
                sys.stderr.write(str(err))
                usage()
        elif opt in ['--level']:
            params['level'] = arg
            continue

        elif opt in ['-J', '--JSON']:
            params['out_format'] = 'JSON'
            continue

        elif opt in ['-C', '--CSV']:
            params['out_format'] = 'CSV'
            continue

        elif opt in ['--in-file']:
            params['in_file'] = arg
            continue

        elif opt in ['--out-file']:
            params['out_file'] = arg
            continue

        elif opt in ['--start']:
            params['start'] = arg
            continue

        elif opt in ['--end']:
            params['end'] = arg
            continue

        else:
            # Should never happen. getopt should catch this!
            sys.stderr.write('Unknown option:' + opt + '\n')
            usage()

    if 'out_format' not in params:
        params['out_format'] = 'JSON'
    if params['out_format'] == 'CSV':
        run_CSV(params)
    elif params['out_format'] == 'JSON':
        run_JSON(params)
    else:   # Should never happen. getopt should catch this.
        sys.stderr('Invalid output option: "%s"\n' % params['out_format'])
        usage()


if __name__ == '__main__':
    main()

