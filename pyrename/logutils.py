import logging

def setup_logging():
    lfmt = '[%(asctime)s][%(process)5d][%(levelname)-5s]: %(message)s'
    dfmt = "%Y-%m-%d %H:%M:%S"
    logging.basicConfig(level=logging.INFO, format=lfmt, datefmt=dfmt)
