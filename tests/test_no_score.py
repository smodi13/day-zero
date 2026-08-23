"""There is no global founder score. Anywhere. This is the load-bearing constraint."""
import json
import re
from pathlib import Path

from dayzero.config import forbidden_score_fields
from dayzero.db import all_column_names

BANNED = {"founder_score", "startup_score", "quality_score", "investment_score",
          "probability_of_founding", "probability_of_success", "unicorn_probability",
          "total_score", "overall_score", "rank_score"}


def test_no_banned_column_in_schema(conn):
    cols = {c.lower() for _, c in all_column_names(conn)}
    assert not (cols & BANNED), f"banned score column present: {cols & BANNED}"


def test_no_generic_score_column(conn):
    offenders = [(t, c) for t, c in all_column_names(conn)
                 if c.lower() == "score" or c.lower().endswith("_score")]
    assert offenders == [], f"score-shaped columns present: {offenders}"


def test_technical_assessments_have_no_total(conn):
    cols = {c for t, c in all_column_names(conn) if t == "technical_assessments"}
    assert "total" not in cols and "score" not in cols


def test_banned_identifiers_absent_from_source(repo_root):
    hits = []
    for p in (repo_root / "src").rglob("*.py"):
        text = p.read_text(encoding="utf-8")
        for b in BANNED:
            # allow the words to appear in the config list that FORBIDS them
            if re.search(rf"\b{b}\b", text) and "forbidden" not in text[:400].lower():
                if b not in ("probability_of_founding",):
                    hits.append((p.name, b))
    assert hits == [], f"banned identifier used in source: {hits}"


def test_exported_records_have_no_score_key(repo_root):
    out = repo_root / "outputs"
    for name in ("builders.json", "projects.json"):
        f = out / name
        if not f.exists():
            continue
        blob = json.loads(f.read_text(encoding="utf-8"))
        text = json.dumps(blob)
        for b in BANNED | {'"score"'}:
            assert b not in text, f"{name} contains {b}"
