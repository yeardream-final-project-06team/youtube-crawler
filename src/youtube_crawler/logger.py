import os
import sys
import logging
import functools
import traceback

import msgspec

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
            sys.exit()

    return wrapper


def check_parsing_error(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if not result:
            return result
        for attr in result.__struct_fields__:
            if not getattr(result, attr):
                if attr in [
                    "tags",
                    "likes",
                    "view_count",
                    "desc",
                ]:
                    continue
                logger.error(f"attribution for {attr} not found")
                logger.error(msgspec.json.encode(result))
                break
        return result

    return wrapper
