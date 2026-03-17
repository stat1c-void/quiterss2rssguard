import sqlite3
import tempfile
from pathlib import Path

import pytest

from quiterss2rssguard.store import QuiteRssStore


def create_test_db(db_path: Path):
    """Create a test QuiteRSS database with sample data."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        # Create info table
        cursor.execute("""
            CREATE TABLE info
            (
                id    integer primary key,
                name  varchar,
                value varchar
            )
        """)

        # Insert version info
        cursor.execute("INSERT INTO info (id, name, value) VALUES (1, 'version', '17')")

        # Create feeds table (simplified version with only needed columns)
        cursor.execute("""
            CREATE TABLE feeds
            (
                id integer primary key,
                text varchar,
                title varchar,
                description varchar,
                xmlUrl varchar,
                htmlUrl varchar
            )
        """)

        # Insert sample feed data
        cursor.execute("""
            INSERT INTO feeds (id, text, title, description, xmlUrl, htmlUrl)
            VALUES (1, 'Test Feed', 'Test Title', 'Test Description', 
                    'https://example.com/rss', 'https://example.com')
        """)

        cursor.execute("""
            INSERT INTO feeds (id, text, title, description, xmlUrl, htmlUrl)
            VALUES (2, 'Another Feed', 'Another Title', 'Another Description', 
                    'https://example2.com/rss', 'https://example2.com')
        """)

        conn.commit()


def test_read_feeds_valid_db():
    """Test reading feeds from a valid database."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)

    try:
        create_test_db(db_path)

        with QuiteRssStore(db_path) as store:
            feeds = store.read_feeds()

        assert len(feeds) == 2

        # Check first feed
        feed1 = feeds[0]
        assert feed1.id == 1
        assert feed1.mapped_id == 0
        assert feed1.name == "Test Feed"
        assert feed1.title == "Test Title"
        assert feed1.description == "Test Description"
        assert feed1.url == "https://example.com/rss"
        assert feed1.url_html == "https://example.com"

        # Check second feed
        feed2 = feeds[1]
        assert feed2.id == 2
        assert feed2.name == "Another Feed"

    finally:
        db_path.unlink()


def test_read_feeds_nonexistent_db():
    """Test that reading from a non-existent database raises ValueError."""
    with tempfile.TemporaryDirectory() as tmpdir:
        non_existent_db = Path(tmpdir) / "nonexistent.db"

        with pytest.raises(ValueError, match="Database file not found"):
            with QuiteRssStore(non_existent_db) as _store:
                pass


def test_read_feeds_wrong_version():
    """Test that reading from a database with wrong version raises ValueError."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE info
                (
                    id    integer primary key,
                    name  varchar,
                    value varchar
                )
            """)
            cursor.execute("INSERT INTO info (id, name, value) VALUES (1, 'version', '16')")
            conn.commit()

        with pytest.raises(ValueError, match="Unsupported database version"):
            with QuiteRssStore(db_path) as _store:
                pass

    finally:
        db_path.unlink()


def test_read_feeds_empty_values():
    """Test handling of NULL/empty values in database."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE info
                (
                    id    integer primary key,
                    name  varchar,
                    value varchar
                )
            """)
            cursor.execute("INSERT INTO info (id, name, value) VALUES (1, 'version', '17')")

            cursor.execute("""
                CREATE TABLE feeds
                (
                    id integer primary key,
                    text varchar,
                    title varchar,
                    description varchar,
                    xmlUrl varchar,
                    htmlUrl varchar
                )
            """)

            # Insert feed with NULL values for required fields (name and url)
            # This feed should be skipped
            cursor.execute("""
                INSERT INTO feeds (id, text, title, description, xmlUrl, htmlUrl)
                VALUES (1, NULL, NULL, NULL, NULL, NULL)
            """)

            # Insert a valid feed
            cursor.execute("""
                INSERT INTO feeds (id, text, title, description, xmlUrl, htmlUrl)
                VALUES (2, 'Valid Feed', 'Valid Title', 'Valid Description', 
                        'https://example.com/rss', 'https://example.com')
            """)

            conn.commit()

        with QuiteRssStore(db_path) as store:
            feeds = store.read_feeds()

        # Only the valid feed should be returned (id 2)
        assert len(feeds) == 1
        feed = feeds[0]
        assert feed.id == 2
        assert feed.name == "Valid Feed"
        assert feed.title == "Valid Title"
        assert feed.description == "Valid Description"
        assert feed.url == "https://example.com/rss"
        assert feed.url_html == "https://example.com"

    finally:
        db_path.unlink()


def test_explicit_open_close():
    """Test explicit open/close methods."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)

    try:
        create_test_db(db_path)

        store = QuiteRssStore(db_path)
        store.open()
        try:
            feeds = store.read_feeds()
            assert len(feeds) == 2
        finally:
            store.close()

    finally:
        db_path.unlink()


def test_read_without_connection():
    """Test that reading without an open connection raises RuntimeError."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)

    try:
        create_test_db(db_path)

        store = QuiteRssStore(db_path)
        with pytest.raises(RuntimeError, match="Database connection is not open"):
            store.read_feeds()

    finally:
        db_path.unlink()
