"""Analyst-review time instrumentation.

Phase 2 correctly refused to invent analyst-review time and reported it as NOT_MEASURED.
Phase 3 starts measuring it. Phase 1 and Phase 2 are NEVER backfilled — a fabricated
baseline would be worse than no baseline.

Elapsed time is measured with a monotonic clock, never wall-clock subtraction.
"""
from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Optional

from .config import OUTPUT_DIR
from .timeutil import now_utc, to_rfc3339

LOG_PATH = OUTPUT_DIR / "phase3" / "analyst_time.json"


@dataclass
class ReviewSession:
    candidate: str
    action: str
    phase: str = "phase3"
    started_at: str = ""
    ended_at: str = ""
    active_seconds: Optional[float] = None
    notes: str = ""


class AnalystTimer:
    """Records real review sessions. Never estimates, never backfills."""

    def __init__(self, path: Path = LOG_PATH) -> None:
        self.path = path
        self.sessions: list[ReviewSession] = []
        self._open: dict[str, tuple[ReviewSession, float]] = {}

    def start(self, candidate: str, action: str, notes: str = "") -> ReviewSession:
        s = ReviewSession(candidate=candidate, action=action,
                          started_at=to_rfc3339(now_utc()), notes=notes)
        self._open[f"{candidate}|{action}"] = (s, time.monotonic())
        return s

    def stop(self, candidate: str, action: str) -> ReviewSession:
        key = f"{candidate}|{action}"
        if key not in self._open:
            raise KeyError(f"no open session for {key}")
        s, t0 = self._open.pop(key)
        s.ended_at = to_rfc3339(now_utc())
        s.active_seconds = round(time.monotonic() - t0, 2)
        self.sessions.append(s)
        return s

    def record(self, candidate: str, action: str, active_seconds: float,
               notes: str = "") -> ReviewSession:
        """Record a session whose duration was measured outside this process."""
        s = ReviewSession(candidate=candidate, action=action,
                          started_at=to_rfc3339(now_utc()),
                          ended_at=to_rfc3339(now_utc()),
                          active_seconds=round(float(active_seconds), 2), notes=notes)
        self.sessions.append(s)
        return s

    def summary(self, intro_ready_count: int) -> dict[str, Any]:
        total = sum(s.active_seconds or 0 for s in self.sessions)
        return {
            "phase": "phase3",
            "backfilled_earlier_phases": False,
            "sessions": [asdict(s) for s in self.sessions],
            "session_count": len(self.sessions),
            "total_active_seconds": round(total, 2),
            "total_active_minutes": round(total / 60, 2),
            "intro_ready_count": intro_ready_count,
            "minutes_per_intro_ready_awu": (round(total / 60 / intro_ready_count, 2)
                                            if intro_ready_count else None),
            "note": ("Phase 3 onward only. Phase 1 and Phase 2 analyst time was never "
                     "measured and is reported as NOT_MEASURED rather than estimated."),
        }

    def flush(self, intro_ready_count: int) -> dict[str, Any]:
        payload = self.summary(intro_ready_count)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n",
                             encoding="utf-8")
        return payload
