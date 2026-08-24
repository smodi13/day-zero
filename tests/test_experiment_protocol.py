"""EXP-1 protocol integrity. These run offline and do not require headroom."""
import hashlib
import json
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "experiments" / "headroom_v1.yaml"
MANIFEST = ROOT / "experiments" / "headroom" / "datasets" / "manifest.json"


@pytest.fixture(scope="module")
def cfg():
    return yaml.safe_load(CONFIG.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def manifest():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_claim_recorded_verbatim_from_two_sources(cfg):
    ids = {c["id"] for c in cfg["claims"]}
    assert {"CLAIM-SRC-A", "CLAIM-SRC-B"} <= ids
    for c in cfg["claims"]:
        assert c["source"] and c["accessed_at"]
        assert len(c["text"]) > 30


def test_claim_is_decomposed_into_independent_components(cfg):
    assert set(cfg["testable_claims"]) == {"CLAIM-A", "CLAIM-B", "CLAIM-C",
                                           "CLAIM-D", "CLAIM-E"}


def test_minification_baseline_is_present_and_primary(cfg):
    ids = {b["id"] for b in cfg["baselines"]}
    assert {"RAW", "MINIFIED", "COMPACT_JSON", "HEADROOM"} <= ids
    assert cfg["primary_comparison"] == "HEADROOM vs MINIFIED"


def test_multiple_tokenizers(cfg):
    assert len(cfg["tokenizers"]) >= 2
    assert cfg["report_per_tokenizer"] is True


def test_no_single_combined_score_allowed(cfg):
    assert cfg["report"]["forbid_single_combined_score"] is True


def test_quality_test_is_not_llm_judged(cfg):
    q = cfg["quality_test"]
    assert q["llm_calls"] == 0
    assert q["paid_resources"] is False
    assert q["method"] == "exact_value_retention"
    assert q["stated_limitation"].strip()


def test_verdict_thresholds_are_pre_registered(cfg):
    th = cfg["thresholds"]
    for k in ("structured_json_vs_minified_median_pct",
              "structured_json_vs_raw_band_pct",
              "coding_context_vs_raw_median_pct",
              "probe_retention_pass", "probe_retention_fail"):
        assert k in th
    assert set(cfg["verdicts"]) == {"REPRODUCED", "PARTIALLY_REPRODUCED",
                                    "NOT_REPRODUCED", "INCONCLUSIVE"}


def test_dataset_meets_declared_minimums(cfg, manifest):
    for cat, spec in cfg["dataset"]["categories"].items():
        assert manifest["categories"].get(cat, 0) >= spec["min_samples"], cat


def test_manifest_hash_is_deterministic(manifest):
    recomputed = hashlib.sha256(
        json.dumps(manifest["samples"], sort_keys=True).encode()).hexdigest()
    assert recomputed == manifest["manifest_sha256"]


def test_every_sample_has_provenance_and_probes(manifest):
    for s in manifest["samples"]:
        assert s["provenance"], s["sample_id"]
        assert s["provenance"].get("public") is True, s["sample_id"]
        assert 1 <= len(s["probes"]) <= 8, s["sample_id"]


def _present(s):
    """Whether a sample's file is available to check in this checkout.

    The manifest is a frozen, pre-registered artifact listing all 35 samples, so
    it is never edited when one is withheld for third-party privacy. Instead the
    file-level checks skip a sample only when its file is genuinely absent AND a
    published disclosure exists for it — a missing file with no disclosure is
    still a hard failure.
    """
    if (ROOT / s["path"]).exists():
        return True
    disclosure = ROOT / "experiments/headroom/datasets/withheld" / f"{s['sample_id']}.md"
    assert disclosure.exists(), (
        f"{s['sample_id']}: sample file missing and no withheld-sample disclosure at "
        f"{disclosure.relative_to(ROOT)}")
    return False


def test_sample_files_match_their_recorded_hash(manifest):
    checked = 0
    for s in manifest["samples"]:
        if not _present(s):
            continue
        content = (ROOT / s["path"]).read_text(encoding="utf-8")
        assert hashlib.sha256(content.encode()).hexdigest() == s["sha256"], s["sample_id"]
        checked += 1
    assert checked >= 34, f"only {checked} samples verifiable; expected at least 34"


def test_probes_are_present_in_every_original(manifest):
    """A probe absent from the original would make retention meaningless."""
    for s in manifest["samples"]:
        if not _present(s):
            continue
        content = (ROOT / s["path"]).read_text(encoding="utf-8")
        for p in s["probes"]:
            assert p in content, f"{s['sample_id']}: probe {p!r} absent from original"


def test_withheld_samples_are_disclosed_and_exceptional(manifest):
    """Withholding must stay rare and documented, never a routine convenience."""
    withheld = [s for s in manifest["samples"] if not (ROOT / s["path"]).exists()]
    assert len(withheld) <= 1, f"too many withheld: {[s['sample_id'] for s in withheld]}"
    for s in withheld:
        doc = ROOT / "experiments/headroom/datasets/withheld" / f"{s['sample_id']}.md"
        text = doc.read_text(encoding="utf-8")
        assert s["sha256"] in text, "the original sample hash must remain published"
        assert "withheld" in text.lower()


def test_no_sample_leakage_between_categories(manifest):
    ids = [s["sample_id"] for s in manifest["samples"]]
    assert len(ids) == len(set(ids))


def test_no_private_data_in_samples(manifest):
    for s in manifest["samples"]:
        prov = s["provenance"]
        assert prov["kind"] in {"github_api_response", "dayzero_canonical_output",
                                "public_repo_file", "self_produced", "synthetic"}
