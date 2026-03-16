# quiterss2rssguard - Agent Guidelines

## Project Overview

- **Type**: Standalone python script
- **Python**: 3.10+
- **Package Manager**: uv
- **Databases**: SQLite v3

Prefer built-in Python library over third-party packages.

## Build/Lint/Test Commands

Remember to use `uv` to run python commands.

### Linting & Formatting

There are convenient shortcuts for for linting and formatting using `poe` task runner:

- `poe lint` - runs uv lock check and ruff linting
- `poe format` - runs ruff formatter

## Code Style Guidelines

### Python Style

- Follow PEP 8 style guide
- Use 4-space indentation
- Max line length: 100 characters
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

### Naming Conventions

- Classes: `PascalCase` (e.g., `MyModel`, `MyViewSet`)
- Functions/methods: `snake_case` (e.g., `get_context_data`)
- Variables: `snake_case` (e.g., `user_input`, `total_count`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`)
- Database fields: `snake_case` (e.g., `created_at`, `is_active`)

### Error Handling

- Catch specific exceptions rather than bare `except`
- Log errors using python logging framework

## Project Structure

(TODO)
