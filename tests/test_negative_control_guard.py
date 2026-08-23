"""Controls are freeze-gated and there is no control-specific rejection code."""
import re
from pathlib import Path

import pytest

from dayzero.config import load


def test_controls_require_a_freeze_manifest(monkeypatch, tmp_path):
    from dayzero import freeze
    monkeypatch.setattr(freeze, "MANIFEST_PATH", tmp_path / "absent.json")
    with pytest.raises(freeze.FreezeError):
        freeze.require_frozen()


def test_eleven_controls_are_declared():
    controls = load("negative_control_rules.yaml")["controls"]
    assert len(controls) >= 11


def test_no_special_case_code_for_any_control_subject(repo_root):
    """The rules must reject controls generically. If a control's subject string
    appears in the engine, the rejection is not general."""
    subjects = [c["subject"] for c in load("negative_control_rules.yaml")["controls"].values()
                if not c["subject"].startswith(("class:", "collision:"))]
    engine = [p for p in (repo_root / "src" / "dayzero").rglob("*.py")]
    offenders = []
    for p in engine:
        text = p.read_text(encoding="utf-8")
        for s in subjects:
            if s in text:
                offenders.append((p.name, s))
    assert offenders == [], f"control subject hard-coded in engine: {offenders}"


def test_expected_drop_reasons_are_from_the_declared_vocabulary():
    allowed = set(load("review_states.yaml")["drop_reasons"])
    for c in load("negative_control_rules.yaml")["controls"].values():
        assert c["expected_drop_reason"] in allowed
