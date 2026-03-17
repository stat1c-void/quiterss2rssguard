"""
QuiteRSS database store implementation.
"""

from __future__ import annotations

import logging
from typing import Self

from ..data import Feed
from .base import BaseStore

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
            ValueError: If database file not found or version is not 17
            sqlite3.Error: If database operations fail
        """
        super().open()

        # Validate database version
        if self._connection is None:
            raise RuntimeError("Database connection failed to initialize")

        cursor = self._connection.cursor()
        cursor.execute("SELECT value FROM info WHERE name = 'version'")
        version_row = cursor.fetchone()

        if not version_row:
            raise ValueError("Could not determine database version")

        version = int(version_row[0])
        if version != 17:
            raise ValueError(f"Unsupported database version: {version}. Expected version 17.")

        return self

    def read_feeds(self) -> list[Feed]:
        """
        Read all feeds from the QuiteRSS database.

        Returns:
            List of Feed objects

        Raises:
            RuntimeError: If database is not open
        """
        if not self._connection:
            raise RuntimeError("Database connection is not open. Use 'with' block or call open().")

        cursor = self._connection.cursor()
        cursor.execute("""
            SELECT 
                id, text, title, description, xmlUrl, htmlUrl
            FROM feeds
        """)

        feeds: list[Feed] = []
        for row in cursor.fetchall():
            row_id, name, title, description, url, url_html = row

            if not name or not url:
                logger.warning(
                    "Skipping feed with id %s: missing required fields (name=%r, url=%r)",
                    row_id,
                    name,
                    url,
                )
                continue

            feed = Feed(
                id=row_id,
                mapped_id=0,  # Will be assigned during migration to RSS Guard
                name=name,
                title=title or "",
                description=description or "",
                url=url,
                url_html=url_html or "",
            )
            feeds.append(feed)

        return feeds
