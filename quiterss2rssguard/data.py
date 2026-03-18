from __future__ import annotations

import datetime as dt
from dataclasses import dataclass


@dataclass
class Feed:
    id: int  # id in quiterss db
    mapped_id: int  # id in rssguard db
    name: str  # stored as `title` in rssguard db
    description: str
    url: str
    url_html: str

    def __str__(self) -> str:
        return f"Feed(id={self.id}, name={self.name!r})"


@dataclass
class NewsItem:
    id: int  # id in quiterss db
    mapped_id: int  # id in rssguard db
    feed: Feed
    guid: str
    title: str
    author: str
    url: str
    date: dt.datetime
    preview: str
