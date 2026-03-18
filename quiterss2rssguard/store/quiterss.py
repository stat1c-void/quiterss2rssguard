"""
QuiteRSS database store implementation.
"""

from __future__ import annotations

import datetime as dt
import logging
from typing import Self

from ..data import Feed, NewsItem
from .base import BaseStore, StoreConnectionError, StoreOperationError, StoreValidationError

logger = logging.getLogger(__name__)


class QuiteRssStore(BaseStore):
    """
    Manages connection to a QuiteRSS SQLite database.
    """

    def open(self) -> Self:
        """
        Open database connection and validate version.

        Returns:
            self for method chaining

        Raises:
            StoreConnectionError: If database file not found or connection fails
            StoreValidationError: If database version is not 17
            sqlite3.Error: If database operations fail
        """
        super().open()

        # Validate database version
        if self._connection is None:
            raise StoreConnectionError("Database connection failed to initialize")

        cursor = self._connection.cursor()
        cursor.execute("SELECT value FROM info WHERE name = 'version'")
        version_row = cursor.fetchone()

        if not version_row:
            raise StoreValidationError("Could not determine database version")

        version = int(version_row[0])
        if version != 17:
            raise StoreValidationError(
                f"Unsupported database version: {version}. Expected version 17."
            )

        return self

    def read_feeds(self) -> list[Feed]:
        """
        Read all feeds from the QuiteRSS database.

        Returns:
            List of Feed objects

        Raises:
            StoreOperationError: If database is not open
        """
        if not self._connection:
            raise StoreOperationError(
                "Database connection is not open. Use 'with' block or call open()."
            )

        cursor = self._connection.cursor()
        cursor.execute("""
            SELECT 
                id, text, description, xmlUrl, htmlUrl
            FROM feeds
        """)

        feeds: list[Feed] = []
        for row in cursor.fetchall():
            row_id, name, description, url, url_html = row

            if not name or not url:
                logger.warning(
                    "skipping feed with id %s: missing required fields (name=%r, url=%r)",
                    row_id,
                    name,
                    url,
                )
                continue

            feed = Feed(
                id=row_id,
                mapped_id=0,  # Will be assigned during migration to RSS Guard
                name=name,
                description=description or "",
                url=url,
                url_html=url_html or "",
            )
            feeds.append(feed)

        return feeds

    def read_news_items(self, feed: Feed, skip_older_than: dt.timedelta) -> list[NewsItem]:
        """
        Read news items for a given feed from the QuiteRSS database.

        Args:
            feed: Feed object to load news items for
            skip_older_than: Filter out deleted items older than this duration

        Returns:
            List of NewsItem objects

        Raises:
            StoreOperationError: If database is not open
        """
        if not self._connection:
            raise StoreOperationError(
                "Database connection is not open. Use 'with' block or call open()."
            )

        cutoff = dt.datetime.now() - skip_older_than
        cutoff_str = cutoff.isoformat()

        cursor = self._connection.cursor()
        cursor.execute(
            """
            SELECT 
                id, guid, guidislink, title, author_name, link_href, published, description, deleted
            FROM news
            WHERE feedId = ? AND (deleted = 0 OR (deleted = 1 AND published >= ?))
            """,
            (feed.id, cutoff_str),
        )

        news_items: list[NewsItem] = []
        for row in cursor.fetchall():
            (
                row_id,
                guid,
                guidislink,
                title,
                author,
                link_href,
                published,
                description,
                deleted,
            ) = row

            if not all([row_id, guid, title, published]):
                logger.warning(
                    "skipping news item with id %s: missing required fields "
                    "(guid=%r, title=%r, published=%r)",
                    row_id,
                    guid,
                    title,
                    published,
                )
                continue

            url = link_href
            if not url:
                if guidislink == "true":
                    url = guid
                else:
                    logger.warning(
                        "skipping news item with id %s: missing URL and guidislink is not true",
                        row_id,
                    )
                    continue

            try:
                date = dt.datetime.fromisoformat(published)
            except ValueError:
                logger.warning(
                    "skipping news item with id %s: invalid date format %r",
                    row_id,
                    published,
                )
                continue

            item = NewsItem(
                id=row_id,
                mapped_id=0,
                feed=feed,
                guid=guid,
                title=title,
                author=author or "",
                url=url,
                date=date,
                preview=description or "",
                deleted=bool(deleted),
            )
            news_items.append(item)

        return news_items
