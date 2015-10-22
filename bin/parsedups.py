#!/usr/bin/python

import argparse
import os
import pprint
import string
import sys

ASCII_NUL = chr(0)

HOSTNAME = 0
MD5SUM = 1
FSDEV = 2
INODE = 3
NLINKS = 4
SIZE = 5
PATH = 6

BYTE = 1
KB = 1024 * BYTE
MB = 1024 * KB
GB = 1024 * MB

DEFAULT_SIZE = 0

EXPECTED_NUMBER_OF_DATA_FIELDS = 7


def print_scanned_data(dupdata):
    ''' this may or may not currently be called by anything in this
        file.  it is useful for debugging.  it prints the scanned data,
        each field to a line
    '''
    for host in dupdata:
        print "host => {}".format(host)
        for fsdev in dupdata[host]:
            print "  fsdev => {}".format(fsdev)
            for md5sum in dupdata[host][fsdev]:
                print "    md5sum => {}".format(md5sum)
                print "      size => {}".format(dupdata[host]
                                                       [fsdev]
                                                       [md5sum]
                                                       ['size'])
                for inode in dupdata[host][fsdev][md5sum]['inodes']:
                    print "      inode => {}".format(inode)
                    for path in dupdata[host][fsdev][md5sum]['inodes'][inode]:
                        print "        path => {}".format(path)


def parse_data(files, field_separator):
    ''' parse the given files, using the field_separator as the character
        separating the data fields in each line of data.  return a dict
        of dicts of dicts... data structure containing all of the parsed
        data.  see comments below for the layout of the data.
    '''
    if field_separator in string.printable:
        printable_separator = field_separator
    else:
        separator_ord = ord(field_separator)
        printable_separator = "ord({})".format(separator_ord)

    dupdata = {}

    for file in files:
        line_number = 0
        with open(file, 'rb') as f:
            for line in f:
                line_number += 1
                line = line.rstrip('\n')
                if line == 'None':
                    continue

                fields = line.split(field_separator)
                if len(fields) != EXPECTED_NUMBER_OF_DATA_FIELDS:
                    sys.stderr.write(
                        "skipping line; field_separator => '{}'; cannot parse:"
                        " line {}: {}\n".format(printable_separator,
                                                line_number,
                                                line))
                    continue

                hostname = fields[HOSTNAME]
                try:
                    md5sum = fields[MD5SUM]
                except Exception as e:
                    sys.stderr.write(
                        "skipping file '{}'; {}; fields => {}".format(file,
                                                                      e,
                                                                      fields))
                    continue

                fsdev = fields[FSDEV]
                inode = fields[INODE]
                nlinks = int(fields[NLINKS])
                size = int(fields[SIZE])
                path = fields[PATH]

                # dupdata => {
                #   hostname => {
                #     fsdev => {
                #       md5sum => {
                #         size => $size,
                #         'inodes' => {
                #           inode => {
                #             path => {
                #              'nlinks' => nlinks,
                #             }
                #           }
                #         }
                #       }
                #     }
                #   },
                #   ...
                # }

                if hostname not in dupdata:
                    dupdata[hostname] = {}
                if fsdev not in dupdata[hostname]:
                    dupdata[hostname][fsdev] = {}
                if md5sum not in dupdata[hostname][fsdev]:
                    dupdata[hostname][fsdev][md5sum] = {}
                if 'inodes' not in dupdata[hostname][fsdev][md5sum]:
                    dupdata[hostname][fsdev][md5sum]['inodes'] = {}
                if inode not in dupdata[hostname][fsdev][md5sum]['inodes']:
                    dupdata[hostname][fsdev][md5sum]['inodes'][inode] = {}
                if path not in dupdata[
                                hostname][fsdev][md5sum]['inodes'][inode]:
                    dupdata[hostname][fsdev][md5sum]['inodes'][inode][path] \
                        = {}

                dupdata[hostname][fsdev][md5sum]['size'] = size
                dupdata[hostname][fsdev][md5sum]['inodes'][inode][path] \
                    = {'nlinks': nlinks}
    return dupdata


def process_data(dupdata, minimum_size=0, list_fields=False):
    ''' either print duplicates that are found (list_fields=False) or just
        print data on all of the files (list_fields=True).  in either case,
        print data only on files at least as big as minimum_size (in bytes).
    '''
    if list_fields:
        NUMBER_OF_INODES_TO_PRINT = 0
    else:
        NUMBER_OF_INODES_TO_PRINT = 2
    for host in dupdata:
        for fsdev in dupdata[host]:
            for md5sum in dupdata[host][fsdev]:
                number_of_inodes = len(dupdata[host][fsdev][md5sum]['inodes'])
                if number_of_inodes >= NUMBER_OF_INODES_TO_PRINT:
                    size = dupdata[host][fsdev][md5sum]['size']
                    if size >= minimum_size:
                        for inode in dupdata[host][fsdev][md5sum]['inodes']:
                            for path in dupdata[
                                    host][fsdev][md5sum]['inodes'][inode]:
                                print "{}  {}  {:10d}  {:>10s}  {}".format(
                                    host, md5sum, size, inode, path)
    return


def parse_args():
    '''parse command line args'''
    description = ('scan files in a tree and print a line of information'
                   ' about each regular file')
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument('--file',
                        '-f',
                        action='append',
                        required=True,
                        help='File from which to read data')

    help = ('Specify the string to use as a field separator in output.'
            '  The default is the ascii nul character.')
    parser.add_argument('--field-separator',
                        '-s',
                        default=ASCII_NUL,
                        help=help)

    help = ('Specify the size (in bytes) a file must be to be considered for'
            ' processing.  The default size is {}.'.format(DEFAULT_SIZE))
    parser.add_argument('--size',
                        '-S',
                        default=DEFAULT_SIZE,
                        help=help)

    help = '''Print data for all files whether or not they're duplicates'''
    parser.add_argument('--list-fields', '-l', action="store_true",
                        dest='list_fields',
                        default=False,
                        help=help)

    args = parser.parse_args()

    files = args.file
    field_separator = args.field_separator
    list_fields = args.list_fields
    size = args.size

    return {
                'field_separator': field_separator,
                'files': files,
                'list_fields': list_fields,
                'size': int(size),
           }


def main():
    options = parse_args()
    sys.stderr.write("args => {}\n".format(options))

    field_separator, files, list_fields, size \
        = options['field_separator'], options['files'], \
        options['list_fields'], options['size']

    dupdata = parse_data(files, field_separator)

    process_data(dupdata, size, list_fields)


if __name__ == "__main__":
    main()
    sys.exit(0)
