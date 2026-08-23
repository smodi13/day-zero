"""Workflow states and the Founder Intro Queue.

Workflow states are NOT investment predictions. There is no score anywhere in this
module; promotion is a conjunction of named, auditable requirements, and every
rejection records which requirement failed.

The queue holds however many leads survive: 0, 1, 2, 3 or more. It is never padded.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Optional

from .config import load
from .signals import DerivedSignal, convergence, is_current, within_array_areas

DISCOVERED, WATCH, REVIEW, INTRO_READY, DROP = (
    "DISCOVERED", "WATCH", "REVIEW", "INTRO_READY", "DROP")


@dataclass
class Candidate:
    """Everything the workflow rules are allowed to look at."""
    key: str
    person_label: str
    repo: dict[str, Any]
    signals: list[DerivedSignal]
    identity_confidence: str
    owner_scope: str
    formation_state: str
    themes: list[str]
    analyst_review: Optional[dict[str, Any]] = None
    status_check: Optional[dict[str, Any]] = None
    channels_present: set[str] = field(default_factory=set)


@dataclass
class Decision:
    state: str
    drop_reason: Optional[str]
    failed: list[str]
    passed: list[str]
    notes: str = ""


def _has(sigs: list[DerivedSignal], family: str) -> bool:
    return any(s.family == family and s.evidence_status == "OBSERVED" and not s.negative
               for s in sigs)


def _abandoned(sigs: list[DerivedSignal]) -> bool:
    return any(s.signal_type == "V-06" for s in sigs)


def evaluate(c: Candidate, as_of: date) -> Decision:
    """Apply the frozen intro-queue rules. Order matters only for reporting."""
    rules = load("intro_queue_rules.yaml")
    req = rules["intro_ready_requirements"]
    passed: list[str] = []
    failed: list[str] = []

    # ---- hard disqualifiers first (each maps to a named drop reason) ----
    if _abandoned(c.signals):
        return Decision(DROP, "ABANDONED", ["abandonment_signal"], passed)
    if c.owner_scope in ("established_organization",):
        return Decision(DROP, "ALREADY_ESTABLISHED", ["owner_scope_established"], passed)
    if not within_array_areas(c.repo):
        return Decision(DROP, "OUTSIDE_THESIS", ["array_relevant_theme"], passed)

    status = (c.status_check or {}).get("status")
    if status in ("institutional_round_public", "acquired", "public_company"):
        return Decision(DROP, "STATUS_TOO_LATE",
                        [f"status:{status}"], passed,
                        notes="publicly financed / already resolved at the research date")

    # ---- requirements ----
    if _has(c.signals, "BUILD"):
        passed.append("real_artifact")
    else:
        failed.append("real_artifact")

    if _has(c.signals, "TECHNICAL_DEPTH"):
        passed.append("technical_depth_signal")
    else:
        failed.append("technical_depth_signal")

    if is_current(c.repo):
        passed.append("current_signal")
    else:
        failed.append("current_signal")

    if c.identity_confidence == req["identity_confidence_min"]:
        passed.append("identity_resolved")
    else:
        failed.append("identity_resolved")

    conv = convergence(c.signals)
    if conv["converged"]:
        passed.append("cross_source_convergence")
    else:
        failed.append("cross_source_convergence")

    if c.formation_state in ("FORMING", "LAUNCHED") or _has(c.signals, "COMMERCIALIZATION"):
        passed.append("formation_or_commercial_evidence")
    else:
        failed.append("formation_or_commercial_evidence")

    if c.themes:
        passed.append("array_relevant_theme")
    else:
        failed.append("array_relevant_theme")

    # X alone can never promote. If the ONLY evidence channel is X, stop here.
    non_x = {ch for ch in c.channels_present if ch != "x"}
    if c.channels_present and not non_x:
        return Decision(DROP, "SINGLE_CHANNEL_ONLY", ["x_alone_cannot_promote"], passed)

    ar = c.analyst_review or {}
    if ar.get("technical_question"):
        passed.append("technical_question")
    else:
        failed.append("technical_question")
    if ar.get("commercial_or_formation_question"):
        passed.append("commercial_or_formation_question")
    else:
        failed.append("commercial_or_formation_question")

    # ---- state assignment ----
    if not failed:
        return Decision(INTRO_READY, None, [], passed)

    # Failing ONLY the analyst-authored fields means it belongs in the review queue.
    analyst_only = {"technical_question", "commercial_or_formation_question"}
    if set(failed) <= analyst_only:
        return Decision(REVIEW, None, failed, passed)

    if "real_artifact" in failed or "technical_depth_signal" in failed:
        return Decision(DROP, "INSUFFICIENT_TECHNICAL_DEPTH", failed, passed)
    if "identity_resolved" in failed and len(failed) == 1:
        return Decision(WATCH, None, failed, passed,
                        notes="identity unresolved: cannot introduce someone you cannot name")
    if "current_signal" in failed:
        return Decision(WATCH, None, failed, passed, notes="no recent construction activity")
    if "formation_or_commercial_evidence" in failed and len(failed) <= 2:
        return Decision(WATCH, None, failed, passed,
                        notes="strong construction, no formation evidence")
    if "cross_source_convergence" in failed:
        return Decision(WATCH, None, failed, passed, notes="single-channel evidence")
    return Decision(WATCH, None, failed, passed)


def drop_reason_for_watch(d: Decision) -> Optional[str]:
    """Map a WATCH decision to the negative-control vocabulary for reporting."""
    if d.state != WATCH:
        return d.drop_reason
    if "identity_resolved" in d.failed:
        return "IDENTITY_UNRESOLVED"
    if "current_signal" in d.failed:
        return "INSUFFICIENT_CURRENT_SIGNAL"
    if "formation_or_commercial_evidence" in d.failed:
        return "NO_FORMATION_EVIDENCE"
    if "cross_source_convergence" in d.failed:
        return "SINGLE_CHANNEL_ONLY"
    return None


def current_three(intro_ready: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Emit a CURRENT 3 only if at least three genuinely qualify. Never padded."""
    rules = load("intro_queue_rules.yaml")["current_3"]
    if not rules.get("enabled"):
        return []
    if len(intro_ready) < rules["emit_only_if_at_least"]:
        return []
    ranked = sorted(intro_ready, key=lambda e: e.get("analyst_rank", 999))
    return ranked[:3]
