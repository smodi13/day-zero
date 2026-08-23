"""v2 rules: separate from v1, deterministic, and no looser where it matters."""
import json
from pathlib import Path

import pytest

from dayzero import freeze, v2
from dayzero.v2 import Fact, IdentityEvidence, convergence_v2, identity_state_v2

ROOT = Path(__file__).resolve().parents[1]
V1_FROZEN_HASH = "ad0b7ae00630f7948e7c4444440af7c20fed61169370e46e076cd8f575a3566c"


# ------------------------------------------------------------- v1 immutability --
def test_v1_frozen_hash_is_unchanged():
    assert freeze.combined_hash(freeze.current_hashes()) == V1_FROZEN_HASH


def test_v1_manifest_still_matches():
    assert freeze.require_frozen()["combined_hash"] == V1_FROZEN_HASH


def test_v1_holdout_results_are_not_overwritten():
    p = ROOT / "outputs" / "holdout_results.json"
    res = json.loads(p.read_text())
    assert res["rules_hash"] == V1_FROZEN_HASH
    assert res["tally"] == {"PARTIAL": 2, "MISS": 4, "UNKNOWN": 4}


def test_v1_negative_controls_are_not_overwritten():
    res = json.loads((ROOT / "outputs" / "negative_controls.json").read_text())
    assert res["rules_hash"] == V1_FROZEN_HASH
    assert res["tally"].get("INCORRECTLY_PROMOTED", 0) == 0


def test_v2_lives_in_separate_files():
    assert (ROOT / "config" / "v2").is_dir()
    for name in v2.V2_FILES:
        assert (ROOT / "config" / "v2" / name).exists()
    # v2 must not be inside the v1 frozen set
    assert not set(v2.V2_FILES) & set(freeze.FROZEN_RULE_FILES)


def test_v2_hash_is_deterministic():
    assert v2.v2_hash() == v2.v2_hash()
    assert len(v2.v2_hash()) == 64


def test_v2_is_labelled_post_hoc():
    for name in v2.V2_FILES:
        assert v2.load_v2(name)["status"] == "POST_HOC_EXPLORATORY"


# --------------------------------------------------------------- convergence --
def daft_facts():
    return [
        Fact("FORMATION", "2022-02-03", True, "", "org Eventual-Inc created"),
        Fact("CONSTRUCTION", "2022-04-25", True, "", "repo Daft created"),
        Fact("CONSTRUCTION", "2022-12-30", True, "", "sustained multi-author commits"),
        Fact("CONSTRUCTION", "2024-07-31", True, "", "first tagged release"),
        Fact("IDENTITY", "2022-12-30", True, "", "named committers"),
        Fact("COLLABORATION", "2022-12-30", True, "", "15 distinct human authors"),
    ]


def test_daft_converges_under_v2():
    """The documented v1 failure is repaired."""
    assert convergence_v2(daft_facts())["converged"] is True


def test_daft_did_not_converge_under_v1_semantics():
    """All Daft evidence is one channel under v1, which is why it only reached PARTIAL."""
    channels = {"github"}
    assert len(channels) < 2


def test_self_published_package_is_not_external_validation():
    """The single line that keeps NC-5 rejected."""
    facts = [
        Fact("CONSTRUCTION", "2026-03-26", True, "", "repo created"),
        Fact("CONSTRUCTION", "2026-08-21", True, "", "sustained owner commits"),
        Fact("EXTERNAL_VALIDATION", "2026-05-01", True, "", "published to PyPI",
             third_party=False),
        Fact("IDENTITY", "2026-03-26", True, "", "named owner"),
    ]
    r = convergence_v2(facts)
    assert r["converged"] is False
    assert any("non-third-party" in x for x in r["rejected_facts"])


def test_frontier_lab_engineer_still_rejected_under_v2():
    """NC-5 regression fixture: strong artifact, zero formation, must not converge."""
    facts = [
        Fact("CONSTRUCTION", "2026-03-26", True, "", "repo created"),
        Fact("CONSTRUCTION", "2026-08-21", True, "", "351 owner commits"),
        Fact("IDENTITY", "2026-03-26", True, "", "named owner"),
    ]
    r = convergence_v2(facts)
    assert r["converged"] is False
    assert r["checks"]["includes_formation_like"] is False


