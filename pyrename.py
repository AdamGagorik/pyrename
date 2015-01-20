#!/usr/bin/env python
"""
Rename files or directories using regular expression.
Does nothing without the --force option.

example:
    ./pyrename.py '(.*)\.py' '\g<1>_renamed.py'

"""
from subprocess import check_call
import itertools
import argparse
import logging
import shutil
import os
import re

def setup_logging():
    lfmt = '[%(asctime)s][%(process)5d][%(levelname)-5s]: %(message)s'
    dfmt = "%Y-%m-%d %H:%M:%S"
    logging.basicConfig(level=logging.INFO, format=lfmt, datefmt=dfmt)

setup_logging()

def log_option(opts, attr):
    obj = getattr(opts, attr)

    if isinstance(obj, list) or isinstance(obj, tuple):
        for i, item in enumerate(obj):
            logging.info('%-10s = %s', '{}[{:d}]'.format(attr, i), obj[i])
        return

    if isinstance(obj, set):
        i = 0
        for item in obj:
            logging.info('%-10s = %s', '{}[{:d}]'.format(attr, i), item)
            i += 1
        return

    logging.info('%-10s = %s', attr, obj)

def move(opath, npath, git=False):
    if git:
        logging.info('\n\n\tgit mv %s\n\t       %s\n', opath, npath)
        check_call(['git', 'mv', opath, npath])
    else:
        logging.info('\n\n\tmv %s\n\t   %s\n', opath, npath)
        shutil.move(opath, npath)

class Options(object):
    def __init__(self, work):
        self.pattern = None
        self.replace = None
        self.nomatch = None
        self.exclude = []
        self.top     = os.path.realpath(os.path.expanduser(work))

        self.recursive  = False
        self.dirs       = False
        self.files      = True
        self.both       = False
        self.force      = False
        self.ignorecase = False
        self.silent     = False
        self.git        = False
        self.func       = False

def get_arguments(work, args=None):
    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    opts = Options(work)

    # regular expressions
    parser.add_argument(dest='pattern', type=str,
        help='expression: pattern')
    parser.add_argument(dest='replace', type=str,
        help='expression: replace')
    parser.add_argument('--nomatch', type=str, default=opts.nomatch,
        help='expression: nomatch')
    parser.add_argument('--exclude', type=str, nargs='*', default=opts.exclude,
        help='list of files to exclude')

    # searching
    parser.add_argument('-t', '--top', type=str, default=opts.top,
        help='top level directory')
    parser.add_argument('-r', '--recursive', action='store_true',
        help='search recursivly')

    fgroup = parser.add_mutually_exclusive_group()
    fgroup.add_argument('-d', '--dirs' , action='store_true',
        help='match directories')
    fgroup.add_argument('-b', '--both' , action='store_true',
        help='match directories and files')

    # mode
    parser.add_argument('-f', '--force', action='store_true',
        help='rename files')
    parser.add_argument('-g', '--git', action='store_true',
        help='use git mv')
    parser.add_argument('-i', '--ignorecase', action='store_true',
        help='ignore case')
    parser.add_argument('-s', '--silent', action='store_true',
        help='silent')
    parser.add_argument('-x', '--func', action='store_true',
        help='replace pattern is lambda x : {replace}')

    # parse
    parser.parse_args(args, namespace=opts)

    # logging
    if opts.silent:
        logging.getLogger().setLevel(logging.ERROR)

    # update opts
    if opts.dirs:
        opts.files = False
    if opts.both:
        opts.dirs  = True
        opts.files = True

    # fix path
    opts.top = os.path.realpath(opts.top)

    # fix exclude
    opts.exclude = set(opts.exclude)
    opts.exclude.add(os.path.basename(__file__))

    # log options
    log_option(opts, 'pattern')
    log_option(opts, 'replace')
    log_option(opts, 'nomatch')
    log_option(opts, 'exclude')

    log_option(opts, 'top')
    log_option(opts, 'recursive')

    log_option(opts, 'dirs')
    log_option(opts, 'both')

    log_option(opts, 'force')
    log_option(opts, 'git')
    log_option(opts, 'ignorecase')
    log_option(opts, 'silent')
    log_option(opts, 'func')

    return opts

