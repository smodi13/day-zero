"""The privacy policy is enforced technically, not just documented."""
import json
import re
from pathlib import Path

from dayzero.db import all_column_names

FORBIDDEN_COLUMNS = {
    "home_address", "address", "street", "postcode", "zip", "phone", "phone_number",
    "mobile", "personal_email", "family", "spouse", "children", "age", "birthdate",
    "dob", "gender", "race", "ethnicity", "nationality", "religion", "political",
    "sexuality", "health", "salary", "precise_location", "gps", "lat", "lon",
    "departure_date", "is_leaving", "job_search",
}

FORBIDDEN_TEXT = re.compile(
    r"(home address|personal phone|phone number|date of birth|marital status|"
    r"is (likely )?leaving|about to quit|planning to leave|resigning from)", re.I)


def test_no_forbidden_columns_in_schema(conn):
    cols = {c.lower() for _, c in all_column_names(conn)}
    assert not (cols & FORBIDDEN_COLUMNS), f"forbidden column: {cols & FORBIDDEN_COLUMNS}"


def test_no_departure_inference_column(conn):
    cols = {c.lower() for _, c in all_column_names(conn)}
    for c in cols:
        assert "departure" not in c and "quitting" not in c


def test_canonical_outputs_contain_no_sensitive_text(repo_root):
    out = repo_root / "outputs"
    for f in out.glob("*.json"):
        text = f.read_text(encoding="utf-8")
        m = FORBIDDEN_TEXT.search(text)
        assert m is None, f"{f.name} contains sensitive phrasing: {m.group(0)!r}"


def test_builders_export_carries_only_professional_fields(repo_root):
    f = repo_root / "outputs" / "builders.json"
    if not f.exists():
        return
    allowed = {"person_id", "display_name", "identity_confidence",
               "career_signal_class", "career_signal_evidence_id",
               "channel", "handle", "profile_url"}
    for rec in json.loads(f.read_text(encoding="utf-8")):
        assert set(rec) <= allowed, f"unexpected field in builders export: {set(rec) - allowed}"


def test_no_email_addresses_in_outputs(repo_root):
    pat = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
    for f in (repo_root / "outputs").glob("*.json"):
        found = pat.findall(f.read_text(encoding="utf-8"))
        assert not found, f"{f.name} contains an email address: {found[:2]}"


def test_events_never_assert_attendance(conn):
    n = conn.execute("SELECT COUNT(*) FROM events WHERE attendance_status='ATTENDED'").fetchone()[0]
    assert n == 0, "the system must never record the operator as having attended"


def test_no_contact_recorded(conn):
    n = conn.execute("SELECT COUNT(*) FROM intro_queue WHERE contacted=1").fetchone()[0]
    assert n == 0
