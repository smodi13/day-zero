"""Negative-control suite.

Controls run through the SAME evaluation path as live candidates. There is no
control-specific rejection code anywhere — `tests/test_no_special_case.py` asserts
that no module references a control's subject string.

Freeze-gated: controls cannot be tuned after seeing which ones fail.
"""
from __future__ import annotations

import sqlite3
from datetime import date
from typing import Any, Optional

from . import ids, registry
from .config import load
from .freeze import require_frozen
from .review import Candidate, Decision, drop_reason_for_watch, evaluate


def _candidate_from_repo(conn: sqlite3.Connection, full_name: str,
                         signal_index: dict[str, list], as_of: date) -> Optional[Candidate]:
    row = conn.execute("SELECT * FROM repositories WHERE full_name=?",
                       (full_name,)).fetchone()
    if not row:
        return None
    rid = ids.repo_id(full_name)
    con = conn.execute("SELECT * FROM repo_construction WHERE repo_id=?", (rid,)).fetchone()
    repo = {
        "full_name": full_name, "description": row["description"],
        "topics": [], "language": row["language"], "license": row["license"],
        "homepage": row["homepage"], "created_at": row["created_at"],
        "pushed_at": row["pushed_at"], "is_fork": bool(row["is_fork"]),
        "construction": dict(con) if con else {},
    }
    org = conn.execute(
        "SELECT * FROM organizations WHERE host='github.com' AND login=?",
        (row["owner_login"],)).fetchone()
    scope = org["scope"] if org else "unregistered"
    sigs = signal_index.get(full_name, [])
    st = conn.execute("SELECT state FROM formation_state_history WHERE project_id=?"
                      " ORDER BY as_of DESC LIMIT 1", (rid,)).fetchone()
    status = conn.execute("SELECT * FROM status_checks WHERE subject_label=?",
                          (full_name,)).fetchone()
    from .signals import themes_for
    return Candidate(
        key=full_name, person_label=row["owner_login"], repo=repo, signals=sigs,
        identity_confidence=_identity_confidence(conn, row["owner_login"]),
        owner_scope=scope, formation_state=(st["state"] if st else "UNKNOWN"),
        themes=themes_for(repo), analyst_review=None,
        status_check=dict(status) if status else None,
        channels_present={s.channel for s in sigs},
    )


def _identity_confidence(conn: sqlite3.Connection, login: str) -> str:
    row = conn.execute(
        "SELECT b.identity_confidence c FROM builders b JOIN identities i"
        " ON i.person_id=b.person_id WHERE i.channel='github' AND i.handle=?",
        (login,)).fetchone()
    return row["c"] if row else "low"


def run(conn: sqlite3.Connection, signal_index: dict[str, list],
        as_of: date) -> dict[str, Any]:
    manifest = require_frozen()
    cfg = load("negative_control_rules.yaml")["controls"]
    results = []
    for cid, c in cfg.items():
        subject = c["subject"]
        if subject.startswith(("class:", "collision:")):
            results.append({
                "control_id": cid, "name": c["name"], "subject": subject,
                "kind": "class_or_fixture",
                "expected_drop_reason": c["expected_drop_reason"],
                "actual_state": "N/A", "actual_drop_reason": None,
                "result": "COVERED_BY_UNIT_TEST",
                "note": ("class-level control; asserted by the offline test suite rather "
                         "than by a single live subject"),
            })
            continue
        cand = _candidate_from_repo(conn, subject, signal_index, as_of)
        if cand is None:
            results.append({
                "control_id": cid, "name": c["name"], "subject": subject,
                "kind": "repo", "expected_drop_reason": c["expected_drop_reason"],
                "actual_state": "NOT_COLLECTED", "actual_drop_reason": None,
                "result": "NOT_EVALUATED",
                "note": "subject not present in the collected universe",
            })
            continue
        d: Decision = evaluate(cand, as_of)
        actual_reason = d.drop_reason or drop_reason_for_watch(d)
        promoted = d.state == "INTRO_READY"
        if promoted:
            result = "INCORRECTLY_PROMOTED"
        elif d.state in ("DROP", "WATCH"):
            result = ("CORRECTLY_REJECTED" if actual_reason == c["expected_drop_reason"]
                      else "REJECTED_FOR_A_DIFFERENT_REASON")
        else:
            result = "AMBIGUOUS"
        results.append({
            "control_id": cid, "name": c["name"], "subject": subject, "kind": "repo",
            "expected_drop_reason": c["expected_drop_reason"],
            "actual_state": d.state, "actual_drop_reason": actual_reason,
            "failed_requirements": d.failed, "passed_requirements": d.passed,
            "result": result, "note": d.notes,
        })
    tally: dict[str, int] = {}
    for r in results:
        tally[r["result"]] = tally.get(r["result"], 0) + 1
    return {"rules_hash": manifest["combined_hash"], "tally": tally,
            "controls": results,
            "caveat": ("The control set is curated. This measures design failure modes, "
                       "not statistical specificity.")}
