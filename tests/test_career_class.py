"""Career signal class is OPTIONAL, evidence-backed, and never a positive ranking factor."""
from datetime import date

from dayzero.config import load
from dayzero.review import Candidate, evaluate
from dayzero.signals import DerivedSignal


def test_unclassified_is_the_default_and_is_allowed():
    cfg = load("career_signal_classes.yaml")
    assert cfg["default"] == "UNCLASSIFIED"
    assert cfg["classes"]["UNCLASSIFIED"]["requires_evidence"] is False


def test_unclassified_is_the_majority_and_that_is_acceptable(conn):
    n_all = conn.execute("SELECT COUNT(*) FROM builders").fetchone()[0]
    n_unc = conn.execute(
        "SELECT COUNT(*) FROM builders WHERE career_signal_class='UNCLASSIFIED'").fetchone()[0]
    assert n_unc > 0
    assert n_all > 0


def test_classified_builders_always_carry_evidence(conn):
    n = conn.execute(
        "SELECT COUNT(*) FROM builders WHERE career_signal_class!='UNCLASSIFIED'"
        " AND career_signal_evidence_id IS NULL").fetchone()[0]
    assert n == 0


def test_career_class_ranking_use_is_forbidden_by_config():
    assert load("career_signal_classes.yaml")["ranking_use"] == "forbidden"


def test_forbidden_career_evidence_is_declared():
    forbidden = set(load("career_signal_classes.yaml")["forbidden_evidence"])
    assert {"account_age", "repo_topic", "follower_count", "employer_silence"} <= forbidden


def _candidate(career: str) -> Candidate:
    sigs = [
        DerivedSignal("B-01", "BUILD", "r", "repository", "2026-01-01", "github", "OBSERVED", ""),
        DerivedSignal("D-01", "TECHNICAL_DEPTH", "r", "repository", "2026-01-01", "github", "OBSERVED", ""),
        DerivedSignal("F-01", "FORMATION", "r", "repository", "2026-02-01", "web", "OBSERVED", ""),
        DerivedSignal("F-02", "FORMATION", "o", "organization", "2026-03-01", "github", "OBSERVED", ""),
    ]
    return Candidate("k", "p", {"description": "ebpf sandbox runtime", "topics": [],
                                "language": "C", "homepage": "https://x.dev",
                                "construction": {"days_since_push": 5}},
                     sigs, "high", "unregistered", "FORMING", ["security"],
                     {"technical_question": "q", "commercial_or_formation_question": "q"},
                     None, {"github", "web"})


def test_career_class_does_not_change_eligibility():
    """Same evidence, different career class -> identical decision."""
    a = evaluate(_candidate("YOUNG_BUILDER"), date(2026, 8, 23))
    b = evaluate(_candidate("OPERATOR_TO_FOUNDER"), date(2026, 8, 23))
    c = evaluate(_candidate("UNCLASSIFIED"), date(2026, 8, 23))
    assert a.state == b.state == c.state == "INTRO_READY"


def test_candidate_has_no_career_field_at_all():
    """The eligibility rules literally cannot read career class: it is not on the
    Candidate object the rules receive."""
    assert not hasattr(_candidate("YOUNG_BUILDER"), "career_signal_class")
