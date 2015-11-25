# duplicates

Python code to detect duplicate files.  My definition of duplicates is two files that do not share an inode, but have the same md5 checksum.
Duplicates can be detected within filesystems or across filesystems, on the same host, or across hosts.  I wrote the code to identify multiple locations of large data files so I could delete the duplicates and reclaim filesystem space.

The idea is to scan one or more filesystem trees and then parse the data, reporting on which files are duplicates, as defined above.

## Detecting duplicates

**dupscan.py** scans a filesystem tree rooted at the given directory, or rooted at the current working directory if no directory is specified.  It traverses the tree processing regular files.  For each such file it encounters, it writes to stdout a line of data that is formatted as follows.  I show the string ' : ' as a field delimiter here for readability, but the default delimiter is an ascii nul character (\0).

*HOSTNAME : MD5_CHECKSUM : FILESYSTEM_DEVICE_NUMBER : INODE_NUMBER : SIZE_IN_BYTES : PATH*

```
usage: dupscan.py [-h] [-d START_DIRECTORY] [-s FIELD_SEPARATOR]

scan files in a tree and print to stdout a line of information about each regular file

optional arguments:
  -h, --help            show this help message and exit
  -d START_DIRECTORY, --start-directory START_DIRECTORY
                        Specify the root of the filesystem tree to be
                        processed. The default is the current directory.
  -s FIELD_SEPARATOR, --field-separator FIELD_SEPARATOR
                        Specify the string to use as a field separator in
                        output. The default is the ascii nul character.
```

**parsedups.py** takes input from stdin or files or both.  It expects each line to be of the format of lines created by dupscan.py.  It reads the data for all input sources into memory and outputs information on any duplicate files it detects.

```
usage: parsedups.py [-h] [--file FILE] [--field-separator FIELD_SEPARATOR]
                    [--size SIZE] [--list-fields]

scan files in a tree and print a line of information about each regular file

optional arguments:
  -h, --help            show this help message and exit
  --file FILE, -f FILE  File(s) from which to read data. The default is to
                        read from stdin. To mix stdin and files, specify stdin
                        as a file called "__stdin__". For example: --file
                        __stdin__ --file my-file --file my-other-file
  --field-separator FIELD_SEPARATOR, -s FIELD_SEPARATOR
                        Specify the string to use as a field separator in
                        output. The default is the ascii nul character.
  --size SIZE, -S SIZE  Specify the size (in bytes) a file must be to be
                        considered for processing. The default size is 0.
  --list-fields, -l     Print data for all files whether or not they're
                        duplicates
```

###Examples:

Let's process a random venv directory for some examples:

```
$ dupscan.py --start-directory venv --field-separator : | wc -l
     698

$ dupscan.py --start-directory venv --field-separator : | tail
manna.local:97c5c7dbc7907fcc8a0aa689ee9afb0b:16777220:18420293:1:15233:venv/lib/python2.7/site-packages/wheel/tool/__init__.pyc
manna.local:5dc3482b782c00465107147dccf06381:16777220:18420295:1:8064:venv/lib/python2.7/site-packages/wheel-0.24.0.dist-info/DESCRIPTION.rst
manna.local:177fe9e411e4f3d4b66fe0e633caf556:16777220:18420296:1:107:venv/lib/python2.7/site-packages/wheel-0.24.0.dist-info/entry_points.txt
manna.local:9d66b41bc2a080e7174acc5dffecd752:16777220:18420297:1:1125:venv/lib/python2.7/site-packages/wheel-0.24.0.dist-info/LICENSE.txt
manna.local:0fa17c98635ebfaf72c46eb5ff31247a:16777220:18420298:1:9117:venv/lib/python2.7/site-packages/wheel-0.24.0.dist-info/METADATA
manna.local:b669361941982cc1d520c77503d688b3:16777220:18420299:1:1510:venv/lib/python2.7/site-packages/wheel-0.24.0.dist-info/metadata.json
manna.local:2af2a25a164ae2c0b07461727cfcbda2:16777220:18420305:1:4930:venv/lib/python2.7/site-packages/wheel-0.24.0.dist-info/RECORD
manna.local:c1f70e1426eb3d219550b814c06c239e:16777220:18420301:1:364:venv/lib/python2.7/site-packages/wheel-0.24.0.dist-info/RECORD.jws
manna.local:ef72659542687b41fb1a4225120f41fa:16777220:18420302:1:6:venv/lib/python2.7/site-packages/wheel-0.24.0.dist-info/top_level.txt
manna.local:7443a0e34e1cdfcb5294578ac7fed8a3:16777220:18420303:1:110:venv/lib/python2.7/site-packages/wheel-0.24.0.dist-info/WHEEL

$ dupscan.py -d venv | parsedups.py --list | wc -l
parsedups.py: args => {'files': [], 'list_fields': True, 'size': 0, 'field_separator': '\x00'}
     698
```

