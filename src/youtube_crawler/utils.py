from random import random
from urllib.parse import urlparse, parse_qs

from youtube_crawler.logger import logger


def get_video_path(url: str) -> str:
    return urlparse(url).path


def get_video_id(url: str) -> str:
    query = urlparse(url).query
    d = parse_qs(query)
    return d["v"][0]


def cvt_play_time(play_time: str) -> int:
    if play_time == "live":
        return int(random() * 10 * 60)
    _play_time = play_time.split(":")
    match len(_play_time):
        case 1:
            seconds = int(_play_time[0])
        case 2:
            seconds = int(_play_time[0]) * 60 + int(_play_time[1])
        case 3:
            seconds = (
                int(_play_time[0]) * 3600 + int(_play_time[1]) * 60 + int(_play_time[2])
            )
        case _:
            logger.warn(f"{play_time} not matched")
            return 0
    return seconds
