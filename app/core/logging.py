import logging
import sys


def setup_logging():
    logger = logging.getLogger("profiler")
    if not logger.handlers:
        stdout_handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(levelname)s:     %(message)s')
        stdout_handler.setFormatter(formatter)
        logger.addHandler(stdout_handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
