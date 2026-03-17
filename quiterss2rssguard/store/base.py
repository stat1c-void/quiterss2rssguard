"""
Base class for database store implementations.
"""
# TODO: add custom exception classes for stores

import logging
import sqlite3
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class BaseStore:
    """
    Manages connection to a SQLite database.

    Supports context manager protocol for automatic connection management.
    """

    def __init__(self, db_path: Path):
        """
        Initialize the store with a database path.

        Args:
            db_path: Path to the SQLite database
        """
        self.db_path = db_path
        self._connection: Optional[sqlite3.Connection] = None

    # FIXME: self type?
    def open(self) -> "BaseStore":
        """
        Open database connection.

        Returns:
            self for method chaining

        Raises:
            ValueError: If database file not found
            sqlite3.Error: If database operations fail
        """
        if not self.db_path.exists():
            raise ValueError(f"Database file not found: {self.db_path}")

        self._connection = sqlite3.connect(self.db_path)
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

    # FIXME: self type?
    def __enter__(self) -> "BaseStore":
        """Enter context manager, opening the database connection."""
        return self.open()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context manager, closing the database connection."""
        self.close()
