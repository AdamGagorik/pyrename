import argparse
import logging
import os

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