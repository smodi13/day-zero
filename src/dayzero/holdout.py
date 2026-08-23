"""Historical holdout — design validation, not investment performance.

Two hard guarantees:

  1. **Freeze gate.** Nothing here runs unless `freeze.require_frozen()` passes.
  2. **As-of enforcement.** Every evidence item is rejected unless
     `evidence_date <= cutoff_date` AND the underlying artifact was itself publicly
     available at the cutoff. `source_accessed_at` may be 2026 — retrieving a 2022
     commit today is legitimate; a 2025 article *describing* that 2022 event is not
     automatically valid evidence for what was knowable in 2023.

Post-cutoff outcomes live in a separate file the evaluator never reads.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Optional

import yaml

from ._dates import iso_to_date
from .config import CONFIG_DIR, DATA_DIR, load
from .freeze import require_frozen

PASS, PARTIAL, MISS, UNKNOWN = "PASS", "PARTIAL", "MISS", "UNKNOWN"
EVIDENCE_PATH = DATA_DIR / "holdout" / "evidence.yaml"
MANIFEST = CONFIG_DIR / "holdout_manifest.yaml"

BLINDED_FIELDS = ("array_relationship", "later_financing", "later_outcome",
                  "acquisition", "post_cutoff_traction", "post_cutoff_team_growth")


class CutoffViolation(ValueError):
    pass


@dataclass
class AsOfEvidence:
    claim_type: str
    claim_class: str
    observed_claim: str
    evidence_date: str
    source_type: str
    source_url: str
    artifact_available_at_cutoff: bool
    evidence_status: str = "OBSERVED"


@dataclass
class Packet:
    case_id: str
    company: str
    cutoff_date: str
    evidence: list[AsOfEvidence] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        d = {"case_id": self.case_id, "company": self.company,
             "cutoff_date": self.cutoff_date,
             "evidence": [vars(e) for e in self.evidence]}
        for f in BLINDED_FIELDS:
            assert f not in d, f"blinded field {f} leaked into the packet"
        return d


def load_cases() -> list[dict[str, Any]]:
    return yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))["cases"]


def load_evidence_file() -> dict[str, list[dict[str, Any]]]:
    if not EVIDENCE_PATH.exists():
        return {}
    return yaml.safe_load(EVIDENCE_PATH.read_text(encoding="utf-8")).get("cases", {}) or {}


def enforce_cutoff(items: list[AsOfEvidence], cutoff: str) -> list[AsOfEvidence]:
    """Hard reject. Anything dated after the cutoff, or whose underlying artifact was
    not publicly available at the cutoff, is removed — not down-weighted."""
    cd = date.fromisoformat(cutoff)
    kept: list[AsOfEvidence] = []
    for e in items:
        ed = iso_to_date(e.evidence_date)
        if ed is None:
            raise CutoffViolation(f"evidence {e.claim_type!r} has no usable date")
        if ed > cd:
            continue
        if not e.artifact_available_at_cutoff:
            continue
        kept.append(e)
    return kept


def build_packet(case: dict[str, Any], raw: list[dict[str, Any]]) -> Packet:
    items = [AsOfEvidence(**r) for r in raw]
    kept = enforce_cutoff(items, case["cutoff_date"])
    return Packet(case["case_id"], case["company"], case["cutoff_date"], kept)


def evaluate(packet: Packet) -> dict[str, Any]:
    """Apply the FROZEN pass criteria to pre-cutoff evidence only."""
    rules = load("holdout_rules.yaml")
    criteria = {c: False for c in rules["pass_criteria"]}
    classes = {e.claim_class for e in packet.evidence}
    types = {e.claim_type for e in packet.evidence}

    criteria["build_signal_present"] = "construction" in classes
    criteria["technical_depth_signal_present"] = "technical_depth" in classes
    criteria["author_identity_resolvable"] = "identity" in classes
    channels = {e.source_type for e in packet.evidence}
    independent = {("github" if c.startswith("github") else c) for c in channels}
    criteria["cross_source_convergence"] = (
        len(independent) >= 2 and criteria["build_signal_present"]
        and ("formation" in classes or "technical_depth" in classes))
    criteria["within_array_areas"] = "thesis_area" in types
    criteria["no_disqualifier"] = "disqualifier" not in types

    surfaced = criteria["build_signal_present"] and criteria["technical_depth_signal_present"]
    if not packet.evidence:
        verdict = MISS
    elif all(criteria.values()):
        verdict = PASS
    elif surfaced:
        verdict = PARTIAL
    elif any(criteria.values()):
        verdict = MISS
    else:
        verdict = MISS
    return {"case_id": packet.case_id, "verdict": verdict, "criteria": criteria,
            "evidence_count": len(packet.evidence),
            "channels": sorted(independent)}


def run() -> dict[str, Any]:
    """Freeze-gated. Raises FreezeError if the rules have drifted."""
    manifest = require_frozen()
    cases = load_cases()
    ev = load_evidence_file()
    results = []
    for case in cases:
        raw = ev.get(case["case_id"], [])
        if not raw:
            results.append({"case_id": case["case_id"], "verdict": UNKNOWN,
                            "criteria": {}, "evidence_count": 0, "channels": [],
                            "note": "no recoverable pre-cutoff public evidence assembled"})
            continue
        packet = build_packet(case, raw)
        r = evaluate(packet)
        r["note"] = ""
        results.append(r)
    tally: dict[str, int] = {}
    for r in results:
        tally[r["verdict"]] = tally.get(r["verdict"], 0) + 1
    by_case = {c["case_id"]: c for c in cases}
    for r in results:
        c = by_case[r["case_id"]]
        r["company"] = c["company"]
        r["cutoff_date"] = c["cutoff_date"]
        r["prereg_expected_verdict"] = c.get("prereg_expected_verdict")
    return {
        "naming": "HISTORICAL_HOLDOUT (design validation, not investment performance)",
        "rules_hash": manifest["combined_hash"],
        "manifest_created_at": manifest["created_at"],
        "tally": tally,
        "cases": results,
        "interpretation_caveat": (
            "The cohort is known to consist of Array portfolio companies. No accuracy "
            "or performance statistic is available from ten known cases."),
    }
