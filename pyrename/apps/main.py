import logging
import os

def main():
    work = os.getcwd()

if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        pass
    except:
        logging.exception('caught unhandled exception')