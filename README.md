# python.rename
Python script for renaming files using regular expression.

```bash
usage: pyrename.py [-h] [--nomatch NOMATCH]
                   [--exclude [EXCLUDE [EXCLUDE ...]]]
                   [-t TOP] [-r]
                   [-d | -b]
                   [-f] [-i] [-s]
                   [pattern] [replace]

Rename files or directories using regular expression.
Does nothing without the --force option.

positional arguments:
  pattern               expression: pattern
  replace               expression: replace

optional arguments:
  -h, --help            show this help message and exit
  --nomatch NOMATCH     expression: nomatch
  --exclude [EXCLUDE [EXCLUDE ...]]
                        list of files to exclude
  -t TOP, --top TOP     top level directory
  -r, --recursive       search recursivly
  -d, --dirs            match directories
  -b, --both            match directories and files
  -f, --force           rename files
  -i, --ignorecase      ignore case
  -s, --silent          silent
```
