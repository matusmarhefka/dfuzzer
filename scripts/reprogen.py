#!/usr/bin/env python3

import argparse
import fileinput
import sys
import os

def dbus_send(bus, name, method, calls):
    print(calls)

def main(bus, process, name_for_stdin, results_filter, files):
    if name_for_stdin is None and '-' in files:
        return False
    for line in fileinput.input(files):
        parsed_line = line.strip().split(';');
        if parsed_line[-1] not in results_filter:
            continue
        process(bus, name_for_stdin if fileinput.isstdin()
                else os.path.basename(fileinput.filename()), parsed_line[0],
                [parsed_line[i:i+1] for i in range(1, len(parsed_line),2)])
    return True

if __name__ == '__main__':
    functions = {'dbus-send': dbus_send}
    p = argparse.ArgumentParser(
            description='Generate reproduction code from dfuzzer logs')
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument('--system',  action='store_true', help='Use system bus')
    g.add_argument('--session', action='store_true', help='Use session bus')
    p.add_argument('-t', '--target', choices=['dbus-send'],
            default='dbus-send', help='Target language/library')
    p.add_argument('-n', '--name', type=str, default=None,
            help='Name of the bus to use when taking input from stdin')
    p.add_argument('-f', '--filter', type=str, choices=['Crash','Success',
        'Command execution error'], default='[Crash]', nargs='+',help=
        'List of result types for which reproduction code will be generated')
    p.add_argument('files', type=str, nargs='+',
            help='Paths to log files ("-" for stdin)')
    args = p.parse_args()
    if not main('system' if args.system else 'session', functions[args.target],
            args.name, args.filter, args.files):
        p.print_usage(file=sys.stderr)
        print('{}: When taking input from stdin, you must specify bus name'
                .format(sys.argv[0]))
        exit(2)