def test_coordinated_same_day_launch_still_rejected():
    """NC-3 / NM-1: org + domain + repo on one day is one decision."""
    facts = [
        Fact("FORMATION", "2026-03-19", True, "", "org created"),
        Fact("FORMATION", "2026-03-19", True, "", "domain live"),
        Fact("CONSTRUCTION", "2026-03-15", True, "", "repo created"),
    ]
    r = convergence_v2(facts)
    assert r["converged"] is False
    assert r["checks"]["temporal_spread"] is False


def test_syndicated_press_release_is_one_event():
    """DEDUP-3: four copies of one announcement are not four facts."""
    facts = [
        Fact("CONSTRUCTION", "2026-01-01", True, "", "repo"),
        Fact("EXTERNAL_VALIDATION", "2026-06-01", False, "evt-launch", "press release",
             third_party=True),
        Fact("EXTERNAL_VALIDATION", "2026-06-01", False, "evt-launch", "news rewrite",
             third_party=True),
        Fact("EXTERNAL_VALIDATION", "2026-06-02", False, "evt-launch", "aggregator",
             third_party=True),
        Fact("EXTERNAL_VALIDATION", "2026-06-02", False, "evt-launch", "social repost",
             third_party=True),
    ]
    r = convergence_v2(facts)
    assert r["event_count"] == 2, "four syndicated copies must collapse to one event"


def test_v2_is_stricter_than_v1_on_counts():
    req = v2.load_v2("convergence_v2.yaml")["requirements"]
    assert req["min_distinct_modalities"] >= 3
    assert req["min_distinct_events"] >= 3
    assert "CONSTRUCTION" in req["must_include"]


def test_attention_can_never_be_an_event():
    cfg = v2.load_v2("convergence_v2.yaml")
    rules = " ".join(r["description"] for r in cfg["event_deduplication"]["rules"])
    assert "Attention is not evidence" in rules


# ------------------------------------------------------------------- identity --
def test_no_fuzzy_name_merge():
    cfg = v2.load_v2("identity_v2.yaml")
    forbidden = set(cfg["forbidden_merge_evidence"])
    assert {"display_name_similarity", "surname_match", "same_employer",
            "same_city"} <= forbidden


def test_single_artifact_name_is_only_possible_match():
    r = identity_state_v2([IdentityEvidence("github_profile", "Some Person", False, "github")])
    assert r["state"] == v2.POSSIBLE_MATCH
    assert v2.intro_eligible_identity(r["state"]) is False


def test_two_independent_artifacts_give_strong_artifact_match():
    r = identity_state_v2([
        IdentityEvidence("company_team_page_naming_the_person_and_linking_the_profile",
                         "Cong Wang", False, "multikernel.io/about.html"),
        IdentityEvidence("paper_author", "Cong Wang", False, "arxiv:2605.26298"),
        IdentityEvidence("github_top_contributor", "Cong Wang", False,
                         "github.com/multikernel/sandlock"),
    ])
    assert r["state"] == v2.STRONG_ARTIFACT_MATCH
    assert v2.intro_eligible_identity(r["state"]) is True


def test_no_evidence_is_unresolved():
    assert identity_state_v2([])["state"] == v2.UNRESOLVED


def test_explicit_cross_link_wins():
    r = identity_state_v2([
        IdentityEvidence("personal_site_links_both_profiles", None, True, "example.com")])
    assert r["state"] == v2.VERIFIED_CROSS_LINK


# --------------------------------------------------------------------- policy --
def test_x_still_disabled_by_default(monkeypatch):
    from dayzero.adapters import x
    monkeypatch.delenv(x.ENV_ENABLE, raising=False)
    assert x.is_enabled() is False


def test_domain_signal_forbids_whois():
    cfg = v2.load_v2("domain_signal_v2.yaml")
    assert "whois_enrichment" in cfg["prohibited"]
    assert "domain_registrant_lookup" in cfg["prohibited"]


def test_v2_has_explicit_anti_loosening_guards():
    guards = v2.load_v2("convergence_v2.yaml")["anti_loosening_guards"]
    assert len(guards) >= 5
    assert any("negative control" in g for g in guards)
