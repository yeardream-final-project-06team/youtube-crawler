import os

import msgspec
from elasticsearch import Elasticsearch

from youtube_crawler.logger import logger
from youtube_crawler.models import VideoDetail, VideoSimple


ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "http://localhost")
ELASTICSEARCH_PORT = os.getenv("ELASTICSEARCH_PORT", "9200")


class Sender:
    def __init__(self):
        self.es = Elasticsearch(f"{ELASTICSEARCH_HOST}:{ELASTICSEARCH_PORT}")

    def send_one(self, index: str, video: VideoDetail | VideoSimple) -> None:
        res = self.es.index(index=index, body=msgspec.json.encode(video))
        logger.info(msgspec.json.encode(res.body))

    def send_many(self, index: str, videos: list[VideoDetail | VideoSimple]) -> None:
        for v in videos:
            self.send_one(index, v)