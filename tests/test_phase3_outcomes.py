"""Phase 3 outcome tests. Validate results; never change a frozen rule."""
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
P3 = ROOT / "outputs" / "phase3"
V1_HASH = "ad0b7ae00630f7948e7c4444440af7c20fed61169370e46e076cd8f575a3566c"


def load(name):
    p = P3 / name
    if not p.exists():
        pytest.skip(f"{name} not generated")
    return json.loads(p.read_text(encoding="utf-8"))


# --------------------------------------------------------------- experiment --
def test_experiment_used_the_pre_registered_protocol():
    import hashlib
    s = load("headroom_summary.json")
    actual = hashlib.sha256(
        (ROOT / "config/experiments/headroom_v1.yaml").read_bytes()).hexdigest()
    assert s["protocol_sha256"] == actual, "protocol changed after the results were produced"


def test_experiment_used_the_frozen_dataset():
    s = load("headroom_summary.json")
    m = json.loads((ROOT / "experiments/headroom/datasets/manifest.json").read_text())
    assert s["manifest_sha256"] == m["manifest_sha256"]


def test_verdict_is_from_the_pre_registered_vocabulary():
    assert load("headroom_summary.json")["verdict"] in {
        "REPRODUCED", "PARTIALLY_REPRODUCED", "NOT_REPRODUCED", "INCONCLUSIVE"}


def test_no_combined_score_in_experiment_output():
    blob = json.dumps(load("headroom_summary.json"))
    for banned in ('"total_score"', '"overall_score"', '"combined_score"'):
        assert banned not in blob


def test_every_claim_reports_value_and_threshold():
    for cid, c in load("headroom_summary.json")["claims"].items():
        assert "supported" in c and "threshold" in c, cid


def test_experiment_reports_distributions_not_just_means():
    s = load("headroom_summary.json")
    d = s["by_variant"]["HEADROOM_A"]["o200k_base"]["structured_json"]["vs_raw"]
    assert {"median", "p25", "p75", "min", "max", "n"} <= set(d)
    assert "mean" not in d


def test_experiment_cost_was_zero():
    env = load("headroom_summary.json")["environment"]
    assert env["paid_api_calls"] == 0
    assert env["gpu"] is False


def test_both_tokenizers_were_measured():
    s = load("headroom_summary.json")
    for t in ("o200k_base", "cl100k_base"):
        assert t in s["by_variant"]["HEADROOM_A"]


def test_supplementary_diagnostics_cannot_change_the_verdict():
    s = load("headroom_supplementary.json")
    assert "cannot change the verdict" in s["label"]
    assert len(s["diagnostics"]) >= 3


def test_probe_retention_is_reported():
    s = load("headroom_summary.json")
    r = s["by_variant"]["HEADROOM_A"]["probe_retention"]
    assert r["overall_rate"] is not None
    assert "by_category" in r


# ---------------------------------------------------------------- sandlock --
def test_every_sandlock_claim_has_a_source_and_status():
    for c in load("sandlock_claims.json")["claims"]:
        assert c.get("source") or c.get("status") in ("UNKNOWN", "NOT_FOUND"), c["id"]
        assert c["status"] in {"OBSERVED", "OBSERVED_AS_CLAIM", "INFERRED",
                               "UNKNOWN", "NOT_FOUND"}, c["id"]


def test_no_unsupported_funding_claim():
    d = load("sandlock_diligence.json")
    assert d["company_status"]["public_institutional_financing"] == \
        "NONE_IDENTIFIED_IN_SOURCES_REVIEWED"
    blob = json.dumps(d) + json.dumps(load("sandlock_claims.json"))
    assert "bootstrapped" not in blob.lower()


def test_recommendation_vocabulary_excludes_invest():
    d = load("sandlock_diligence.json")
    assert "INVEST" not in d["recommendation_vocabulary"]
    assert d["recommendation"] in d["recommendation_vocabulary"]


def test_competitor_facts_are_source_backed():
    for a in load("sandlock_competitors.json")["alternatives"]:
        assert a.get("source"), a["name"]


def test_agentsight_relationship_states_what_is_not_established():
    r = load("sandlock_diligence.json")["agentsight_relationship"]
    assert "not_established" in r
    assert "none inferred" in r["not_established"]


def test_thematic_mirroring_guard_was_applied_and_carries_a_caveat():
    g = load("sandlock_diligence.json")["thematic_mirroring_guard"]
    assert "passed" in g and g["basis"] and g["caveat"]


def test_attention_is_labelled_descriptive_only():
    assert "never a surfacing input" in load("sandlock_diligence.json")["attention"]["note"]


# ---------------------------------------------------------------------- v2 --
def test_v2_results_are_labelled_post_hoc():
    for name in ("v2_holdout_results.json", "v2_negative_controls.json"):
        assert "POST-HOC" in load(name)["label"]
        assert "NOT OUT-OF-SAMPLE VALIDATION" in load(name)["label"]


def test_v2_holdout_preserves_v1_results_alongside():
    h = load("v2_holdout_results.json")
    assert h["v1_rules_hash"] == V1_HASH
    assert h["v1_tally"] == {"PARTIAL": 2, "MISS": 4, "UNKNOWN": 4}
    for c in h["cases"]:
        assert "v1_verdict" in c and "v2_verdict" in c


def test_v2_makes_no_accuracy_claim():
    h = load("v2_holdout_results.json")
    assert "cannot produce an accuracy statistic" in h["no_accuracy_claim"]
    assert "accuracy" not in json.dumps(h["cases"]).lower()


def test_v2_introduced_no_negative_control_regression():
    n = load("v2_negative_controls.json")
    assert n["v2_incorrectly_promoted"] == 0, f"v2 regressions: {n['regressions']}"


def test_nc5_still_rejected_under_v2():
    n = load("v2_negative_controls.json")
    nc5 = [c for c in n["controls"] if c["control_id"] == "NC-5"][0]
    assert nc5["v2_result"] == "STILL_REJECTED"
    assert "includes_formation_like" in nc5["failed_checks"]


def test_daft_is_the_repaired_case():
    h = load("v2_holdout_results.json")
    b1 = [c for c in h["cases"] if c["case_id"] == "B1"][0]
    assert b1["v1_verdict"] == "PARTIAL" and b1["v2_verdict"] == "PASS"
    assert b1["changed"] is True


# ------------------------------------------------------------ analyst time --
def test_analyst_time_is_not_backfilled():
    a = load("analyst_time.json")
    assert a["backfilled_earlier_phases"] is False
    assert a["minutes_per_intro_ready_awu"] is None
    assert a["phase3_review_measured"] is False
