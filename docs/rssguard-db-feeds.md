# RSS Guard feeds database schema

```sqlite
CREATE TABLE Feeds
(
    id                        INTEGER PRIMARY KEY,
    ordr                      INTEGER NOT NULL CHECK (ordr >= 0),
    title                     TEXT    NOT NULL CHECK (title != ''),
    description               TEXT,
    date_created              BIGINT,
    icon                      BLOB,
    category                  INTEGER NOT NULL CHECK (category >= -1), /* Physical category ID, also root feeds contain -1 here. */
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
    custom_id                 TEXT    NOT NULL CHECK (custom_id != ''), /* Custom ID cannot be empty, it must contain either service-specific ID, or Feeds/id. */
    /* Custom column for (serialized) custom account-specific data. */
    custom_data               TEXT,

    FOREIGN KEY (account_id) REFERENCES Accounts (id) ON DELETE CASCADE
);
```

Example data:

```text
                       id = 1
                     ordr = 0
                    title = Django News
              description = Weekly Django news, articles, projects, and more. Curated by Jeff Triplett &amp; William Vincent.
             date_created = 1773676235119
                     icon = (serialized Qt object (probably a QIcon) captured via QDataStream, base64)
                 category = -1
                   source = https://django-news.com/issues.rss
              update_type = 1
          update_interval = 900
                   is_off = 0
                 is_quiet = 0
                   is_rtl = 0
add_any_datetime_articles = 0
        datetime_to_avoid = 0
   keep_article_customize = 0
       keep_article_count = 0
     keep_unread_articles = 1
    keep_starred_articles = 1
         recycle_articles = 0
            open_articles = 0
               account_id = 1
                custom_id = 1
              custom_data = {
    "encoding": "UTF-8",
    "password": "",
    "post_process": "",
    "protected": 0,
    "source_type": 0,
    "type": 1,
    "username": ""
}


                       id = 2
                     ordr = 1
                    title = DistroWatch - Debian
              description = Latest updates from Debian
             date_created = 1773691594795
                     icon = (serialized Qt object (probably a QIcon) captured via QDataStream, base64)
                 category = -1
                   source = https://distrowatch.com/news/distro/debian.xml
              update_type = 1
          update_interval = 900
                   is_off = 0
                 is_quiet = 0
                   is_rtl = 0
add_any_datetime_articles = 0
        datetime_to_avoid = 0
   keep_article_customize = 0
       keep_article_count = 0
     keep_unread_articles = 1
    keep_starred_articles = 1
         recycle_articles = 0
            open_articles = 0
               account_id = 1
                custom_id = 2
              custom_data = {
    "encoding": "UTF-8",
    "password": "",
    "post_process": "",
    "protected": 0,
    "source_type": 0,
    "type": 1,
    "username": ""
}
```
