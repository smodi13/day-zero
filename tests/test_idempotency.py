"""Rebuilding must not duplicate entities, evidence or relationships."""
from datetime import date

from dayzero.build import Builder


def _dupes(conn, table, key):
    return conn.execute(
        f"SELECT COUNT(*) FROM (SELECT {key} FROM {table} GROUP BY {key} HAVING COUNT(*)>1)"
    ).fetchone()[0]


def test_no_duplicate_builders(conn):
    assert _dupes(conn, "builders", "person_id") == 0


def test_no_duplicate_identities(conn):
    assert _dupes(conn, "identities", "channel || '/' || handle") == 0


def test_no_duplicate_repositories(conn):
    assert _dupes(conn, "repositories", "full_name") == 0


def test_no_duplicate_evidence(conn):
    assert _dupes(conn, "evidence", "evidence_id") == 0


def test_no_duplicate_relationships(conn):
    assert _dupes(conn, "relationships", "from_id || kind || to_id") == 0


def test_second_ingest_adds_nothing(tmp_path):
    b = Builder(db_path=tmp_path / "x.db", as_of=date(2026, 8, 23))
    b.run()
    before = {t: b.conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
              for t in ("repositories", "evidence", "relationships", "builders")}
    b.ingest_github()
    b.resolve_people()
    after = {t: b.conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
             for t in before}
    assert before == after
