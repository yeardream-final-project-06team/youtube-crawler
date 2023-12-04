import functools
import logging
import os
import sys
import traceback

import msgspec
import requests

DISCOED_WEBHOOK_URL = os.getenv("DISCOED_WEBHOOK_URL", "")

# 사용자 정의 로그 레벨 생성
NOTICE_LEVEL = 25  # INFO(20)와 WARNING(30) 사이
logging.addLevelName(NOTICE_LEVEL, 'NOTICE')

def notice(self, message, *args, **kws):
    if self.isEnabledFor(NOTICE_LEVEL):
        self._log(NOTICE_LEVEL, message, args, **kws)

logging.Logger.notice = notice

# 로거 설정
logger = logging.getLogger("crawler")
logger.setLevel(NOTICE_LEVEL)

if os.getenv("MODE", "dev") == "prod":
    logging.basicConfig(level=NOTICE_LEVEL)
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
                    "ads",
                ]:
                    continue
                logger.error(f"attribution for {attr} not found")
                logger.error(msgspec.json.encode(result))
                break
        return result

    return wrapper
