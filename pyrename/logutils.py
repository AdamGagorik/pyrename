import contextlib
import warnings
import logging


lfmt = '[%(asctime)s][%(process)5d][%(levelname)-5s]: %(message)s'
dfmt = "%Y-%m-%d %H:%M:%S"


def setup_logging(**kwargs):
    _kwargs = dict(level=logging.INFO, format=lfmt, datefmt=dfmt)
    _kwargs.update(**kwargs)
    logging.basicConfig(**_kwargs)
    logging.addLevelName(logging.CRITICAL, 'FATAL')
    logging.addLevelName(logging.WARNING, 'WARN')


def custom_warning_format(message, category, filename, lineno, *args, **kwargs):
    return '%s:%s\n%s: %s' % (filename, lineno, category.__name__, message)


@contextlib.contextmanager
def capture(capture_warnings=True, reraise=False):
    """
    Log exceptions and warnings.
    """
    try:
        if capture_warnings:
            default_warning_format = warnings.formatwarning
            warnings.formatwarning = custom_warning_format
            logging.captureWarnings(True)
        try:
            yield
        except Exception as e:
            logging.exception('caught unhandled excetion')
            if reraise:
                if not isinstance(e, Warning):
                    raise
    finally:
        if capture_warnings:
            warnings.formatwarning = default_warning_format
            logging.captureWarnings(False)