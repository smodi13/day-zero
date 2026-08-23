"""Post-evaluation tests. These validate the RESULTS, not the rules.

They must not be used to change a frozen rule.
"""
import json
from pathlib import Path

import pytest
import yaml

OUT = Path(__file__).resolve().parents[1] / "outputs"
FROZEN_HASH = json.loads((OUT / "frozen_rules_manifest.json").read_text())["combined_hash"]


def _load(name):
    p = OUT / name
    if not p.exists():
        pytest.skip(f"{name} not generated yet")
    return json.loads(p.read_text(encoding="utf-8"))


def test_holdout_used_the_frozen_rules():
    assert _load("holdout_results.json")["rules_hash"] == FROZEN_HASH


def test_negative_controls_used_the_frozen_rules():
    assert _load("negative_controls.json")["rules_hash"] == FROZEN_HASH


def test_intro_queue_used_the_frozen_rules():
    assert _load("intro_queue.json")["rules_hash"] == FROZEN_HASH


def test_no_holdout_evidence_postdates_its_cutoff():
    cases = {c["case_id"]: c["cutoff_date"] for c in _load("holdout_results.json")["cases"]}
    raw = yaml.safe_load(
        (Path(__file__).resolve().parents[1] / "data" / "holdout" / "evidence.yaml")
        .read_text(encoding="utf-8"))["cases"]
    for case_id, items in raw.items():
        cutoff = cases[case_id]
        for it in items:
            if it["artifact_available_at_cutoff"]:
                assert it["evidence_date"] <= cutoff, (
                    f"{case_id}: {it['claim_type']} dated {it['evidence_date']} > {cutoff}")


def test_holdout_verdicts_are_from_the_declared_vocabulary():
    allowed = {"PASS", "PARTIAL", "MISS", "UNKNOWN"}
    for c in _load("holdout_results.json")["cases"]:
        assert c["verdict"] in allowed


def test_every_holdout_case_has_a_preregistered_expectation():
    for c in _load("holdout_results.json")["cases"]:
        assert c["prereg_expected_verdict"] in ("PASS", "PARTIAL", "MISS", "UNKNOWN")


def test_no_negative_control_was_promoted():
    res = _load("negative_controls.json")
    promoted = [c for c in res["controls"] if c["result"] == "INCORRECTLY_PROMOTED"]
    assert promoted == [], f"controls promoted to INTRO_READY: {promoted}"


def test_frontier_lab_control_did_not_promote():
    res = _load("negative_controls.json")
    nc5 = [c for c in res["controls"] if c["control_id"] == "NC-5"][0]
    assert nc5["actual_state"] != "INTRO_READY"


def test_intro_queue_records_no_contact():
    q = _load("intro_queue.json")
    assert q["contacted_anyone"] is False


def test_current_three_only_when_three_qualify():
    q = _load("intro_queue.json")
    if q["current_3_emitted"]:
        assert len(q["current_3"]) == 3 and q["intro_ready_count"] >= 3
    else:
        assert q["current_3"] == []


def test_every_analyst_override_records_state_reason_and_evidence():
    q = _load("intro_queue.json")
    for r in q["intro_queue"]:
        ov = r.get("analyst_override")
        if ov:
            assert ov["original_system_state"]
            assert ov["analyst_state"]
            assert ov["reason"].strip()
            assert ov["evidence"].strip()


def test_analyst_overrides_never_edit_the_system_state():
    q = _load("intro_queue.json")
    for r in q["intro_queue"]:
        ov = r.get("analyst_override")
        if ov:
            assert r["system_state"] == ov["original_system_state"]


def test_every_intro_ready_lead_has_both_questions():
    q = _load("intro_queue.json")
    for r in q["intro_queue"]:
        card = r.get("card") or {}
        assert card.get("technical_artifact")
        assert card.get("why_company_first_sourcing_may_miss_it")
        assert "technical_question" in r["passed_requirements"]
        assert "commercial_or_formation_question" in r["passed_requirements"]


def test_watchlist_entries_state_why_not_ready():
    w = _load("watchlist.json")
    with_reason = [r for r in w["records"] if r.get("why_not_intro_ready")]
    assert len(with_reason) == len(w["records"])


def test_outputs_do_not_claim_statistical_performance():
    """Disclaiming accuracy is required; asserting it is forbidden."""
    import re
    claim = re.compile(r"(\d+\s*%\s*(accuracy|precision|recall)|"
                       r"(accuracy|precision|recall|f1)\s*[:=]\s*\d)", re.I)
    for name in ("holdout_results.json", "negative_controls.json"):
        blob = json.dumps(_load(name))
        m = claim.search(blob)
        assert m is None, f"{name} asserts a performance statistic: {m.group(0)!r}"
    holdout = json.dumps(_load("holdout_results.json")).lower()
    assert "not investment performance" in holdout
    assert "no accuracy or performance statistic is available" in holdout
