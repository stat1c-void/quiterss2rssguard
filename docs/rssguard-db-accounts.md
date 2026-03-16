# RSS Guard accounts database schema

```sqlite
CREATE TABLE Accounts
(
    id             INTEGER PRIMARY KEY,
    ordr           INTEGER NOT NULL CHECK (ordr >= 0),
    type           TEXT    NOT NULL CHECK (type != ''), /* ID of the account type. Each account defines its own, for example 'ttrss'. */
    proxy_type     INTEGER NOT NULL DEFAULT 0 CHECK (proxy_type >= 0),
    proxy_host     TEXT,
    proxy_port     INTEGER,
    proxy_username TEXT,
    proxy_password TEXT,
    /* Custom column for (serialized) custom account-specific data. */
    custom_data    TEXT
);
```

Example data:

```text
            id = 1
          ordr = 0
          type = std-rss
    proxy_type = 0
    proxy_host = 
    proxy_port = 0
proxy_username = 
proxy_password = 
   custom_data = {
    "icon": "AAAAIABRAFQAaABlAG0AZQBJAGMAbwBuAEUAbgBnAGkAbgBlAAAAJgBhAHAAcABsAGkAYwBhAHQAaQBvAG4ALQByAHMAcwArAHgAbQBs",
    "show_node_important": false,
    "show_node_labels": false,
    "show_node_probes": false,
    "show_node_unread": false,
    "title": "my-account (RSS/ATOM/JSON)"
}
```
