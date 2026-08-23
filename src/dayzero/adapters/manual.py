"""Manual research import path.

Devpost's robots.txt explicitly disallows `anthropic-ai`, `GPTBot`, `ChatGPT-User`,
`CCBot` and `Google-Extended` (verified 2026-08-22). DAY ZERO therefore has NO
automated hackathon adapter — deliberately. Hackathon and event evidence enters
only through analyst-entered records citing an official page.

Every record imported here carries `import_mode: MANUAL_RESEARCH_SOURCE` so the
limitation stays visible in every downstream output.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

MANUAL_MODE = "MANUAL_RESEARCH_SOURCE"
REQUIRED_HACKATHON = ("name", "year", "official_url")
REQUIRED_EVENT = ("name", "date", "official_url", "theme", "why_relevant",
                  "sourcing_objective")
ATTENDANCE_VALUES = {"NOT_ATTENDED", "PLANNED", "ATTENDED"}


class ManualImportError(ValueError):
    pass


def load_yaml(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data.get("records", []) or []


def validate_hackathon(rec: dict[str, Any]) -> dict[str, Any]:
    for f in REQUIRED_HACKATHON:
        if not rec.get(f):
            raise ManualImportError(f"hackathon record missing {f!r}")
    rec = dict(rec)
    rec["import_mode"] = MANUAL_MODE
    return rec


def validate_event(rec: dict[str, Any]) -> dict[str, Any]:
    for f in REQUIRED_EVENT:
        if not rec.get(f):
            raise ManualImportError(f"event record missing {f!r}")
    rec = dict(rec)
    status = rec.get("attendance_status", "NOT_ATTENDED")
    if status not in ATTENDANCE_VALUES:
        raise ManualImportError(f"attendance_status {status!r} not in {ATTENDANCE_VALUES}")
    # The system never asserts attendance. Only a human may set ATTENDED.
    rec["attendance_status"] = status
    rec["import_mode"] = MANUAL_MODE
    return rec


def has_automated_hackathon_adapter() -> bool:
    """Always False, by policy. Asserted by the test suite."""
    return False
