import sqlite3
from datetime import date
from pathlib import Path

import pytest

from dayzero.build import Builder
from dayzero.config import DATA_DIR
from dayzero.db import connect

AS_OF = date(2026, 8, 23)
PINNED_NOW = "2026-08-23T00:00:00Z"


@pytest.fixture(scope="session")
def built(tmp_path_factory) -> Builder:
    """One deterministic build over the committed collected data. No network."""
    db = tmp_path_factory.mktemp("db") / "t.db"
    b = Builder(db_path=db, as_of=AS_OF, now=PINNED_NOW)
    b.run()
    return b


@pytest.fixture(scope="session")
def conn(built) -> sqlite3.Connection:
    return built.conn


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]
