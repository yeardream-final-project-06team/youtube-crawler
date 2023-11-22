import functools
import logging
import os
import sys
import traceback

import msgspec
import requests

from youtube_crawler.models import VideoSimple

logger = logging.getLogger("web-crawler-container")
DISCOED_WEBHOOK_URL = os.getenv("DISCOED_WEBHOOK_URL", "")

if os.getenv("MODE", "dev") == "prod":
    logging.basicConfig(level=logging.INFO)
else:
    logging.basicConfig(level=logging.DEBUG)


def call_logger(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            logger.fatal(e)
            logger.fatal(traceback.format_exc())

            error_type = type(e).__name__  # 에러 타입
            error_msg = str(e)  # 에러 메시지
            send_msg = f"ErrorType: {error_type}\nErrorMessage: {error_msg}"
            if DISCOED_WEBHOOK_URL:
                requests.post(DISCOED_WEBHOOK_URL, json={"content": send_msg})

            sys.exit()

    return wrapper


def check_parsing_error(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if not result:
            return result
        for attr in result.__dict__:
            if not getattr(result, attr):
                if attr in [
                    "tags",
                    "likes",
                    "view_count",
                    "description",
                ]:
                    continue
                logger.error(f"attribution for {attr} not found")
                logger.error(msgspec.json.encode(result))
                break
        return result

    return wrapper
