# RSS Guard messages database schema

```sqlite
CREATE TABLE Messages
(
    id           INTEGER PRIMARY KEY,
    is_read      INTEGER NOT NULL DEFAULT 0 CHECK (is_read >= 0 AND is_read <= 1),
    is_important INTEGER NOT NULL DEFAULT 0 CHECK (is_important >= 0 AND is_important <= 1),
    is_deleted   INTEGER NOT NULL DEFAULT 0 CHECK (is_deleted >= 0 AND is_deleted <= 1),
    is_pdeleted  INTEGER NOT NULL DEFAULT 0 CHECK (is_pdeleted >= 0 AND is_pdeleted <= 1),
    feed         TEXT    NOT NULL, /* Points to Feeds/custom_id. */
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
    labels       TEXT    NOT NULL DEFAULT ".", /* Holds list of assigned label IDs. */

    FOREIGN KEY (account_id) REFERENCES Accounts (id) ON DELETE CASCADE
);
```

Example data:

```text
          id = 1
     is_read = 0
is_important = 0
  is_deleted = 0
 is_pdeleted = 0
        feed = 1
       title = Django News - 21 PRs in One Week to Django Core! - Mar 13th 2026
         url = https://django-news.com/issues/328
      author = 
date_created = 1773396000000
    contents = (html preview)
  enclosures = []
       score = 0.0
  account_id = 1
   custom_id = https://django-news.com/issues/328
 custom_hash = 
      labels = .

          id = 12
     is_read = 1
is_important = 0
  is_deleted = 1
 is_pdeleted = 0
        feed = 2
       title = Distribution Release: Debian 13
         url = https://distrowatch.com/12521
      author = 
date_created = 1754763418000
    contents = (html preview)
  enclosures = []
       score = 0.0
  account_id = 1
   custom_id = https://distrowatch.com/12521
 custom_hash = 
      labels = .
```
