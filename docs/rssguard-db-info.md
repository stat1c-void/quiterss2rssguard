# RSS Guard database version

Schema:

```sqlite
CREATE TABLE Information
(
    inf_key   VARCHAR(128) NOT NULL UNIQUE CHECK (inf_key != ''), /* Use VARCHAR as MariaDB 10.3 does no support UNIQUE TEXT columns. */
    inf_value TEXT
);
```

Target version data:

```text
  inf_key = schema_version
inf_value = 8
```
