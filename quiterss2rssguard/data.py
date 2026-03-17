from dataclasses import dataclass


@dataclass
class Feed:
    id: int  # id in quiterss db
    mapped_id: int  # id in rssguard db
    name: str
    title: str
    description: str
    url: str
    url_html: str

    def __repr__(self) -> str:
        return f"Feed(id={self.id}, name={self.name!r}, url={self.url!r})"
