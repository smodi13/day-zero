"""Analyst-time instrumentation: measured, never backfilled, never fabricated."""
import json
from pathlib import Path

from dayzero.analyst_time import AnalystTimer

ROOT = Path(__file__).resolve().parents[1]


def test_timer_measures_a_session(tmp_path):
    t = AnalystTimer(tmp_path / "a.json")
    t.start("x/y", "review")
    s = t.stop("x/y", "review")
    assert s.active_seconds is not None and s.active_seconds >= 0
    assert s.started_at.endswith("Z") and s.ended_at.endswith("Z")


def test_recorded_session_keeps_its_duration(tmp_path):
    t = AnalystTimer(tmp_path / "a.json")
    t.record("x/y", "diligence", 900.0, notes="n")
    assert t.sessions[0].active_seconds == 900.0


def test_summary_never_backfills_earlier_phases(tmp_path):
    t = AnalystTimer(tmp_path / "a.json")
    t.record("x/y", "review", 60.0)
    s = t.summary(intro_ready_count=3)
    assert s["backfilled_earlier_phases"] is False
    assert s["phase"] == "phase3"
    assert "NOT_MEASURED" in s["note"]


def test_per_awu_is_none_when_no_awu(tmp_path):
    t = AnalystTimer(tmp_path / "a.json")
    t.record("x/y", "review", 60.0)
    assert t.summary(intro_ready_count=0)["minutes_per_intro_ready_awu"] is None


def test_phase2_summary_still_reports_not_measured():
    p = ROOT / "outputs" / "phase2_summary.json"
    if not p.exists():
        return
    assert json.loads(p.read_text())["cost"]["human_review_minutes"] == "NOT_MEASURED"
