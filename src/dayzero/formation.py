"""Formation-state computation and history.

States are computed deterministically from the signal set. The ANALYST decides
whether a person is worth an introduction; the SYSTEM decides only whether the
evidence for a state exists. Keeping these separate is what stops the engine from
becoming an opinion generator.

History is preserved: a subject accumulates dated states, never a single collapsed
"current" value.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable, Optional

from ._dates import iso_to_date
from .config import load
from .signals import DerivedSignal

BUILDING = "BUILDING"
COLLABORATING = "COLLABORATING"
FORMING = "FORMING"
LAUNCHED = "LAUNCHED"
FUNDED = "FUNDED"
UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class StateAt:
    state: str
    as_of: str
    supporting: tuple[str, ...]


def _independent_channels(sigs: Iterable[DerivedSignal]) -> int:
    """Channels announced on the same day by the same actor collapse to one
    (Phase 1 near-miss NM-1)."""
    by_day: dict[str, set[str]] = {}
    for s in sigs:
        by_day.setdefault(s.observed_at, set()).add(s.channel)
    channels: set[str] = set()
    for day, chans in by_day.items():
        if len(chans) > 1:
            channels.add(f"coordinated:{day}")
        else:
            channels |= chans
    return len(channels)


def compute_state(signals: list[DerivedSignal], *, author_resolved: bool) -> StateAt:
    """Apply the frozen entry conditions. Only OBSERVED signals may support a state."""
    obs = [s for s in signals if s.evidence_status == "OBSERVED" and not s.negative]
    fams = [s.family for s in obs]
    formation = [s for s in obs if s.family == "FORMATION"]

    supporting: list[str] = []
    state = UNKNOWN

    has_build = "BUILD" in fams
    has_depth = "TECHNICAL_DEPTH" in fams
    if has_build and has_depth and author_resolved:
        state = BUILDING
        supporting = [s.signal_type for s in obs if s.family in ("BUILD", "TECHNICAL_DEPTH")]
    if state == BUILDING and "COLLABORATION" in fams:
        state = COLLABORATING
        supporting += [s.signal_type for s in obs if s.family == "COLLABORATION"]
    if len(formation) >= 2 and _independent_channels(formation) >= 2:
        state = FORMING
        supporting += [s.signal_type for s in formation]
    if any(s.signal_type == "F-07" for s in obs):
        state = LAUNCHED
        supporting += ["F-07"]
    if any(s.signal_type == "F-08" for s in obs):
        state = FUNDED
        supporting += ["F-08"]

    dates = sorted(s.observed_at for s in obs if s.observed_at)
    as_of = dates[-1] if dates else ""
    return StateAt(state, as_of, tuple(sorted(set(supporting))))


def history(signals: list[DerivedSignal], *, author_resolved: bool) -> list[StateAt]:
    """Chronological state history. Signals are replayed in observation order so a
    subject's trajectory (BUILDING -> COLLABORATING -> FORMING) is preserved."""
    dated = sorted([s for s in signals if s.observed_at], key=lambda s: s.observed_at)
    out: list[StateAt] = []
    seen: list[DerivedSignal] = []
    last = None
    for s in dated:
        seen.append(s)
        st = compute_state(seen, author_resolved=author_resolved)
        if st.state != last and st.state != UNKNOWN:
            out.append(StateAt(st.state, s.observed_at, st.supporting))
            last = st.state
    return out


def mark_stale(signals: list[DerivedSignal], as_of: date) -> dict[str, bool]:
    """Formation and velocity signals go stale; construction evidence never does."""
    cfg = load("signal_types.yaml")["families"]
    out: dict[str, bool] = {}
    for s in signals:
        fam = cfg.get(s.family, {})
        if not fam.get("decays"):
            out[s.signal_type] = False
            continue
        d = iso_to_date(s.observed_at)
        limit = fam.get("stale_after_days")
        out[s.signal_type] = bool(d and limit and (as_of - d).days > limit)
    return out
