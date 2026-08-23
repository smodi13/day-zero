"""Evidence integrity and claim-specific source authority."""
import pytest

from dayzero.config import load


def test_every_evidence_row_has_a_source(conn):
    n = conn.execute("SELECT COUNT(*) FROM evidence e LEFT JOIN sources s"
                     " ON s.source_id=e.source_id WHERE s.source_id IS NULL").fetchone()[0]
    assert n == 0


def test_evidence_statuses_are_from_the_allowed_set(conn):
    allowed = set(load("evidence_types.yaml")["evidence_status"])
    got = {r[0] for r in conn.execute("SELECT DISTINCT evidence_status FROM evidence")}
    assert got <= allowed


def test_inferred_evidence_is_stored_separately_from_observed(conn):
    n_obs = conn.execute("SELECT COUNT(*) FROM evidence WHERE evidence_status='OBSERVED'").fetchone()[0]
    n_inf = conn.execute("SELECT COUNT(*) FROM evidence WHERE evidence_status='INFERRED'").fetchone()[0]
    assert n_obs > 0 and n_inf > 0, "both classes should exist and be distinguishable"


def test_inferred_signals_cannot_support_a_formation_state():
    from dayzero.formation import compute_state
    from dayzero.signals import DerivedSignal
    inferred = [
        DerivedSignal("B-01", "BUILD", "r", "repository", "2026-01-01", "github", "INFERRED", ""),
        DerivedSignal("D-01", "TECHNICAL_DEPTH", "r", "repository", "2026-01-01", "github", "INFERRED", ""),
    ]
    assert compute_state(inferred, author_resolved=True).state == "UNKNOWN"


def test_unknown_stays_unknown():
    from dayzero.formation import compute_state
    assert compute_state([], author_resolved=True).state == "UNKNOWN"


def test_source_authority_is_claim_specific():
    """A builder's own post is authoritative for the STATEMENT, not for the CLAIM."""
    from dayzero.build import Builder
    b = Builder.__new__(Builder)
    statement = b._authority("x_post", "statement", first_party=True)
    performance = b._authority("x_post", "technical_performance", first_party=True)
    assert statement == 1
    assert performance == 3
    assert statement != performance


def test_first_party_commercial_claim_is_not_authoritative():
    from dayzero.build import Builder
    b = Builder.__new__(Builder)
    assert b._authority("company_site", "commercial", first_party=True) == 3


def test_x_post_about_a_repo_is_not_construction_evidence():
    from dayzero.build import Builder
    b = Builder.__new__(Builder)
    assert b._authority("x_post", "construction", first_party=True) == 3
    assert b._authority("github_repo", "construction", first_party=True) == 1


def test_ai_classifications_table_is_separate_and_empty(conn):
    n = conn.execute("SELECT COUNT(*) FROM ai_classifications").fetchone()[0]
    assert n == 0, "no AI-produced value may be written during a build"


def test_evidence_has_both_timestamps(conn):
    n = conn.execute("SELECT COUNT(*) FROM evidence WHERE evidence_date IS NULL"
                     " OR source_accessed_at IS NULL").fetchone()[0]
    assert n == 0
