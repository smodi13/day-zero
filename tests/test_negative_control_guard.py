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


# `v2_rerun.py` is a DIAGNOSTIC HARNESS, not part of the decision path: it exists to
# replay named controls against v2 and therefore must name them. It is excluded here by
# file, and `test_control_harness_is_not_in_the_decision_path` proves the exclusion is
# safe by asserting no decision module imports it.
DECISION_PATH_EXCLUSIONS = {"v2_rerun.py"}


def test_no_special_case_code_for_any_control_subject(repo_root):
    """The rules must reject controls generically. If a control's subject string
    appears in a decision module, the rejection is not general."""
    subjects = [c["subject"] for c in load("negative_control_rules.yaml")["controls"].values()
                if not c["subject"].startswith(("class:", "collision:"))]
    engine = [p for p in (repo_root / "src" / "dayzero").rglob("*.py")
              if p.name not in DECISION_PATH_EXCLUSIONS]
    offenders = []
    for p in engine:
        text = p.read_text(encoding="utf-8")
        for s in subjects:
            if s in text:
                offenders.append((p.name, s))
    assert offenders == [], f"control subject hard-coded in a decision module: {offenders}"


def test_control_harness_is_not_in_the_decision_path(repo_root):
    """Nothing that decides a candidate's fate may import the control harness."""
    decision_modules = ("review.py", "signals.py", "formation.py", "technical.py",
                        "build.py", "holdout.py", "pipeline.py", "negative_controls.py",
                        "v2.py")
    for name in decision_modules:
        text = (repo_root / "src" / "dayzero" / name).read_text(encoding="utf-8")
        assert "v2_rerun" not in text, f"{name} imports the control harness"


def test_expected_drop_reasons_are_from_the_declared_vocabulary():
    allowed = set(load("review_states.yaml")["drop_reasons"])
    for c in load("negative_control_rules.yaml")["controls"].values():
        assert c["expected_drop_reason"] in allowed
