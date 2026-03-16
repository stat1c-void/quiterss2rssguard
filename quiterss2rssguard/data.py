from dataclasses import dataclass


@dataclass
class Feed:
    id: int  # id in quiterss db
    mapped_id: int  # id in rssguard db
    name: str
    title: str
    description: str
    url: str
    urlHtml: str
