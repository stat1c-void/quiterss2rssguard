import datetime as dt
import sqlite3

import pytest

from quiterss2rssguard.data import Feed, NewsItem
from quiterss2rssguard.store import RssGuardStore, StoreOperationError, StoreValidationError


@pytest.fixture
def rss_guard_db(db_file):
    """Create a test RSS Guard database with sample data."""
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()

        # Create Information table
        cursor.execute("""
            CREATE TABLE Information
            (
                inf_key   VARCHAR(128) NOT NULL UNIQUE CHECK (inf_key != ''),
                inf_value TEXT
            )
        """)
        cursor.execute(
            "INSERT INTO Information (inf_key, inf_value) VALUES ('schema_version', '8')"
        )

        # Create Accounts table
        cursor.execute("""
            CREATE TABLE Accounts
            (
                id             INTEGER PRIMARY KEY,
                ordr           INTEGER NOT NULL CHECK (ordr >= 0),
                type           TEXT    NOT NULL CHECK (type != ''),
                proxy_type     INTEGER NOT NULL DEFAULT 0 CHECK (proxy_type >= 0),
                proxy_host     TEXT,
                proxy_port     INTEGER,
                proxy_username TEXT,
                proxy_password TEXT,
                custom_data    TEXT
            )
        """)
        cursor.execute("""
            INSERT INTO Accounts (id, ordr, type) VALUES (1, 0, 'std-rss')
        """)

        # Create Feeds table
        cursor.execute("""
            CREATE TABLE Feeds
            (
                id                        INTEGER PRIMARY KEY,
                ordr                      INTEGER NOT NULL CHECK (ordr >= 0),
                title                     TEXT    NOT NULL CHECK (title != ''),
                description               TEXT,
                date_created              BIGINT,
                icon                      BLOB,
                category                  INTEGER NOT NULL CHECK (category >= -1),
                source                    TEXT,
                update_type               INTEGER NOT NULL CHECK (update_type >= 0),
                update_interval           INTEGER NOT NULL DEFAULT 900 CHECK (update_interval >= 1),
                is_off                    INTEGER NOT NULL DEFAULT 0 CHECK (is_off >= 0 AND is_off <= 1),
                is_quiet                  INTEGER NOT NULL DEFAULT 0 CHECK (is_quiet >= 0 AND is_quiet <= 1),
                is_rtl                    INTEGER NOT NULL DEFAULT 0 CHECK (is_rtl >= 0 AND is_rtl <= 1),
                add_any_datetime_articles INTEGER NOT NULL DEFAULT 0 CHECK (add_any_datetime_articles >= 0 AND add_any_datetime_articles <= 1),
                datetime_to_avoid         BIGINT  NOT NULL DEFAULT 0 CHECK (datetime_to_avoid >= 0),
                keep_article_customize    INTEGER NOT NULL DEFAULT 0 CHECK (keep_article_customize >= 0 AND keep_article_customize <= 1),
                keep_article_count        INTEGER NOT NULL DEFAULT 0 CHECK (keep_article_count >= 0),
                keep_unread_articles      INTEGER NOT NULL DEFAULT 1 CHECK (keep_unread_articles >= 0 AND keep_unread_articles <= 1),
                keep_starred_articles     INTEGER NOT NULL DEFAULT 1 CHECK (keep_starred_articles >= 0 AND keep_starred_articles <= 1),
                recycle_articles          INTEGER NOT NULL DEFAULT 0 CHECK (recycle_articles >= 0 AND recycle_articles <= 1),
                open_articles             INTEGER NOT NULL DEFAULT 0 CHECK (open_articles >= 0 AND open_articles <= 1),
                account_id                INTEGER NOT NULL,
                custom_id                 TEXT    NOT NULL CHECK (custom_id != ''),
                custom_data               TEXT,
                FOREIGN KEY (account_id) REFERENCES Accounts (id) ON DELETE CASCADE
            )
        """)

        # Create Messages table
        cursor.execute("""
            CREATE TABLE Messages
            (
                id           INTEGER PRIMARY KEY,
                is_read      INTEGER NOT NULL DEFAULT 0 CHECK (is_read >= 0 AND is_read <= 1),
                is_important INTEGER NOT NULL DEFAULT 0 CHECK (is_important >= 0 AND is_important <= 1),
                is_deleted   INTEGER NOT NULL DEFAULT 0 CHECK (is_deleted >= 0 AND is_deleted <= 1),
                is_pdeleted  INTEGER NOT NULL DEFAULT 0 CHECK (is_pdeleted >= 0 AND is_pdeleted <= 1),
                feed         TEXT    NOT NULL,
                title        TEXT    NOT NULL CHECK (title != ''),
                url          TEXT,
                author       TEXT,
                date_created BIGINT  NOT NULL CHECK (date_created >= 0),
                contents     TEXT,
                enclosures   TEXT,
                score        REAL    NOT NULL DEFAULT 0.0 CHECK (score >= 0.0 AND score <= 100.0),
                account_id   INTEGER NOT NULL,
                custom_id    TEXT,
                custom_hash  TEXT,
                labels       TEXT    NOT NULL DEFAULT ".",
                FOREIGN KEY (account_id) REFERENCES Accounts (id) ON DELETE CASCADE
            )
        """)

        conn.commit()

    yield db_file


def test_open_valid_db(rss_guard_db):
    """Test opening a valid RSS Guard database."""
    with RssGuardStore(rss_guard_db) as store:
        assert store.account_id == 1


