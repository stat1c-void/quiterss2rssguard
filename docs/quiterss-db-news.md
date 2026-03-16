# QuiteRSS news database schema

```sqlite
CREATE TABLE news
(
    id             integer primary key,
    feedId         integer,
    guid           varchar,
    guidislink     varchar default 'true',
    description    varchar,
    content        varchar,
    title          varchar,
    published      varchar,
    modified       varchar,
    received       varchar,
    author_name    varchar,
    author_uri     varchar,
    author_email   varchar,
    category       varchar,
    label          varchar,
    new            integer default 1,
    read           integer default 0,
    starred        integer default 0,
    deleted        integer default 0,
    attachment     varchar,
    comments       varchar,
    enclosure_length,
    enclosure_type,
    enclosure_url,
    source         varchar,
    link_href      varchar,
    link_enclosure varchar,
    link_related   varchar,
    link_alternate varchar,
    contributor    varchar,
    rights         varchar,
    deleteDate     varchar,
    feedParentId   integer default 0
);
CREATE INDEX feedId ON news (feedId);
```
