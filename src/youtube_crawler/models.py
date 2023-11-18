from msgspec import Struct
from datetime import datetime


class VideoDetail(Struct):
    title: str | None
    author: str | None
    channel: str | None
    view_count: int | None
    url: str | None
    like: int | None
    desc: str | None
    tags: list[str] | None
    upload_date: datetime | None
    play_time: str | None
    category: str | None
    id: str | None
    next_video_url: str | None


class VideoSimple(Struct):
    id: str | None
    title: str | None
    author: str | None
    url: str | None
    play_time: str | None
    view_count: int | None
