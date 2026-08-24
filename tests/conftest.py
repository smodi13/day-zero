import sqlite3
from datetime import date
from pathlib import Path

import pytest

from dayzero.build import Builder
from dayzero.config import DATA_DIR
from dayzero.db import connect

AS_OF = date(2026, 8, 23)
PINNED_NOW = "2026-08-23T00:00:00Z"


# Rebuilding the database needs the raw collection caches. Two of them hold bulk
# third-party profile fields and are deliberately absent from the public
# repository (research/prepublication_privacy_audit.md), so the database-backed
# suite skips there rather than failing with misleading assertion errors about
# "missing" research data. In the private working repository the caches are
# present and every one of these tests runs exactly as it always has.
REQUIRED_CACHES = ("github_users.json", "github_orgs.json")


@pytest.fixture(scope="session")
def built(tmp_path_factory) -> Builder:
    """One deterministic build over the committed collected data. No network."""
    missing = [c for c in REQUIRED_CACHES if not (DATA_DIR / "collected" / c).exists()]
    if missing:
        pytest.skip(
            "raw collection caches withheld from the public repository "
            f"({', '.join(missing)}); database-backed tests run in the private "
            "working repository. See data/collected/README.md.")
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
