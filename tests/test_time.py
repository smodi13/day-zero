"""Timezone discipline and evidence_date vs source_accessed_at semantics."""
from datetime import datetime, timezone

import pytest

from dayzero.timeutil import (NaiveDatetimeError, ensure_aware_utc, parse_date,
                              parse_rfc3339, to_rfc3339)


def test_naive_datetime_is_rejected_at_the_boundary():
    with pytest.raises(NaiveDatetimeError):
        ensure_aware_utc(datetime(2026, 1, 1))


def test_aware_datetime_round_trips():
    dt = datetime(2026, 1, 1, tzinfo=timezone.utc)
    assert to_rfc3339(dt) == "2026-01-01T00:00:00Z"
    assert parse_rfc3339("2026-01-01T00:00:00Z") == dt


def test_parse_date_accepts_rfc3339_prefix():
    assert parse_date("2022-04-25T10:00:00Z").isoformat() == "2022-04-25"


def test_all_stored_timestamps_are_utc_z(conn):
    rows = conn.execute("SELECT source_accessed_at FROM evidence LIMIT 50").fetchall()
    assert rows
    for (ts,) in rows:
        assert ts.endswith("Z"), f"non-UTC timestamp stored: {ts}"


def test_evidence_date_may_predate_access_date(conn):
    """Retrieving a 2022 commit in 2026 is legitimate; the semantics must allow it."""
    n = conn.execute(
        "SELECT COUNT(*) FROM evidence WHERE substr(evidence_date,1,4) < '2026'"
    ).fetchone()[0]
    assert n > 0


def test_evidence_date_is_never_the_access_date_by_accident(conn):
    """If every evidence_date equalled the access date, cutoffs would be meaningless."""
    distinct = conn.execute(
        "SELECT COUNT(DISTINCT evidence_date) FROM evidence").fetchone()[0]
    assert distinct > 10