def walk(top, r=False, dirs=False, files=False):
    if dirs or files:
        if r:
            for root, dbases, fbases in os.walk(top, followlinks=False):
                if dirs and files:
                    for p in itertools.chain(dbases, fbases):
                        yield root, p
                elif dirs:
                    for d in dbases:
                        yield root, d
                elif files:
                    for f in fbases:
                        yield root, f
        else:
            root, dbases, fbases = next(os.walk(top, followlinks=False))
            if dirs and files:
                for p in itertools.chain(dbases, fbases):
                    yield root, p
            elif dirs:
                for d in dbases:
                    yield root, d
            elif files:
                for f in fbases:
                    yield root, f
    else:
        raise StopIteration

def main(args=None):
    work = os.getcwd()
    opts = get_arguments(work, args)

    # check top level directory
    if not os.path.exists(opts.top) or not os.path.isdir(opts.top):
        raise RuntimeError('invalid top level directory: %s' % opts.top)

    # compile regex
    if opts.ignorecase:
        regex1 = re.compile(opts.pattern, re.IGNORECASE)
        try:
            regex2 = re.compile(opts.nomatch, re.IGNORECASE)
        except TypeError:
            regex2 = None
    else:
        regex1 = re.compile(opts.pattern)
        try:
            regex2 = re.compile(opts.nomatch)
        except TypeError:
            regex2 = None

    # compile replace
    if opts.func:
        opts.replace = eval('lambda x : {}'.format(opts.replace))

    # record errors
    error = False

    # find paths
    opaths = []
    npaths = []
    for root, p in walk(opts.top, r=opts.recursive, dirs=opts.dirs, files=opts.files):
        match = regex1.match(p)
        if match:
            # exclude list
            if p in opts.exclude:
                logging.info('path excluded!\n\n\t%s\n', os.path.join(root, p))
                continue

            # exclude nomatch
            if not regex2 is None and regex2.match(p):
                logging.info('path excluded!\n\n\t%s\n', os.path.join(root, p))
                continue

            # construct new base
            try:
                n = regex1.sub(opts.replace, p)
            except re.error:
                logging.exception('regex error')
                error = True
                n = p

            # construct paths
            opath = os.path.join(root, p)
            npath = os.path.join(root, n)
            opaths.append((root, p, opath))
            npaths.append((root, n, npath))

            # output match
            logging.info('found a match!\n\n\topath (%d): %s\n\tnpath (%d): %s\n',
                os.path.exists(opath), opath, os.path.exists(npath), npath)

    # descibe paths
    oset = set(opaths)
    nset = set(npaths)
    iset = oset.intersection(nset)

    logging.info('%d old', len(opaths))
    logging.info('%d old (unique)', len(oset))
    logging.info('%d new', len(npaths))
    logging.info('%d new (unique)', len(nset))
    logging.info('%d same', len(iset))

    # make sure paths were found
    try:
        assert opaths
    except AssertionError:
        logging.error('no old paths found')
        error = True

    # make sure paths were found
    try:
        assert npaths
    except AssertionError:
        logging.error('no new paths found')
        error = True

    # make sure old paths are unique
    try:
        assert len(oset) is len(opaths)
    except AssertionError:
        logging.error('old paths are not unique')
        error = True

    # make sure new paths are unique
    try:
        assert len(nset) is len(npaths)
    except AssertionError:
        logging.error('new paths are not unique')
        error = True

    # make sure old paths and new paths do not intersect
    try:
        assert not iset
    except AssertionError:
        logging.error('some paths are the same')
        error = True

    # check if old paths exist
    found = []
    for root, base, path in opaths:
        try:
            assert os.path.exists(path)
        except AssertionError:
            found.append(path)
    if found:
        logging.error('some old paths do not exist\n\n\t%s\n',
            '\n\t'.join(found))
        error = True

    # check if new paths exist
    found = []
    for root, base, path in npaths:
        try:
            assert not os.path.exists(path)
        except AssertionError:
            found.append(path)
    if found:
        logging.error('some new paths already exist\n\n\t%s\n',
            '\n\t'.join(found))
        error = True

    # stop if there were errors
    if error:
        raise RuntimeError('invalid configuration')

    # move files
    if opts.force:
        logging.info('moving paths!')
        for (oroot, obase, opath), (nroot, nbase, npath) in zip(opaths, npaths):
            move(opath, npath, git=opts.git)
    else:
        logging.info('\n\n\tThis was a dry run, please use --force to perform renaming\n')

if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        pass
    except:
        logging.exception('caught unhandled exception')
