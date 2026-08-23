"""Intro-queue eligibility comes from the frozen config; analyst input is separate."""
from datetime import date

from dayzero.config import load
from dayzero.review import Candidate, current_three, evaluate
from dayzero.signals import DerivedSignal


def base_signals():
    return [
        DerivedSignal("B-01", "BUILD", "r", "repository", "2026-01-01", "github", "OBSERVED", ""),
        DerivedSignal("D-01", "TECHNICAL_DEPTH", "r", "repository", "2026-01-01", "github", "OBSERVED", ""),
        DerivedSignal("F-01", "FORMATION", "r", "repository", "2026-02-01", "web", "OBSERVED", ""),
        DerivedSignal("F-02", "FORMATION", "o", "organization", "2026-03-01", "github", "OBSERVED", ""),
    ]


def cand(**kw):
    d = dict(key="k", person_label="p",
             repo={"description": "agent sandbox isolation runtime", "topics": [],
                   "language": "Rust", "homepage": "https://x.dev",
                   "construction": {"days_since_push": 5}},
             signals=base_signals(), identity_confidence="high",
             owner_scope="unregistered", formation_state="FORMING",
             themes=["agent_execution_isolation"],
             analyst_review={"technical_question": "q",
                             "commercial_or_formation_question": "q"},
             status_check=None, channels_present={"github", "web"})
    d.update(kw)
    return Candidate(**d)


AS_OF = date(2026, 8, 23)


def test_baseline_candidate_is_intro_ready():
    assert evaluate(cand(), AS_OF).state == "INTRO_READY"


def test_low_identity_confidence_blocks_promotion():
    d = evaluate(cand(identity_confidence="low"), AS_OF)
    assert d.state != "INTRO_READY"


def test_established_org_owner_is_dropped():
    d = evaluate(cand(owner_scope="established_organization"), AS_OF)
    assert d.drop_reason == "ALREADY_ESTABLISHED"


def test_abandonment_drops():
    sigs = base_signals() + [DerivedSignal("V-06", "VELOCITY", "r", "repository",
                                           "2026-03-01", "github", "OBSERVED", "")]
    assert evaluate(cand(signals=sigs), AS_OF).drop_reason == "ABANDONED"


def test_out_of_thesis_drops():
    d = evaluate(cand(repo={"description": "a plain text budget tracker", "topics": [],
                            "language": "Rust", "homepage": None,
                            "construction": {"days_since_push": 5}}), AS_OF)
    assert d.drop_reason == "OUTSIDE_THESIS"


def test_publicly_funded_status_drops_as_too_late():
    d = evaluate(cand(status_check={"status": "institutional_round_public"}), AS_OF)
    assert d.drop_reason == "STATUS_TOO_LATE"


def test_stale_project_is_watch_not_intro_ready():
    d = evaluate(cand(repo={"description": "agent sandbox isolation", "topics": [],
                            "language": "Rust", "homepage": "https://x.dev",
                            "construction": {"days_since_push": 400}}), AS_OF)
    assert d.state != "INTRO_READY"


def test_missing_analyst_questions_yields_review_not_intro_ready():
    d = evaluate(cand(analyst_review=None), AS_OF)
    assert d.state == "REVIEW"


def test_current_three_not_emitted_below_three():
    assert current_three([{"analyst_rank": 1}, {"analyst_rank": 2}]) == []


def test_current_three_is_never_padded():
    rules = load("intro_queue_rules.yaml")["current_3"]
    assert rules["never_pad"] is True
    assert rules["emit_only_if_at_least"] == 3


def test_current_three_emitted_at_three():
    got = current_three([{"analyst_rank": 3}, {"analyst_rank": 1}, {"analyst_rank": 2}])
    assert [g["analyst_rank"] for g in got] == [1, 2, 3]


def test_eligibility_requirements_come_from_config():
    req = load("intro_queue_rules.yaml")["intro_ready_requirements"]
    assert req["x_alone_can_promote"] is False
    assert req["requires_cross_source_convergence"] is True
    assert req["identity_confidence_min"] == "high"