If I indicate it should list files of size 100,000 bytes or greater:

```
$ dupscan.py -d venv | parsedups.py --list --size 100000
parsedups.py: args => {'files': [], 'list_fields': True, 'size': 100000, 'field_separator': '\x00'}
manna.local  fb0e405e7b3311dd6a46cf5918d41bf1      133353    18419337  venv/lib/python2.7/site-packages/pkg_resources/__init__.pyc
manna.local  4ea2a802c8f2188dcff76e40c0ec77e2      106466    18419911  venv/lib/python2.7/site-packages/pip/_vendor/pkg_resources/__init__.py
manna.local  3578983e05e8367767122054b8e40ad1      113855    18419961  venv/lib/python2.7/site-packages/pip/_vendor/requests/packages/chardet/big5freq.pyc
manna.local  eb9de34540cc21712b38f555ad3415bb      134764    18419912  venv/lib/python2.7/site-packages/pip/_vendor/pkg_resources/__init__.pyc
manna.local  aeaceddba964d9486b92c111ee77c2b0      106670    18419336  venv/lib/python2.7/site-packages/pkg_resources/__init__.py
manna.local  ffb367a1b27f407fe02ecd0a8cbefc35      117347    18419810  venv/lib/python2.7/site-packages/pip/_vendor/html5lib/html5parser.py
manna.local  6f58f7b3d7b46120dfa9839a15e2ef4e      136381    18419811  venv/lib/python2.7/site-packages/pip/_vendor/html5lib/html5parser.pyc
manna.local  cc3d2cd6b035dc31b2614c1df204848e      308434    18419933  venv/lib/python2.7/site-packages/pip/_vendor/requests/cacert.pem
```

We see that there are no duplicates 100,000 bytes or more in size:

```
$ ~/projects/bizcor/duplicates/bin/dupscan.py -d venv | ~/projects/bizcor/duplicates/bin/parsedups.py --size 100000
parsedups.py: args => {'files': [], 'list_fields': False, 'size': 100000, 'field_separator': '\x00'}
```

But there are some 10,000 bytes or more:

```
$ ~/projects/bizcor/duplicates/bin/dupscan.py -d venv | ~/projects/bizcor/duplicates/bin/parsedups.py --size 10000
parsedups.py: args => {'files': [], 'list_fields': False, 'size': 10000, 'field_separator': '\x00'}
manna.local  4ffe71fb39c0bec005ef454f84403a35       28079    18419350  venv/lib/python2.7/site-packages/pkg_resources/_vendor/packaging/specifiers.py
manna.local  4ffe71fb39c0bec005ef454f84403a35       28079    18419906  venv/lib/python2.7/site-packages/pip/_vendor/packaging/specifiers.py
manna.local  3e8b4f33d9750ce201facbf437b8d0ad       11949    18419908  venv/lib/python2.7/site-packages/pip/_vendor/packaging/version.py
manna.local  3e8b4f33d9750ce201facbf437b8d0ad       11949    18419352  venv/lib/python2.7/site-packages/pkg_resources/_vendor/packaging/version.py
manna.local  e97c622b03fb2a2598bf019fbbe29f2c       65536    18419371  venv/lib/python2.7/site-packages/setuptools/gui-32.exe
manna.local  e97c622b03fb2a2598bf019fbbe29f2c       65536    18419374  venv/lib/python2.7/site-packages/setuptools/gui.exe
manna.local  a32a382b8a5a906e03a83b4f3e5b7a9b       65536    18419359  venv/lib/python2.7/site-packages/setuptools/cli-32.exe
manna.local  a32a382b8a5a906e03a83b4f3e5b7a9b       65536    18419362  venv/lib/python2.7/site-packages/setuptools/cli.exe
```
