"""
RSS Guard database store implementation.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Self

from ..data import Feed
from .base import BaseStore, StoreConnectionError, StoreOperationError, StoreValidationError

logger = logging.getLogger(__name__)


class RssGuardStore(BaseStore):
    """
    Manages connection to an RSS Guard SQLite database.
    """

    def __init__(self, db_path: Path):
        super().__init__(db_path)
        self.account_id: int = 0

    def open(self) -> Self:
        """
        Open database connection and validate version.

        Returns:
            self for method chaining

        Raises:
            StoreConnectionError: If database file not found or connection fails
            StoreValidationError: If database schema version is not 8 or no std-rss account found
            sqlite3.Error: If database operations fail
        """
        super().open()

        # Validate database version
        if self._connection is None:
            raise StoreConnectionError("Database connection failed to initialize")

        cursor = self._connection.cursor()
        cursor.execute("SELECT inf_value FROM Information WHERE inf_key = 'schema_version'")
        version_row = cursor.fetchone()

        if not version_row:
            raise StoreValidationError("Could not determine database schema version")

        version = version_row[0]
        if version != "8":
            raise StoreValidationError(
                f"Unsupported database schema version: {version}. Expected version 8."
            )

        # Find first "type = std-rss" account
        cursor.execute("SELECT id FROM Accounts WHERE type = 'std-rss' LIMIT 1")
        account_row = cursor.fetchone()

        if not account_row:
            raise StoreValidationError("No 'std-rss' account found in Accounts table")

        self.account_id = account_row[0]
        logger.info("found std-rss account with id: %d", self.account_id)

        return self

    def store_feed(self, feed: Feed) -> None:
        """
        Store a feed in the RSS Guard database.

        Args:
            feed: Feed object to store

        Raises:
            StoreOperationError: If database is not open
            StoreOperationError: If database operations fail
        """
        if not self._connection:
            raise StoreOperationError(
                "Database connection is not open. Use 'with' block or call open()."
            )

        cursor = self._connection.cursor()

        # Check if feed exists by title
        cursor.execute("SELECT id FROM Feeds WHERE title = ?", (feed.title,))
        existing_row = cursor.fetchone()

        if existing_row:
            existing_id = existing_row[0]
            if existing_id is None:
                raise StoreOperationError("Database returned NULL for Feed id")
            feed.mapped_id = existing_id
            logger.info("feed '%s' found in DB, mapped_id=%d", feed.title, feed.mapped_id)
            return

        # Get max order
        cursor.execute("SELECT MAX(ordr) FROM Feeds")
        max_order_row = cursor.fetchone()

        if max_order_row and max_order_row[0] is not None:
            max_order = max_order_row[0]
        else:
            max_order = -1

        new_order = max_order + 1

        # Create deterministic custom_id
        custom_id = f"migrated_{feed.id}"

        # Insert new feed
        cursor.execute(
            """
            INSERT INTO Feeds (
                ordr, title, description, source, category, update_type, 
                account_id, custom_id, icon
            ) VALUES (?, ?, ?, ?, -1, 1, ?, ?, ?)
            """,
            (
                new_order,
                feed.title,
                feed.description,
                feed.url,
                self.account_id,
                custom_id,
                b"",  # icon as empty blob
            ),
        )

        # Get the new row ID
        new_id = cursor.lastrowid
        if new_id is None:
            raise StoreOperationError("Failed to get new feed ID after insert")

        feed.mapped_id = new_id
        logger.info("feed '%s' created in DB, mapped_id=%d", feed.title, new_id)

        # Update custom_id to match the new row ID
        cursor.execute("UPDATE Feeds SET custom_id = ? WHERE id = ?", (str(new_id), new_id))

        # Commit changes
        self._connection.commit()
