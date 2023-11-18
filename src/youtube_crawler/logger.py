import os
import logging
import functools
import traceback

logger = logging.getLogger("web-crawler-container")

if os.getenv("MODE", "dev") == "prod":
    logger.setLevel(logging.INFO)
else:
    logger.setLevel(logging.DEBUG)


def call_logger(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            logger.fatal(e)
            logger.fatal(traceback.format_exc())
            exit()

    return wrapper
