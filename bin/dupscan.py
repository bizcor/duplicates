#!/usr/bin/python

import argparse
import hashlib
import os
import stat
import sys

from platform import node
from stat import S_ISREG, S_ISLNK

ASCII_NUL = chr(0)


def md5_for_file(path):
    ''' return md5 hex digest for given file'''
    try:
        md5 = hashlib.md5()
        with open(path, 'rb') as f:
            try:
                data = f.read()
            except Exception as e:
                print "{}: could not read file: got {}".format(path, e)
            md5.update(data)
    except Exception as e:
        print "before return true loop: {}: got {}".format(path, e)
    return md5.hexdigest()


def file_info(thishost, directory, basename, field_separator=ASCII_NUL):
    '''return a string joined by field_separator of the hostname,
       file's md5 hash, filesystem device number, inode, number of hard links,
       size in bytes, and path, unless the file is not a regular file or is
       a symlink'''
    file_path = os.path.join(directory, basename)
    st = os.lstat(file_path)

    mode = st.st_mode
    if not S_ISREG(mode) or S_ISLNK(mode):
        return

    with open(file_path, 'rb') as f:
        md5sum = md5_for_file(file_path)

    return field_separator.join([thishost,
                                md5sum,
                                str(st.st_dev),
                                str(st.st_ino),
                                str(st.st_nlink),
                                str(st.st_size),
                                file_path])


def getargs():
    '''parse command line args'''
    description = (
        'scan files in a tree and print to stdout a line of information about'
        ' each regular file'
    )
    parser = argparse.ArgumentParser(description=description)

    help = ('Specify the root of the filesystem tree to be processed.'
            "  The default is the current directory.")
    parser.add_argument('-d',
                        '--start-directory',
                        default='.',
                        help=help)

    help = ('Specify the string to use as a field separator in output.'
            '  The default is the ascii nul character.')
    parser.add_argument('-s',
                        '--field-separator',
                        default=ASCII_NUL,
                        help=help)
    return parser.parse_args()


def main():
    args = getargs()

    start_directory = args.start_directory.rstrip('/')
    field_separator = args.field_separator

    thishost = node()
    if thishost == '':
        thishost = '[UNKNOWN]'

    # recursively process each file in the tree rooted at the start directory
    for directory_path, directory_names, file_names \
            in os.walk(start_directory):
        for file_name in file_names:
            path = '{}/{}'.format(directory_path, file_name)

            mode = os.lstat(path).st_mode
            if stat.S_ISLNK(mode) or not stat.S_ISREG(mode):
                continue

            print file_info(thishost,
                            directory_path,
                            file_name,
                            field_separator)

if __name__ == "__main__":
    main()
    sys.exit(0)
