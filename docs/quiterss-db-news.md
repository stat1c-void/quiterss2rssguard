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

Example data:

```text
              id = 170031
          feedId = 36
            guid = tag:github.com,2008:Repository/260274833/v11.0
      guidislink = true
     description = (html preview)
         content = 
           title = v11.0
       published = 2026-03-10T19:03:37
        modified = 
        received = 2026-03-11T00:24:43
     author_name = PatrickF1
      author_uri = 
    author_email = 
        category = 
           label = 
             new = 0
            read = 0
         starred = 0
         deleted = 0
      attachment = 
        comments = 
enclosure_length = 
  enclosure_type = 
   enclosure_url = 
          source = 
       link_href = https://github.com/PatrickF1/fzf.fish/releases/tag/v11.0
  link_enclosure = 
    link_related = 
  link_alternate = 
     contributor = 
          rights = 
      deleteDate = 
    feedParentId = 0

              id = 169849
          feedId = 39
            guid = RouterOS 7.21.3 [stable]
      guidislink = true
     description = (html preview)
         content = 
           title = RouterOS 7.21.3 [stable]
       published = 2026-02-13T09:50:00
        modified = 
        received = 2026-02-13T18:07:54
     author_name = 
      author_uri = 
    author_email = 
        category = 
           label = 
             new = 0
            read = 0
         starred = 0
         deleted = 0
      attachment = 
        comments = 
enclosure_length = 
  enclosure_type = 
   enclosure_url = 
          source = 
       link_href = https://mikrotik.com/download?v=7.21.3
  link_enclosure = 
    link_related = 
  link_alternate = 
     contributor = 
          rights = 
      deleteDate = 
    feedParentId = 0
```
