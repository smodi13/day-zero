"""AI output is never evidence and never a factual value."""
import inspect
from pathlib import Path

from dayzero import build, formation, review, signals, technical
from dayzero.config import load


def test_ai_policy_forbids_writing_evidence():
    p = load("evidence_types.yaml")["ai_policy"]
    assert p["may_write_evidence"] is False
    assert p["storage_table"] == "ai_classifications"
    assert p["promotion_requires"] == "human_verification_against_source"


def test_ai_table_is_separate_from_evidence(conn):
    ev_cols = {c[1] for c in conn.execute("PRAGMA table_info(evidence)")}
    ai_cols = {c[1] for c in conn.execute("PRAGMA table_info(ai_classifications)")}
    assert "verified_by" in ai_cols and "verified_by" not in ev_cols


def test_no_model_call_in_the_decision_path():
    """No engine module that decides anything may import an LLM client."""
    for mod in (signals, formation, review, technical, build):
        src = inspect.getsource(mod)
        for banned in ("anthropic", "openai", "import llm", "ChatCompletion"):
            assert banned not in src, f"{mod.__name__} references {banned}"


def test_technical_dimension_values_are_constrained():
    import pytest
    from dayzero.technical import DimensionValue
    with pytest.raises(ValueError):
        DimensionValue("systems_depth", "amazing", "OBSERVED", "b")


def test_missing_dimension_is_unknown_not_zero(conn):
    rows = conn.execute(
        "SELECT DISTINCT value FROM technical_assessments"
        " WHERE dimension='technical_difficulty'").fetchall()
    values = {r[0] for r in rows}
    assert values == {"UNKNOWN"}, (
        "technical difficulty must not be guessed from metadata; it is what the "
        "reproduction lab exists to resolve")


def test_every_dimension_row_carries_a_basis(conn):
    n = conn.execute("SELECT COUNT(*) FROM technical_assessments"
                     " WHERE basis IS NULL OR basis=''").fetchone()[0]
    assert n == 0


def test_dimensions_stay_independent(conn):
    """Nine separate rows per subject; no combined row exists."""
    row = conn.execute(
        "SELECT subject_id, COUNT(DISTINCT dimension) n FROM technical_assessments"
        " GROUP BY subject_id ORDER BY n DESC LIMIT 1").fetchone()
    assert row["n"] == 9
