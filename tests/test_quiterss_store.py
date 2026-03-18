import datetime as dt
import sqlite3
import tempfile
from pathlib import Path

import pytest

from quiterss2rssguard.data import Feed
from quiterss2rssguard.store import (
    QuiteRssStore,
    StoreConnectionError,
    StoreOperationError,
    StoreValidationError,
)


@pytest.fixture
def quite_rss_db(db_file):
    """Create a test QuiteRSS database with sample data."""
    with sqlite3.connect(db_file) as conn:
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

        # Create news table
        cursor.execute("""
            CREATE TABLE news
            (
                id             integer primary key,
                feedId         integer,
                guid           varchar,
                guidislink     varchar default 'true',
                description    varchar,
                title          varchar,
                published      varchar,
                author_name    varchar,
                link_href      varchar
            )
        """)

        conn.commit()

    yield db_file


def test_read_feeds_valid_db(quite_rss_db):
    """Test reading feeds from a valid database."""
    with QuiteRssStore(quite_rss_db) as store:
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


def test_read_feeds_nonexistent_db():
    """Test that reading from a non-existent database raises StoreConnectionError."""
    with tempfile.TemporaryDirectory() as tmpdir:
        non_existent_db = Path(tmpdir) / "nonexistent.db"

        with pytest.raises(StoreConnectionError, match="Database file not found"):
            with QuiteRssStore(non_existent_db):
                pass


def test_read_feeds_wrong_version(quite_rss_db):
    """Test that reading from a database with wrong version raises StoreValidationError."""
    with sqlite3.connect(quite_rss_db) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE info SET value = '16' WHERE id = 1")
        conn.commit()

    with pytest.raises(StoreValidationError, match="Unsupported database version"):
        with QuiteRssStore(quite_rss_db):
            pass


def test_read_feeds_empty_values(quite_rss_db):
    """Test handling of NULL/empty values in database."""
    with sqlite3.connect(quite_rss_db) as conn:
        cursor = conn.cursor()

        # Delete existing feeds
        cursor.execute("DELETE FROM feeds")

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

    with QuiteRssStore(quite_rss_db) as store:
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


def test_explicit_open_close(quite_rss_db):
    """Test explicit open/close methods."""
    store = QuiteRssStore(quite_rss_db)
    store.open()
    try:
        feeds = store.read_feeds()
        assert len(feeds) == 2
    finally:
        store.close()


def test_read_without_connection(quite_rss_db):
    """Test that reading without an open connection raises StoreOperationError."""
    store = QuiteRssStore(quite_rss_db)
    with pytest.raises(StoreOperationError, match="Database connection is not open"):
        store.read_feeds()


def test_read_news_items_happy_path(quite_rss_db):
    """Test reading news items for a feed."""
    with sqlite3.connect(quite_rss_db) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO news (id, feedId, guid, title, author_name, link_href, published, description)
            VALUES (101, 1, 'guid-1', 'News Title 1', 'Author 1', 
                    'https://example.com/news1', '2026-03-18T12:00:00', 'Description 1')
            """
        )
        conn.commit()

    feed = Feed(1, 0, "Test Feed", "Test Title", "Test Description", "url", "url_html")
    with QuiteRssStore(quite_rss_db) as store:
        news_items = store.read_news_items(feed)

    assert len(news_items) == 1
    item = news_items[0]
    assert item.id == 101
    assert item.mapped_id == 0
    assert item.feed == feed
    assert item.guid == "guid-1"
    assert item.title == "News Title 1"
    assert item.author == "Author 1"
    assert item.url == "https://example.com/news1"
    assert item.date == dt.datetime(2026, 3, 18, 12, 0)
    assert item.preview == "Description 1"


def test_read_news_items_validation(quite_rss_db):
    """Test validation and skipping of news items with missing required fields."""
    with sqlite3.connect(quite_rss_db) as conn:
        cursor = conn.cursor()
        # Item 1: Missing guid
        cursor.execute(
            "INSERT INTO news (id, feedId, guid, title, published) VALUES (1, 1, NULL, 'T', '2026-01-01T00:00:00')"
        )
        # Item 2: Missing title
        cursor.execute(
            "INSERT INTO news (id, feedId, guid, title, published) VALUES (2, 1, 'G', NULL, '2026-01-01T00:00:00')"
        )
        # Item 3: Missing published
        cursor.execute(
            "INSERT INTO news (id, feedId, guid, title, published) VALUES (3, 1, 'G', 'T', NULL)"
        )
        # Item 4: Invalid date
        cursor.execute(
            "INSERT INTO news (id, feedId, guid, title, published) VALUES (4, 1, 'G', 'T', 'invalid')"
        )
        # Item 5: Valid
        cursor.execute(
            "INSERT INTO news (id, feedId, guid, title, published, link_href) VALUES (5, 1, 'G', 'T', '2026-01-01T00:00:00', 'url')"
        )
        conn.commit()

    feed = Feed(1, 0, "F", "T", "D", "U", "H")
    with QuiteRssStore(quite_rss_db) as store:
        news_items = store.read_news_items(feed)

    assert len(news_items) == 1
    assert news_items[0].id == 5


def test_read_news_items_url_logic(quite_rss_db):
    """Test URL mapping logic: link_href vs guidislink."""
    with sqlite3.connect(quite_rss_db) as conn:
        cursor = conn.cursor()
        # Item 1: link_href is set, guidislink is ignored
        cursor.execute(
            """
            INSERT INTO news (id, feedId, guid, guidislink, title, published, link_href) 
            VALUES (1, 1, 'guid-1', 'false', 'T1', '2026-01-01T00:00:00', 'https://link.com')
            """
        )
        # Item 2: link_href is empty, guidislink is true -> use guid
        cursor.execute(
            """
            INSERT INTO news (id, feedId, guid, guidislink, title, published, link_href) 
            VALUES (2, 1, 'https://guid-link.com', 'true', 'T2', '2026-01-01T00:00:00', NULL)
            """
        )
        # Item 3: link_href is empty, guidislink is false -> skip
        cursor.execute(
            """
            INSERT INTO news (id, feedId, guid, guidislink, title, published, link_href) 
            VALUES (3, 1, 'guid-3', 'false', 'T3', '2026-01-01T00:00:00', '')
            """
        )
        conn.commit()

    feed = Feed(1, 0, "F", "T", "D", "U", "H")
    with QuiteRssStore(quite_rss_db) as store:
        news_items = store.read_news_items(feed)

    assert len(news_items) == 2
    # Check Item 1: link_href used
    assert news_items[0].id == 1
    assert news_items[0].url == "https://link.com"
    # Check Item 2: guid used
    assert news_items[1].id == 2
    assert news_items[1].url == "https://guid-link.com"
