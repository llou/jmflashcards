import sys
from logging import getLogger, StreamHandler, DEBUG, INFO, WARNING, ERROR, CRITICAL

def get_logger(level=WARNING):
    logger = getLogger()
    logger.setLevel(level)
    logger.setHandler(StreamHandler(stream=sys.stderr))
    return logger

