"""Data-access constraints found in Phase 1 are enforced in code."""
from pathlib import Path

from dayzero.adapters import manual


def test_no_automated_devpost_adapter_exists(repo_root):
    adapters = list((repo_root / "src" / "dayzero" / "adapters").glob("*.py"))
    names = {p.stem for p in adapters}
    assert "devpost" not in names
    for p in adapters:
        text = p.read_text(encoding="utf-8").lower()
        # devpost may only be MENTIONED as a policy note, never fetched
        if "devpost" in text:
            assert "http" not in text.split("devpost")[1][:200] or "robots" in text


def test_manual_hackathon_path_exists_and_is_labelled():
    assert manual.has_automated_hackathon_adapter() is False
    rec = manual.validate_hackathon({"name": "X", "year": 2026,
                                     "official_url": "https://example.org"})
    assert rec["import_mode"] == "MANUAL_RESEARCH_SOURCE"


def test_manual_event_requires_sourcing_fields():
    import pytest
    with pytest.raises(manual.ManualImportError):
        manual.validate_event({"name": "x", "date": "2026-01-01"})


def test_event_attendance_defaults_to_not_attended():
    rec = manual.validate_event({"name": "x", "date": "2026-01-01",
                                 "official_url": "u", "theme": "t",
                                 "why_relevant": "w", "sourcing_objective": "s"})
    assert rec["attendance_status"] == "NOT_ATTENDED"


def test_manual_files_declare_their_limitation(repo_root):
    hk = (repo_root / "data" / "manual" / "hackathons.yaml").read_text()
    assert "robots" in hk.lower() and "anthropic-ai" in hk


def test_source_types_config_marks_hackathons_manual_only():
    from dayzero.config import load
    cfg = load("source_types.yaml")
    assert cfg["source_types"]["hackathon_official"]["automation"] == "manual_only"
    assert "hackathon" in cfg["manual_only_channels"]
