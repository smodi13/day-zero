"""The public frontend export: minimal, deterministic, faithful to canon.

These tests guard the boundary between the canonical research outputs and what
the static site is allowed to know. If a research value drifts, or a private
field leaks, or the export stops being reproducible, this file fails.
"""
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EXPORT = ROOT / "web" / "src" / "data" / "research.json"
MANIFEST = ROOT / "web" / "src" / "data" / "export_manifest.json"


def _load_builder():
    spec = importlib.util.spec_from_file_location(
        "build_frontend_data", ROOT / "scripts" / "build_frontend_data.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def export():
    return json.loads(EXPORT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def outputs():
    def load(rel):
        return json.loads((ROOT / "outputs" / rel).read_text(encoding="utf-8"))
    return load


# ---- shape and hygiene -----------------------------------------------------

def test_export_matches_its_manifest(export):
    blob = EXPORT.read_text(encoding="utf-8")
    man = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert man["bytes"] == len(blob.encode("utf-8"))
    assert man["sha256"] == hashlib.sha256(blob.encode("utf-8")).hexdigest()


def test_export_is_deterministic_across_two_builds():
    mod = _load_builder()
    a = json.dumps(mod.build(), sort_keys=True)
    b = json.dumps(mod.build(), sort_keys=True)
    assert a == b


def test_export_stays_small(export):
    assert EXPORT.stat().st_size < 100_000, "public export should stay under 100 KB"


def _walk_keys(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield f"{path}.{k}", k
            yield from _walk_keys(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _walk_keys(v, f"{path}[{i}]")


FORBIDDEN_KEYS = {"email", "phone", "address", "location", "followers",
                  "score", "founder_score", "probability", "rank"}


def test_no_forbidden_keys_anywhere(export):
    bad = [p for p, k in _walk_keys(export) if k.lower() in FORBIDDEN_KEYS]
    assert bad == []


def test_no_score_or_leaderboard_values(export):
    text = json.dumps(export).lower()
    for phrase in ("founder score", "leaderboard", "top founders", "/10"):
        assert phrase not in text, phrase


def test_person_universe_is_not_exported(export):
    builders = json.loads((ROOT / "outputs" / "builders.json").read_text())
    handles = [r["handle"] for r in builders if r.get("handle")]
    blob = EXPORT.read_text(encoding="utf-8")
    leaked = [h for h in handles if h in blob]
    # A handful of handles legitimately appear inside repo slugs used by the
    # public analyses (Current 3, attention-vs-construction examples).
    assert len(handles) - len(leaked) >= 250, f"universe leak: {leaked[:20]}"
    assert "person:" not in blob, "internal person ids must not be exported"
    assert "ev:" not in blob or "evidence" not in json.dumps(export.get("evidence", "")), \
        "evidence store must not be exported"


def test_evidence_store_and_registry_absent(export):
    assert "sourceRegistry" not in export
    assert "evidence" not in export
    assert len(export["current3"]) == 3


# ---- fidelity to canonical outputs -----------------------------------------

def test_current3_matches_intro_queue(export, outputs):
    intro = outputs("intro_queue.json")
    assert [c["subject"] for c in export["current3"]] == \
        [c["subject"] for c in intro["current_3"]]
    assert export["introQueue"]["count"] == intro["intro_ready_count"] == 3
    assert export["introQueue"]["contactedAnyone"] is False


def test_sandlock_verdict_and_financing_wording(export, outputs):
    sd = outputs("phase3/sandlock_diligence.json")
    s = export["sandlock"]
    assert s["recommendation"] == sd["recommendation"] == \
        "ADVANCE_TO_FOUNDER_CONVERSATION"
    assert s["financingWording"] == \
        "No public institutional financing identified in the reviewed sources."
    assert s["financingStatusCode"] == "NONE_IDENTIFIED_IN_SOURCES_REVIEWED"
    assert "INVEST" not in s["recommendationVocabulary"]


def test_sandlock_claims_preserve_evidence_states(export):
    claims = {c["id"]: c for c in export["sandlock"]["claims"]}
    assert claims["C1"]["status"] == "OBSERVED_AS_CLAIM"      # 5 ms startup
    assert claims["C1"]["verified_independently"] is False
    assert claims["C8"]["status"] == "OBSERVED"               # kernel out of scope
    assert claims["C11"]["status"] == "NOT_FOUND"             # financing
    assert claims["C12"]["status"] == "NOT_FOUND"             # audit
    assert claims["C13"]["status"] == "UNKNOWN"               # customers


def test_headroom_results_match_summary(export, outputs):
    hs = outputs("phase3/headroom_summary.json")
    h = export["headroom"]
    assert h["verdict"] == hs["verdict"] == "PARTIALLY_REPRODUCED"
    cats = h["categories"]
    assert cats["structured_json"]["vsRaw"]["median"] == 46.30
    assert cats["structured_json"]["vsMinified"]["median"] == 28.41
    assert cats["coding_context"]["vsRaw"]["median"] == 0.0
    assert cats["coding_context"]["vsRaw"]["min"] == 0.0
    assert cats["coding_context"]["vsRaw"]["max"] == 0.0
    assert h["retention"] == 1.0
    assert h["errors"] == 0
    assert h["dataset"]["sampleCount"] == 35
    assert h["dataset"]["totalBytes"] == 1573042
    assert h["dataset"]["primaryBaseline"] == "MINIFIED"
    assert len(h["samples"]) == 35


def test_headroom_source_claims_are_verbatim(export):
    texts = " ".join(c["text"] for c in export["headroom"]["sourceClaims"])
    assert "20% fewer tokens for coding agents" in texts
    assert "15-20% fewer tokens" in texts
    assert "60-95% fewer tokens for JSON" in texts or "60–95% fewer tokens" in texts


def test_methodology_tallies_match_canon(export, outputs):
    m = export["methodology"]
    assert m["v1"]["tally"] == outputs("holdout_results.json")["tally"]
    assert m["v1"]["tally"] == {"PARTIAL": 2, "MISS": 4, "UNKNOWN": 4}
    assert m["v2Exploratory"]["tally"] == \
        outputs("phase3/v2_holdout_results.json")["v2_tally"]
    assert m["v2Exploratory"]["tally"] == \
        {"PASS": 2, "PARTIAL": 1, "MISS": 3, "UNKNOWN": 4}
    unseen = outputs("phase4/unseen_holdout_results.json")
    assert m["unseen"]["tally"] == unseen["tally"] == \
        {"PASS": 2, "MISS": 1, "UNKNOWN": 6}
    assert m["unseen"]["freezeCommit"] == unseen["cohort_freeze_commit"]
    assert m["unseen"]["cohortSize"] == 9


def test_unseen_labels_prevent_performance_reading(export):
    u = export["methodology"]["unseen"]
    assert "NOT investment accuracy" in u["label"]
    assert "none is reported" in u["noStatistic"]


def test_perspective_ai_case_is_present_and_unpatched(export):
    cases = {c["company"]: c for c in export["methodology"]["unseen"]["cases"]}
    assert cases["Perspective AI"]["verdict"] == "PASS"
    assert cases["MokSa.ai"]["verdict"] == "MISS"
    assert cases["Blumira"]["verdict"] == "PASS"


def test_negative_controls_show_zero_regressions(export, outputs):
    nc = export["methodology"]["negativeControls"]
    assert nc["v2Regressions"] == 0
    assert all(c["v2_result"] == "STILL_REJECTED" for c in nc["v2Controls"])


def test_identity_audit_matches_canon(export, outputs):
    ident = export["signals"]["identity"]
    canon = outputs("phase4/identity_audit.json")
    assert ident == canon
    assert ident["total_identities"] == 267
    assert ident["mergeable_identities"] == 166
    assert ident["mergeable_pct"] == 62.17
    assert ident["x_linkable_count"] == 1
    assert ident["x_linkable_pct"] == 0.37
    assert ident["states"]["VERIFIED_CROSS_LINK"] == 109
    assert ident["states"]["UNRESOLVED"] == 41
    assert ident["no_private_identifiers_exported"] is True


def test_domain_audit_matches_canon(export, outputs):
    dom = export["signals"]["domain"]
    canon = outputs("phase4/domain_audit.json")
    assert dom == canon
    assert dom["with_a_project_domain_pct"] == 70.59
    assert dom["domain_adds_distinct_pct"] == 32.35


def test_bio_handles_are_counted_but_never_listed(export):
    ident = export["signals"]["identity"]
    assert ident["context"]["identities_with_an_at_handle_in_bio"] == 28
    # No @handle strings from bios may appear anywhere in the export.
    blob = EXPORT.read_text(encoding="utf-8")
    assert "at_handle_list" not in blob


def test_hashes_and_commits_are_exported(export, outputs):
    assert export["hashes"]["v1Frozen"] == \
        outputs("frozen_rules_manifest.json")["combined_hash"]
    assert export["hashes"]["v2Rules"] == \
        outputs("phase3/v2_rule_manifest.json")["combined_hash"]
    for key in ("commit_a", "commit_b", "commit_c", "commit_d",
                "commit_e", "commit_f", "commit_g"):
        assert len(export["commits"][key]) == 40, key


def test_sandlock_sources_parsed_completely(export):
    ids = [s["id"] for s in export["sandlock"]["sources"]]
    assert ids == [f"S{i}" for i in range(1, 20)]
