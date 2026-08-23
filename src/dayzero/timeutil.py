"""Timezone-aware UTC discipline.

Concept ported from the audited `~/headline-x-sourcing` engine (see
research/x_integration_phase2.md). Reimplemented here; nothing is imported from
that repository at runtime.

Naive datetimes are rejected at every boundary. This is a correctness requirement,
not a style preference: look-ahead bias in the historical holdout is fundamentally a
timestamp bug.
"""
from __future__ import annotations

import time
from datetime import date, datetime, timezone
from typing import Callable, Optional


class NaiveDatetimeError(ValueError):
    """Raised when a naive (timezone-unaware) datetime crosses a boundary."""


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def ensure_aware_utc(dt: datetime, *, field: str = "datetime") -> datetime:
    if not isinstance(dt, datetime):
        raise NaiveDatetimeError(f"{field}: expected datetime, got {type(dt).__name__}")
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        raise NaiveDatetimeError(f"{field}: naive datetime not allowed; use aware UTC")
    return dt.astimezone(timezone.utc)


def to_rfc3339(dt: datetime, *, field: str = "datetime") -> str:
    return ensure_aware_utc(dt, field=field).isoformat().replace("+00:00", "Z")


def parse_rfc3339(value: str, *, field: str = "timestamp") -> datetime:
    if not isinstance(value, str) or not value:
        raise NaiveDatetimeError(f"{field}: empty/invalid timestamp")
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return ensure_aware_utc(dt, field=field)


def parse_date(value: str, *, field: str = "date") -> date:
    """Parse an ISO date (YYYY-MM-DD) or the date part of an RFC3339 timestamp."""
    if not isinstance(value, str) or len(value) < 10:
        raise ValueError(f"{field}: expected an ISO date, got {value!r}")
    return date.fromisoformat(value[:10])


def days_between(a: date, b: date) -> int:
    return (b - a).days


class Stopwatch:
    """Monotonic elapsed time. Never wall-clock subtraction."""

    def __init__(self, clock: Callable[[], float] = time.monotonic) -> None:
        self._clock = clock
        self._start = clock()

    def elapsed_seconds(self) -> float:
        return self._clock() - self._start
