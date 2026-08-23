"""Holdout cutoff enforcement and the freeze gate."""
import pytest

from dayzero.holdout import AsOfEvidence, CutoffViolation, enforce_cutoff, load_cases


def E(day, available=True, claim="construction"):
    return AsOfEvidence("t", claim, "o", day, "github_repo", "u", available)


def test_post_cutoff_evidence_is_hard_rejected():
    kept = enforce_cutoff([E("2024-09-30"), E("2024-10-01"), E("2025-01-01")],
                          "2024-09-30")
    assert len(kept) == 1 and kept[0].evidence_date == "2024-09-30"


def test_artifact_must_have_been_available_at_the_cutoff():
    """A later article describing an earlier event is not automatically valid."""
    kept = enforce_cutoff([E("2022-01-01", available=False)], "2024-09-30")
    assert kept == []


def test_undated_evidence_raises():
    with pytest.raises(CutoffViolation):
        enforce_cutoff([AsOfEvidence("t", "c", "o", "", "github_repo", "u", True)],
                       "2024-09-30")


def test_manifest_has_ten_cases_with_cutoffs_and_preregistered_verdicts():
    cases = load_cases()
    assert len(cases) == 10
    for c in cases:
        assert c["cutoff_date"] and c["case_id"] and c["company"]
        assert c["prereg_expected_verdict"] in ("PASS", "PARTIAL", "MISS", "UNKNOWN")


def test_manifest_contains_no_outcome_fields():
    banned = ("outcome", "later_financing", "array_relationship", "acquisition",
              "raised", "series_a", "investor")
    for c in load_cases():
        blob = str(c).lower()
        for b in banned:
            assert b not in blob, f"case {c['case_id']} leaks {b}"


def test_outcomes_live_in_a_separate_file(repo_root):
    assert (repo_root / "data" / "holdout" / "outcomes.yaml").exists()
    manifest = (repo_root / "config" / "holdout_manifest.yaml").read_text()
    assert "Series A" not in manifest and "$" not in manifest


def test_holdout_refuses_without_a_freeze_manifest(monkeypatch, tmp_path):
    from dayzero import freeze
    monkeypatch.setattr(freeze, "MANIFEST_PATH", tmp_path / "absent.json")
    with pytest.raises(freeze.FreezeError) as ei:
        freeze.require_frozen()
    assert "cannot proceed" in str(ei.value)


def test_config_drift_fails_closed(monkeypatch, tmp_path):
    from dayzero import freeze
    import json
    m = {"schema_version": "x", "engine_version": "0", "git_commit": "c",
         "created_at": "2026-01-01T00:00:00Z",
         "files": dict(freeze.current_hashes()), "combined_hash": "deadbeef"}
    m["files"]["intro_queue_rules.yaml"] = "0" * 64
    p = tmp_path / "m.json"
    p.write_text(json.dumps(m))
    monkeypatch.setattr(freeze, "MANIFEST_PATH", p)
    with pytest.raises(freeze.FreezeError) as ei:
        freeze.require_frozen()
    assert "Frozen evaluation configuration has changed" in str(ei.value)
