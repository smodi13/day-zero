"""DAY ZERO v2 sourcing rules.

v2 is a RESPONSE to two documented v1 failures, and it is POST-HOC relative to the v1
holdout. Anything it produces on historical cases is an exploratory diagnostic, never
out-of-sample validation. v1 is never modified and its results are never replaced.

The two failures:
  1. v1 convergence collapsed all GitHub sub-sources into one channel, so Eventual/Daft —
     three years of multi-contributor systems work — could not reach PASS.
  2. v1 identity confidence read only GitHub profile fields, so a founder who publishes no
     blog URL resolved to `medium` and needed a manual override.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Iterable, Optional

import yaml

from ._dates import iso_to_date
from .config import CONFIG_DIR, OUTPUT_DIR

V2_DIR = CONFIG_DIR / "v2"
V2_FILES = ("convergence_v2.yaml", "identity_v2.yaml", "domain_signal_v2.yaml")
V2_MANIFEST = OUTPUT_DIR / "phase3" / "v2_rule_manifest.json"

VERIFIED_CROSS_LINK = "VERIFIED_CROSS_LINK"
STRONG_ARTIFACT_MATCH = "STRONG_ARTIFACT_MATCH"
POSSIBLE_MATCH = "POSSIBLE_MATCH"
UNRESOLVED = "UNRESOLVED"
MERGEABLE = {VERIFIED_CROSS_LINK, STRONG_ARTIFACT_MATCH}


def load_v2(name: str) -> dict[str, Any]:
    return yaml.safe_load((V2_DIR / name).read_text(encoding="utf-8"))


def v2_hash() -> str:
    payload = {n: load_v2(n) for n in sorted(V2_FILES)}
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def write_manifest(git_commit: str = "PENDING") -> dict[str, Any]:
    from .timeutil import now_utc, to_rfc3339
    files = {n: hashlib.sha256(
        json.dumps(load_v2(n), sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        for n in sorted(V2_FILES)}
    m = {"schema_version": "dayzero-rules-2", "status": "POST_HOC_EXPLORATORY",
         "git_commit": git_commit, "created_at": to_rfc3339(now_utc()),
         "files": files, "combined_hash": v2_hash(),
         "v1_hash_unchanged_note": "v1 remains frozen and is never modified by v2."}
    V2_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    V2_MANIFEST.write_text(json.dumps(m, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return m


# --------------------------------------------------------------------- events --
@dataclass(frozen=True)
class Fact:
    """One asserted fact, with the modality it belongs to and the event it describes."""
    modality: str
    observed_at: str
    actor_controlled: bool          # is the surface controlled by the subject?
    underlying_event_key: str       # facts sharing this key are ONE event
    basis: str = ""
    third_party: bool = False       # required for EXTERNAL_VALIDATION


def dedup_events(facts: Iterable[Fact]) -> list[tuple[str, str, str]]:
    """Collapse facts into distinct (modality, day, event_key) events.

    DEDUP-1  shared underlying_event_key -> one event
    DEDUP-2  same modality + same day + actor-controlled surfaces -> one event
    """
    seen: set[tuple[str, str, str]] = set()
    out: list[tuple[str, str, str]] = []
    for f in facts:
        if f.underlying_event_key:
            key = ("EVENT", "", f.underlying_event_key)
        elif f.actor_controlled:
            key = (f.modality, f.observed_at, "actor_day")
        else:
            key = (f.modality, f.observed_at, f.basis[:40])
        if key in seen:
            continue
        seen.add(key)
        out.append((f.modality, f.observed_at, str(key)))
    return out


def convergence_v2(facts: list[Fact]) -> dict[str, Any]:
    """Independent FACTS, not independent websites."""
    cfg = load_v2("convergence_v2.yaml")
    req = cfg["requirements"]

    valid: list[Fact] = []
    rejected: list[str] = []
    for f in facts:
        if f.modality == "EXTERNAL_VALIDATION" and not f.third_party:
            rejected.append(f"EXTERNAL_VALIDATION from a non-third-party surface: {f.basis[:60]}")
            continue
        valid.append(f)

    events = dedup_events(valid)
    modalities = {m for m, _, _ in events}

    must = set(req["must_include"])
    one_of = set(req["must_include_one_of"])
    spread_cfg = cfg["temporal_spread"]
    days = sorted({d for _, d, _ in events if d})
    span = ((iso_to_date(days[-1]) - iso_to_date(days[0])).days
            if len(days) >= 2 else 0)

    checks = {
        "distinct_modalities": len(modalities) >= req["min_distinct_modalities"],
        "distinct_events": len(events) >= req["min_distinct_events"],
        "includes_construction": must <= modalities,
        "includes_formation_like": bool(one_of & modalities),
        "temporal_spread": span >= spread_cfg["min_span_days"],
    }
    return {"converged": all(checks.values()), "checks": checks,
            "modalities": sorted(modalities), "event_count": len(events),
            "span_days": span, "rejected_facts": rejected}


# ------------------------------------------------------------------- identity --
@dataclass(frozen=True)
class IdentityEvidence:
    kind: str
    subject_name: Optional[str]
    links_profile: bool
    source: str


def identity_state_v2(evidence: list[IdentityEvidence]) -> dict[str, Any]:
    """VERIFIED_CROSS_LINK > STRONG_ARTIFACT_MATCH > POSSIBLE_MATCH > UNRESOLVED.

    Never merges on name similarity, employer or location.
    """
    cfg = load_v2("identity_v2.yaml")
    accepted = set(cfg["states"][VERIFIED_CROSS_LINK]["accepted_evidence"])

    for e in evidence:
        if e.kind in accepted and e.links_profile:
            return {"state": VERIFIED_CROSS_LINK, "may_merge": True,
                    "basis": f"{e.kind} via {e.source}"}

    named = [e for e in evidence if e.subject_name]
    by_name: dict[str, list[IdentityEvidence]] = {}
    for e in named:
        by_name.setdefault(e.subject_name.strip().lower(), []).append(e)
    for name, group in by_name.items():
        sources = {e.source for e in group}
        if len(sources) >= cfg["states"][STRONG_ARTIFACT_MATCH]["requires"]["min_independent_artifacts"]:
            return {"state": STRONG_ARTIFACT_MATCH, "may_merge": True,
                    "basis": f"exact name {name!r} on {len(sources)} independent artifacts: "
                             f"{sorted(sources)}"}
    if named:
        return {"state": POSSIBLE_MATCH, "may_merge": False,
                "basis": "a name appears on only one artifact"}
    return {"state": UNRESOLVED, "may_merge": False, "basis": "no accepted evidence"}


def intro_eligible_identity(state: str) -> bool:
    return state in MERGEABLE
