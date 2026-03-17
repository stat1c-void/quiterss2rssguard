import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def db_file():
    """Create a temporary database file and yield its path."""
    with tempfile.NamedTemporaryFile(suffix=".db") as f:
        db_path = Path(f.name)
        yield db_path
