# quiterss2rssguard

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://github.com/stat1c-void/quiterss2rssguard/blob/main/LICENSE.txt)

A database migration tool that transfers feed data from QuiteRSS to RSS Guard.

## Features

- Migrates all feeds from QuiteRSS to RSS Guard
- Migrates news items (articles) for each feed
- Preserves deleted item states
- Automatic backup of target database
- Date-based filtering for old deleted items
- Duplicate detection to prevent re-migration
- Comprehensive logging and error handling

## Tested Versions

- **QuiteRSS**: v0.19.4 (database schema version 17)
- **RSS Guard**: v4.7.3 (database schema version 8)

## Requirements

- Python 3.11 or higher
- **Pre-requisite**: You must create an RSS/ATOM account in RSS Guard **before** running the migration
    - The tool will use the first available `std-rss` account it finds
- **Recommended**: Ensure the following setting in RSS Guard is *enabled*:
    - Settings → Feeds & articles → Articles → "Ignore changes in article body when new articles are being fetched"

## Installation

Since this project is not published to PyPI, you need to download or clone it first.

### Option 1: Clone with Git (recommended)

```bash
git clone https://github.com/stat1c-void/quiterss2rssguard.git
```

### Option 2: Download Source Archive

1. Download the source code from GitHub (Code → Download ZIP)
2. Extract the archive

## Usage

The tool has no additional runtime dependencies other than Python built-in library.

### Basic Usage

```bash
# Need to run from root repo dir (where pyproject.toml is)
# Run as module
python -m quiterss2rssguard /path/to/feeds.db /path/to/database.db
```

### Command-line Options

```bash
usage: quiterss2rssguard [-h] [--skip-older-than SKIP_OLDER_THAN] source target

Migrate feed data from QuiteRSS to RSS Guard.

positional arguments:
  source                Path to the QuiteRSS source database file.
  target                Path to the RSS Guard target database file.

options:
  -h, --help            show this help message and exit
  --skip-older-than SKIP_OLDER_THAN
                        Skip deleted news items older than N days (default: 365)
```

### Examples

```bash
# Basic migration with defaults
python -m quiterss2rssguard \
  ~/.local/share/QuiteRss/QuiteRss/feeds.db \
  ~/.config/RSS\ Guard\ 4/database/database.db

# Only migrate news items deleted in the last 90 days
python -m quiterss2rssguard \
  --skip-older-than 90 \
  ~/.local/share/QuiteRss/QuiteRss/feeds.db \
  ~/.config/RSS\ Guard\ 4/database/database.db
```

### Typical Database Locations

**QuiteRSS (Source)**

- **Linux**: `~/.local/share/QuiteRss/QuiteRss/feeds.db`
- **Windows**: `C:\Users\[username]\AppData\Local\QuiteRss\QuiteRss\feeds.db`
- **macOS**: `~/Library/Application Support/QuiteRss/QuiteRss/feeds.db`

**RSS Guard (Target)**

- **Linux**: `~/.config/RSS Guard 4/database/database.db`
- **Windows**: `C:\Users\[username]\AppData\Local\RSS Guard4\data\database\database.db`
- **macOS**: `~/Library/Application Support/RSS Guard 4/database/database.db`

**Note**: RSS Guard can run in portable mode, where the data folder is `data4` in the same directory as the executable.
Check the application's "Help → About → Resources" dialog for your exact paths.

**⚠️ Important**: Always back up your databases before running the migration!

## Known Limitations

### Flat Structure

The target feed list is **flat** - folder hierarchy is not migrated. All feeds will appear at the root level in RSS
Guard.

### Manual Metadata Fetch Required

After migration, you should manually run "Fetch metadata" on feeds in RSS Guard:

- ⚠️ If you had customized feed titles, this operation will reset them to the feed's default title

### Deleted Items May Reappear

Old deleted news items may reappear when feeds are updated after migration. This is because RSS Guard fetches fresh
content from the feed, and the tool may have discarded those items during migration (`--skip-older-than`).

## Development

Development environment requires `uv`. Additional tools are expected to be globally available for full dev experience
(for example, via `uv tool`):

* `ruff`
* `ty`
* `poethepoet`

### Setup

```bash
# fork & clone repo
# then:
uv sync
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test
uv run pytest tests/test_file.py::test_function
```

### Code Quality

```bash
# Lint and format check
poe lint

# Format code
poe format
```

## Contributing

Contributions are welcome! Please ensure:

- Code follows PEP 8 style
- All functions have type hints
- New features include tests
- Documentation is updated

## License

[MIT](LICENSE.txt)

## Disclaimer

This tool modifies SQLite database files. **Always back up your databases** before running the migration. The authors
are not responsible for data loss.

## Support

- Report issues: [GitHub Issues](https://github.com/stat1c-void/quiterss2rssguard/issues)
