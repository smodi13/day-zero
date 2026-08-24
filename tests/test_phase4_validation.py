"""Phase 4A: unseen validation integrity, identity audit, domain audit."""
import json
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
P4 = ROOT / "outputs" / "phase4"
V1_HASH = "ad0b7ae00630f7948e7c4444440af7c20fed61169370e46e076cd8f575a3566c"
V2_HASH = "435dfb8a568d8f07124125b08566cc9ced48f4d17ef76064978905968287f434"
ORIGINAL_TEN = {"Eventual (Daft)", "Sapiom", "HappyRobot", "Flamingo", "Meibel",
                "Integral", "Mozart Data", "ZecOps", "Era Software", "Wokelo"}


def load(name):
    p = P4 / name
    if not p.exists():
        pytest.skip(f"{name} not generated")
    return json.loads(p.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def manifest():
    return yaml.safe_load((ROOT / "config" / "phase4_unseen_holdout.yaml")
                          .read_text(encoding="utf-8"))


# ------------------------------------------------------- immutability of prior work --
def test_v1_and_v2_hashes_unchanged():
    from dayzero import freeze
    from dayzero.v2 import v2_hash
    assert freeze.combined_hash(freeze.current_hashes()) == V1_HASH
    assert v2_hash() == V2_HASH


def test_prior_results_untouched():
    v1 = json.loads((ROOT / "outputs" / "holdout_results.json").read_text())
    assert v1["tally"] == {"PARTIAL": 2, "MISS": 4, "UNKNOWN": 4}
    v2 = json.loads((ROOT / "outputs" / "phase3" / "v2_holdout_results.json").read_text())
    assert v2["v2_tally"] == {"PASS": 2, "PARTIAL": 1, "UNKNOWN": 4, "MISS": 3}
    h = json.loads((ROOT / "outputs" / "phase3" / "headroom_summary.json").read_text())
    assert h["verdict"] == "PARTIALLY_REPRODUCED"
    s = json.loads((ROOT / "outputs" / "phase3" / "sandlock_diligence.json").read_text())
    assert s["recommendation"] == "ADVANCE_TO_FOUNDER_CONVERSATION"


# --------------------------------------------------------------- cohort integrity --
def test_cohort_bound_to_the_v2_hash(manifest):
    assert manifest["v2_frozen_hash"] == V2_HASH


def test_selection_is_deterministic_and_reproducible(manifest):
    import hashlib
    for c in manifest["cases"]:
        expected = hashlib.sha256(f"{V2_HASH}:{c['case_id']}".encode()).hexdigest()
        assert c["selection_hash"] == expected, c["case_id"]


def test_cases_are_sorted_by_selection_hash(manifest):
    hashes = [c["selection_hash"] for c in manifest["cases"]]
    assert hashes == sorted(hashes)


def test_no_original_holdout_company_reappears(manifest):
    for c in manifest["cases"]:
        assert c["company"] not in ORIGINAL_TEN, c["company"]


def test_manifest_contains_no_outcome_information(manifest):
    blob = " ".join(str(c) for c in manifest["cases"]).lower()
    for banned in ("acquired", "acquisition", "traction", "series b", "series c",
                   "valuation", "revenue", "customers", "outcome", "exit"):
        assert banned not in blob, banned


def test_cutoff_precedes_announcement(manifest):
    for c in manifest["cases"]:
        assert c["cutoff_date"] < c["announcement_date"], c["case_id"]


def test_exclusions_record_a_reason(manifest):
    for e in manifest["excluded_from_eligibility"]:
        assert e["reason"] in {"CUTOFF_DATE_UNRESOLVED", "NO_FINANCING_ANNOUNCEMENT",
                               "ENTITY_AMBIGUOUS"}


# ---------------------------------------------------------------- unseen results --
def test_unseen_run_used_the_frozen_v2_hash():
    assert load("unseen_holdout_results.json")["v2_rules_hash"] == V2_HASH


def test_unseen_run_references_the_freeze_commit():
    r = load("unseen_holdout_results.json")
    assert r["cohort_freeze_commit"] == "662392ab2e9e2eeec6549e08b2819d65aa03d4d8"


def test_unseen_result_is_labelled_correctly():
    lbl = load("unseen_holdout_results.json")["label"]
    assert "UNSEEN V2 DESIGN VALIDATION" in lbl
    assert "NOT investment accuracy" in lbl


def test_no_statistic_is_claimed():
    """Disclaiming a statistic is required; asserting one is forbidden."""
    import re
    r = load("unseen_holdout_results.json")
    blob = json.dumps(r)
    claim = re.compile(r"(\d+\s*%\s*(accuracy|precision|recall|win[ -]?rate)|"
                       r"(accuracy|precision|recall|win[ -]?rate|alpha)\s*[:=]\s*[\d.]+)", re.I)
    m = claim.search(blob)
    assert m is None, f"a performance statistic is asserted: {m.group(0)!r}"
    assert "cannot produce an accuracy" in r["no_statistic_claim"]


def test_no_evidence_postdates_its_cutoff(manifest):
    ev = yaml.safe_load((ROOT / "data" / "phase4" / "evidence.yaml").read_text())["cases"]
    cutoffs = {c["case_id"]: c["cutoff_date"] for c in manifest["cases"]}
    for cid, items in ev.items():
        for it in items:
            if it["artifact_available_at_cutoff"]:
                assert it["evidence_date"] <= cutoffs[cid], (cid, it["claim_type"])


def test_every_verdict_is_from_the_vocabulary():
    for c in load("unseen_holdout_results.json")["cases"]:
        assert c["verdict"] in {"PASS", "PARTIAL", "MISS", "UNKNOWN"}
        assert c["reason"]


def test_cohorts_are_not_presented_as_comparable_scores():
    r = load("unseen_holdout_results.json")
    assert "NOT comparable as scores" in r["for_comparison_only"]["note"]


# ------------------------------------------------------------------ identity audit --
def test_identity_audit_excludes_prohibited_methods():
    a = load("identity_audit.json")
    for m in ("data_brokers", "people_search_sites", "guessed_username_matching",
              "arbitrary_x_username_search", "facial_recognition", "location_inference"):
        assert m in a["methods_excluded"]


def test_identity_states_sum_to_the_universe():
    a = load("identity_audit.json")
    assert sum(a["states"].values()) == a["total_identities"]


def test_only_two_states_may_merge():
    a = load("identity_audit.json")
    assert a["mergeable_identities"] == (a["states"]["VERIFIED_CROSS_LINK"] +
                                         a["states"]["STRONG_ARTIFACT_MATCH"])


def test_bare_at_handles_are_not_counted_as_x_links():
    a = load("identity_audit.json")
    assert a["x_linkable_count"] < a["context"]["identities_with_an_at_handle_in_bio"]
    assert "fuzzy matching v2 forbids" in a["context"]["why_at_handles_are_not_counted"]


def test_no_private_identifiers_exported():
    a = load("identity_audit.json")
    assert a["no_private_identifiers_exported"] is True
    blob = json.dumps(a)
    import re
    assert not re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", blob)


# -------------------------------------------------------------------- domain audit --
def test_domain_audit_excludes_whois():
    d = load("domain_audit.json")
    for m in ("whois_enrichment", "domain_registrant_lookup", "reverse_whois"):
        assert m in d["methods_excluded"]


def test_domain_interpretation_matches_the_numbers():
    d = load("domain_audit.json")
    pct = d["with_a_project_domain_pct"]
    text = d["interpretation"]
    assert f"{pct}%" in text, "interpretation must quote the measured figure exactly"
    if pct > 50:
        assert "minority" not in text.lower()


# ------------------------------------------------------------------ analyst time --
def test_human_time_is_not_fabricated():
    p = P4 / "analyst_time_phase4.json"
    if not p.exists():
        pytest.skip("not generated")
    a = json.loads(p.read_text())
    assert a["HUMAN_ANALYST_ACTIVE_TIME"]["value"] == "NOT_MEASURED"
    assert a["HUMAN_ANALYST_ACTIVE_TIME"]["fabricated"] is False
    assert a["backfilled_earlier_phases"] is False
    assert "NOT human analyst time" in a["HUMAN_ANALYST_ACTIVE_TIME"]["why"]
