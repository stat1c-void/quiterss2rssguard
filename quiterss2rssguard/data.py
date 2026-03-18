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
        return f"Feed(id={self.id}, mapped_id={self.mapped_id}, name={self.name!r})"


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
    deleted: bool

    def __str__(self) -> str:
        title = (self.title[:12] + "...") if len(self.title) > 15 else self.title
        return (
            f"NewsItem(id={self.id}, mapped_id={self.mapped_id}, deleted={self.deleted}, "
            f"feed={self.feed}, title={title!r})"
        )
