from msgspec import Struct
from datetime import datetime


class VideoAd(Struct):
    headline: str | None
    description: str | None
    icon: str | None
    container_id: str


class VideoDetail(Struct):
    id: str | None
    title: str | None
    author: str | None
    url: str | None
    play_time: str | None
    view_count: int | None
    description: str | None
    channel: str | None
    like: int | None
    tags: list[str] | None
    upload_date: datetime | None
    category: str | None
    next_video_url: str | None
    container_id: str
    ads: list[VideoAd] = []


class VideoSimple(Struct):
    id: str | None
    title: str | None
    author: str | None
    url: str | None
    play_time: str | None
    view_count: int | None
    container_id: str

