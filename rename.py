"""
Rename files or directories using regular expression.
"""
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
    logging.info('%-10s = %s', attr, getattr(opts, attr))

class Options(object):
    def __init__(self, work):
        self.pattern = r'(.*)'
        self.replace = r'\1'
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

def get_arguments(work, args=None):
    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    opts = Options(work)

    # regular expressions
    parser.add_argument(dest='pattern', type=str, nargs='?', default=opts.pattern,
        help='expression: pattern')
    parser.add_argument(dest='replace', type=str, nargs='?', default=opts.replace,
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
    parser.add_argument('-i', '--ignorecase', action='store_true',
        help='ignore case')
    parser.add_argument('-s', '--silent', action='store_true',
        help='silent')

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

    # log options
    log_option(opts, 'pattern')
    log_option(opts, 'replace')
    log_option(opts, 'top')

    log_option(opts, 'recursive')
    log_option(opts, 'files')
    log_option(opts, 'dirs')
    log_option(opts, 'both')

    log_option(opts, 'force')
    log_option(opts, 'ignorecase')

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
    try:
        for root, base, path in opaths:
            assert os.path.exists(path)
    except AssertionError:
        logging.error('some old paths do not exist')
        error = True

    # check if new paths exist
    try:
        for root, base, path in npaths:
           assert not os.path.exists(path)
    except AssertionError:
        logging.error('some new paths already exist')
        error = True

    # stop if there were errors
    if error:
        raise RuntimeError('invalid configuration')

    # move files
    if opts.force:
        logging.info('moving paths!')
        for (oroot, obase, opath), (nroot, nbase, npath) in zip(opaths, npaths):
            logging.info('\n\n\tmv %s\n\t   %s\n', opath, npath)
            shutil.move(opath, npath)
            pass
    else:
        logging.info('\n\n\tThis was a dry run, please use --force to perform renaming\n')

if __name__ == '__main__':
    try:
        main()
    except:
        logging.exception('caught unhandled exception')