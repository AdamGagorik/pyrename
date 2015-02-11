"""
Rename files or directories using regular expression.
Does nothing without the --force option.

example:
    ./pyrename.py '(.*)\.py' '\g<1>_renamed.py'

"""
import logging
import os
import re

from .. import logutils
from .. import options
from .. import utils

logutils.setup_logging()

def main(args=None):
    work = os.getcwd()
    opts = options.get_arguments(work, args)

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
    for root, p in utils.walk(opts.top, r=opts.recursive, dirs=opts.dirs, files=opts.files):
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
            utils.move(opath, npath, git=opts.git)
    else:
        logging.info('\n\n\tThis was a dry run, please use --force to perform renaming\n')

if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        pass
    except:
        logging.exception('caught unhandled exception')