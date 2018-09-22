import logging
import sys

from rainbow_logging_handler import RainbowLoggingHandler

# setup `logging` module
logger = logging.getLogger('console')
formatter = logging.Formatter("%(message)s")

# setup `RainbowLoggingHandler`
handler = RainbowLoggingHandler(sys.stderr, color_funcName=('black', 'yellow', True))
handler.setFormatter(formatter)
logger.addHandler(handler)


def get_logger():
    return logger


def set_level(level):
    logger.setLevel(level)


