from dataclasses import dataclass


@dataclass
class Feed:
    id: int
    mapped_id: int
    name: str
    title: str
    description: str
    url: str
    urlHtml: str
