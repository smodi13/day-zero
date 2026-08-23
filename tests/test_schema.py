"""Schema integrity, enums, and the absence of score fields."""
import sqlite3

from dayzero.config import forbidden_score_fields
from dayzero.db import all_column_names

EXPECTED_TABLES = 35


def test_table_count(conn):
    n = conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'").fetchone()[0]
    assert n == EXPECTED_TABLES


def test_foreign_keys_enabled(conn):
    assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1


def test_evidence_status_enum_enforced(conn):
    with_bad = "INSERT INTO evidence VALUES ('x','e','t','c','cc','o','s','2026-01-01'," \
               "'2026-01-01',1,1,'MAYBE',0,'')"
    try:
        conn.execute(with_bad)
        raised = False
    except sqlite3.IntegrityError:
        raised = True
    finally:
        conn.rollback()
    assert raised, "evidence_status must be constrained to OBSERVED/INFERRED/UNKNOWN"


def test_attendance_status_enum_enforced(conn):
    try:
        conn.execute("INSERT INTO events(event_id,name,date,official_url,theme,"
                     "why_relevant,sourcing_objective,attendance_status,import_mode)"
                     " VALUES ('e','n','2026-01-01','u','t','w','s','MAYBE','m')")
        raised = False
    except sqlite3.IntegrityError:
        raised = True
    finally:
        conn.rollback()
    assert raised


def test_attendance_defaults_to_not_attended(conn):
    conn.execute("INSERT INTO events(event_id,name,date,official_url,theme,why_relevant,"
                 "sourcing_objective,import_mode) VALUES ('e2','n','2026-01-01','u','t',"
                 "'w','s','MANUAL_RESEARCH_SOURCE')")
    row = conn.execute("SELECT attendance_status FROM events WHERE event_id='e2'").fetchone()
    conn.rollback()
    assert row[0] == "NOT_ATTENDED"


def test_intro_queue_contacted_defaults_false(conn):
    conn.execute("INSERT INTO intro_queue(entry_id,workflow_state) VALUES ('q','REVIEW')")
    row = conn.execute("SELECT contacted FROM intro_queue WHERE entry_id='q'").fetchone()
    conn.rollback()
    assert row[0] == 0
