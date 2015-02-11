from subprocess import check_call
import itertools
import logging
import shutil
import os

def move(opath, npath, git=False):
    if git:
        logging.info('\n\n\tgit mv %s\n\t       %s\n', opath, npath)
        check_call(['git', 'mv', opath, npath])
    else:
        logging.info('\n\n\tmv %s\n\t   %s\n', opath, npath)
        shutil.move(opath, npath)

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