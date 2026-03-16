"""
QuiteRSS database store implementation.
"""

import sqlite3
from pathlib import Path
from typing import Optional

from ..data import Feed


class QuiteRssStore:
    """
    Manages connection to a QuiteRSS SQLite database.

    Supports context manager protocol for automatic connection management.
    """

    def __init__(self, db_path: Path):
        """
        Initialize the store with a database path.

        Args:
            db_path: Path to the QuiteRSS SQLite database
        """
        self.db_path = db_path
        self._connection: Optional[sqlite3.Connection] = None

    def open(self) -> "QuiteRssStore":
        """
        Open database connection and validate version.

        Returns:
            self for method chaining

        Raises:
            ValueError: If database file not found or version is not 17
            sqlite3.Error: If database operations fail
        """
        if not self.db_path.exists():
            raise ValueError(f"Database file not found: {self.db_path}")

        self._connection = sqlite3.connect(self.db_path)

        # Validate database version
        cursor = self._connection.cursor()
        cursor.execute("SELECT value FROM info WHERE name = 'version'")
        version_row = cursor.fetchone()

        if not version_row:
            raise ValueError("Could not determine database version")

        version = int(version_row[0])
        if version != 17:
            raise ValueError(f"Unsupported database version: {version}. Expected version 17.")

        return self

    def close(self) -> None:
        """
        Close the database connection.

        Raises:
            sqlite3.Error: If closing the connection fails
        """
        if self._connection:
            self._connection.close()
            self._connection = None

    def __enter__(self) -> "QuiteRssStore":
        """Enter context manager, opening the database connection."""
        return self.open()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context manager, closing the database connection."""
        self.close()

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
            feed = Feed(
                id=row[0],
                mapped_id=0,  # Will be assigned during migration to RSS Guard
                name=row[1] or "",
                title=row[2] or "",
                description=row[3] or "",
                url=row[4] or "",
                urlHtml=row[5] or "",
            )
            feeds.append(feed)

        return feeds
