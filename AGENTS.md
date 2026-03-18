# quiterss2rssguard - Agent Guidelines

## Project Overview

- **Type**: Standalone python script for database migration
- **Python**: 3.10+
- **Package Manager**: uv
- **Databases**: SQLite v3
- **Purpose**: Migrate feed data from QuiteRSS database to RSS Guard database

## Build/Lint/Test Commands

Remember to use `uv` to run python commands.

### Development Commands

- `uv run python -m quiterss2rssguard` - Run the main script
- `uv run poe lint` - Run linting checks (uv lock, ruff format, ruff check, ty check)
- `uv run poe format` - Format code (ruff check --select I --fix, ruff format)

### Testing

There are currently no tests in this project. When adding tests:

- Use `uv run pytest` or `uv run python -m pytest`
- Run a single test: `uv run pytest tests/test_file.py::test_function`
- Run tests in specific directory: `uv run pytest tests/`

## Code Style Guidelines

### Python Style

- Follow PEP 8 style guide
- Use 4-space indentation
- Max line length: 99 characters (configured in pyproject.toml)
- Prefer f-strings over `.format()` or `%` formatting

### Imports

```python
# Standard library imports first
import os
from pathlib import Path

# Third-party imports here

# Local app imports
from .data import Feed
```

### Type Hints

- Use type hints for all function parameters and return values
- Use standard library types (e.g., `str`, `int`, `list`, `dict`)
- Import `typing` only if needed for older Python compatibility features

### Naming Conventions

- Classes: `PascalCase` (e.g., `Feed`, `QuiteRssStore`)
- Functions/methods: `snake_case` (e.g., `read_feeds`, `open`)
- Variables: `snake_case` (e.g., `db_path`, `version_row`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`)
- Database fields: `snake_case` (e.g., `created_at`, `is_active`)

### Error Handling

- Catch specific exceptions rather than bare `except`
- Validate file paths and database connections early
- Use try/except for database operations
- Raise descriptive errors with context (e.g., `ValueError`, `RuntimeError`)

### Logging

- Use python build-in logging framework
- Log messages should start with lowercase (unless first word is an abbreviation)
- Log messages should use logging framework %-style string formatting

### Git Workflow

- Commit messages should be concise and descriptive
- Use imperative mood (e.g., "Add feature", "Fix bug")
- Reference issue numbers if applicable

## Project Structure

- `quiterss2rssguard/` - Main package directory
    - `__main__.py` - Entry point
    - `data.py` - Data models (dataclasses)
    - `__init__.py` - Package initialization
    - `store/quiterss.py` - QuiteRSS database store implementation
- `tests/` - Test directory
- `docs/` - Documentation files

## Database schema doc files

- QuiteRSS info (schema version): docs/quiterss-db-info.md
- QuiteRSS feeds: docs/quiterss-db-feeds.md and docs/quiterss-db-feeds-example.md
- QuiteRSS news items: docs/quiterss-db-news.md
- RSS Guard info (schema version): docs/rssguard-db-info.md
- RSS Guard accounts: docs/rssguard-db-accounts.md
- RSS Guard feeds: docs/rssguard-db-feeds.md
- RSS Guard news items: docs/rssguard-db-messages.md

## Additional Notes

- This is a database migration tool - handle SQLite connections carefully
- Use context managers (`with` statements) for database connections
- Make backups before modifying target database
- Validate data integrity during migration
- Prefer built-in Python libraries (sqlite3, pathlib) over third-party packages
