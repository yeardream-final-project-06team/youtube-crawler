from datetime import datetime
from dataclasses import dataclass


@dataclass
class VideoAd:
    headline: str
    description: str
    icon: str


@dataclass
class VideoDetail:
    id: str
    title: str
    author: str
    url: str
    play_time: str
    view_count: int
    description: str
    channel: str
    like: int
    tags: list[str]
    upload_date: datetime
    category: str
    next_video_url: str
    ads: list[VideoAd] = []


@dataclass
class VideoSimple:
    id: str
    title: str
    author: str
    url: str
    play_time: str
    view_count: int
