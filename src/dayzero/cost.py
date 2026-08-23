"""Exact-Decimal cost ledger with an append-only audit trail.

Free sources record 0. Sources whose real cost we cannot determine record UNKNOWN.
A cost is never invented.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import Optional

from .money import money_str, parse_money
from .timeutil import now_utc, to_rfc3339


@dataclass(frozen=True)
class CostEvent:
    run_id: str
    source: str
    api: str
    requests: int
    units: int
    unit_label: str
    estimated_cost_usd: Optional[Decimal]   # None == UNKNOWN
    actual_cost_usd: Optional[Decimal]      # None == UNKNOWN
    at: str

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "source": self.source,
            "api": self.api,
            "requests": self.requests,
            "units": self.units,
            "unit_label": self.unit_label,
            "estimated_cost_usd": money_str(self.estimated_cost_usd),
            "actual_cost_usd": money_str(self.actual_cost_usd),
            "at": self.at,
        }


class CostLedger:
    def __init__(self, path: Path, run_id: str) -> None:
        self.path = path
        self.run_id = run_id
        self.events: list[CostEvent] = []

    def record(self, *, source: str, api: str, requests: int, units: int,
               unit_label: str, estimated_cost_usd="0", actual_cost_usd=None) -> CostEvent:
        est = None if estimated_cost_usd is None else parse_money(
            estimated_cost_usd, field=f"{source}.estimated")
        act = None if actual_cost_usd is None else parse_money(
            actual_cost_usd, field=f"{source}.actual")
        ev = CostEvent(self.run_id, source, api, requests, units, unit_label,
                       est, act, to_rfc3339(now_utc()))
        self.events.append(ev)
        return ev

    def total_estimated(self) -> tuple[Decimal, int]:
        """(sum of known estimates, count of UNKNOWN estimates)."""
        total = Decimal("0")
        unknown = 0
        for e in self.events:
            if e.estimated_cost_usd is None:
                unknown += 1
            else:
                total += e.estimated_cost_usd
        return total, unknown

    def flush(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as fh:
            for e in self.events:
                fh.write(json.dumps(e.to_dict(), sort_keys=True) + "\n")
