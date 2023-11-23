import os
import hashlib
import subprocess
from datetime import datetime

import msgspec
from elasticsearch import Elasticsearch

from youtube_crawler.logger import logger
from youtube_crawler.models import VideoAd, VideoDetail, VideoSimple

ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "localhost")
ELASTICSEARCH_PORT = os.getenv("ELASTICSEARCH_PORT", "9200")


class Sender:
    def __init__(self, name: str):
        self.es = Elasticsearch(f"http://{ELASTICSEARCH_HOST}:{ELASTICSEARCH_PORT}")

        self.container_id = subprocess.run(
            ["hostname"], capture_output=True, text=True
        ).stdout.strip()

        self.name = name
        self.hashed = hashlib.md5(name.encode("utf-8")).hexdigest()

    def send_one(
        self,
        index: str,
        video: VideoDetail | VideoSimple | VideoAd,
    ) -> None:
        data = video.__dict__
        data["@timestamp"] = (
            datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        )
        data["container_id"] = self.container_id
        data["persona"] = self.name
        index += f"_{self.hashed}"
        self.es.index(index=index, body=msgspec.json.encode(data))

    def send_many(self, index: str, videos: list[VideoSimple]) -> None:
        for v in videos:
            self.send_one(index, v)