def test_open_wrong_version(rss_guard_db):
    """Test that opening a database with wrong schema version raises StoreValidationError."""
    with sqlite3.connect(rss_guard_db) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE Information SET inf_value = '7' WHERE inf_key = 'schema_version'")
        conn.commit()

    with pytest.raises(StoreValidationError, match="Unsupported database schema version"):
        with RssGuardStore(rss_guard_db):
            pass


def test_open_no_std_rss_account(rss_guard_db):
    """Test that opening a database without std-rss account raises StoreValidationError."""
    with sqlite3.connect(rss_guard_db) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Accounts")
        conn.commit()

    with pytest.raises(StoreValidationError, match="No 'std-rss' account found"):
        with RssGuardStore(rss_guard_db):
            pass


def test_store_new_feed(rss_guard_db):
    """Test storing a new feed."""
    feed = Feed(
        id=1,
        mapped_id=0,
        name="Test Feed",
        description="Test Description",
        url="https://example.com/rss",
        url_html="https://example.com",
    )

    with RssGuardStore(rss_guard_db) as store:
        store.store_feed(feed)

    # Verify feed was stored
    with sqlite3.connect(rss_guard_db) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, title, source, custom_id, account_id FROM Feeds WHERE title = ?",
            (feed.name,),
        )
        row = cursor.fetchone()
        assert row is not None
        stored_id, stored_title, stored_source, stored_custom_id, stored_account_id = row
        assert stored_source == feed.url
        assert stored_account_id == 1
        assert stored_custom_id == str(stored_id)  # Should be updated to match id
        assert feed.mapped_id == stored_id


def test_store_existing_feed(rss_guard_db):
    """Test storing an existing feed (Feed.name -> title)."""
    # Insert a feed first
    with sqlite3.connect(rss_guard_db) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Feeds (ordr, title, source, category, update_type, account_id, custom_id)
            VALUES (0, 'Existing Feed', 'https://existing.com/rss', -1, 1, 1, '1')
        """)
        conn.commit()

    feed = Feed(
        id=999,
        mapped_id=0,
        name="Existing Feed",
        description="",
        url="https://new-url.com/rss",
        url_html="",
    )

    with RssGuardStore(rss_guard_db) as store:
        store.store_feed(feed)

    # Verify mapped_id is updated
    assert feed.mapped_id == 1


def test_store_new_news_item(rss_guard_db):
    """Test storing a new news item."""
    feed = Feed(
        id=1,
        mapped_id=1,
        name="Test Feed",
        description="",
        url="https://example.com/rss",
        url_html="",
    )

    news_item = NewsItem(
        id=1,
        mapped_id=0,
        feed=feed,
        guid="test-guid",
        title="Test News",
        author="Test Author",
        url="https://example.com/news/1",
        date=dt.datetime(2023, 1, 1, tzinfo=dt.timezone.utc),
        preview="Test content",
        deleted=False,
    )

    with RssGuardStore(rss_guard_db) as store:
        store.store_news_item(news_item)

    assert news_item.mapped_id != 0

    # Verify message was stored
    with sqlite3.connect(rss_guard_db) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, title, feed, custom_id, date_created FROM Messages WHERE title = ?",
            (news_item.title,),
        )
        row = cursor.fetchone()
        assert row is not None
        stored_id, stored_title, stored_feed_id, stored_custom_id, stored_date = row
        assert stored_id == news_item.mapped_id
        assert stored_title == news_item.title
        assert stored_feed_id == str(feed.mapped_id)
        assert stored_custom_id == news_item.guid
        # date_created should be in milliseconds
        assert stored_date == int(news_item.date.timestamp() * 1000)


def test_store_existing_news_item(rss_guard_db):
    """Test storing an existing news item (by guid)."""
    feed = Feed(
        id=1,
        mapped_id=1,
        name="Test Feed",
        description="",
        url="https://example.com/rss",
        url_html="",
    )

    # Insert a message first
    with sqlite3.connect(rss_guard_db) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO Messages (feed, title, date_created, account_id, custom_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("1", "Existing News", 1672531200000, 1, "existing-guid"),
        )
        conn.commit()

    news_item = NewsItem(
        id=99,
        mapped_id=0,
        feed=feed,
        guid="existing-guid",
        title="New News Title",  # Different title, but same GUID
        author="",
        url="",
        date=dt.datetime(2023, 1, 1, tzinfo=dt.timezone.utc),
        preview="",
        deleted=False,
    )

    with RssGuardStore(rss_guard_db) as store:
        store.store_news_item(news_item)

    # Should map to existing id 1
    assert news_item.mapped_id == 1


def test_store_news_item_unmapped_feed(rss_guard_db):
    """Test storing a news item whose feed has not been mapped yet."""
    feed = Feed(
        id=1,
        mapped_id=0,  # Not mapped
        name="Test Feed",
        description="",
        url="https://example.com/rss",
        url_html="",
    )

    news_item = NewsItem(
        id=1,
        mapped_id=0,
        feed=feed,
        guid="guid",
        title="Title",
        author="",
        url="",
        date=dt.datetime.now(),
        preview="",
        deleted=False,
    )

    with RssGuardStore(rss_guard_db) as store:
        with pytest.raises(StoreOperationError, match="must be stored before its news items"):
            store.store_news_item(news_item)
