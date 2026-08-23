"""v2 exploratory re-run over the v1 holdout cohort and negative controls.

LABELLED POST-HOC EVERYWHERE. This is a diagnostic that answers "which design failure
did v2 repair, and what did it cost?" — it is NOT validation, and it never overwrites a
v1 output.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from .config import CONFIG_DIR, DATA_DIR, OUTPUT_DIR
from .v2 import Fact, convergence_v2, v2_hash

OUT = OUTPUT_DIR / "phase3"
POST_HOC = ("POST-HOC EXPLORATORY RE-RUN — NOT OUT-OF-SAMPLE VALIDATION. "
            "v2 was designed after seeing v1 fail on cases whose answers were known.")

# Map the v1 as-of evidence claim_class vocabulary onto v2 modalities.
MODALITY_OF = {
    "construction": "CONSTRUCTION",
    "formation": "FORMATION",
    "identity": "IDENTITY",
    "technical_depth": "CONSTRUCTION",   # depth is a property of what was built
    "commercial": "COMMERCIALIZATION",
    "research": "RESEARCH",
}
# claim_types that describe a distinct kind of fact rather than the same one twice
COLLAB_TYPES = {"sustained_construction"}


def facts_for_case(case_id: str, items: list[dict[str, Any]],
                   cutoff: str) -> list[Fact]:
    facts: list[Fact] = []
    for it in items:
        if it["evidence_date"] > cutoff or not it["artifact_available_at_cutoff"]:
            continue
        modality = MODALITY_OF.get(it["claim_class"], "CONSTRUCTION")
        third_party = it["source_type"] in ("press", "press_release", "hackathon_official")
        facts.append(Fact(modality=modality, observed_at=it["evidence_date"],
                          actor_controlled=not third_party,
                          underlying_event_key="",
                          basis=f"{it['claim_type']}: {it['observed_claim'][:70]}",
                          third_party=third_party))
        # A multi-author commit history is ALSO collaboration evidence — a distinct
        # fact about a distinct thing (other people chose to build it too).
        if it["claim_type"] in COLLAB_TYPES and "authors" in it["observed_claim"]:
            facts.append(Fact("COLLABORATION", it["evidence_date"], True, "",
                              "multiple distinct human authors before the cutoff"))
    return facts


def run_holdout_v2() -> dict[str, Any]:
    cases = yaml.safe_load(
        (CONFIG_DIR / "holdout_manifest.yaml").read_text(encoding="utf-8"))["cases"]
    ev_file = DATA_DIR / "holdout" / "evidence.yaml"
    evidence = (yaml.safe_load(ev_file.read_text(encoding="utf-8")).get("cases", {})
                if ev_file.exists() else {})
    v1 = json.loads((OUTPUT_DIR / "holdout_results.json").read_text(encoding="utf-8"))
    v1_by_case = {c["case_id"]: c for c in v1["cases"]}

    results = []
    for case in cases:
        cid = case["case_id"]
        items = evidence.get(cid, [])
        if not items:
            results.append({"case_id": cid, "company": case["company"],
                            "cutoff_date": case["cutoff_date"],
                            "v1_verdict": v1_by_case[cid]["verdict"],
                            "v2_verdict": "UNKNOWN", "changed": False,
                            "reason": "no recoverable pre-cutoff evidence assembled"})
            continue
        facts = facts_for_case(cid, items, case["cutoff_date"])
        conv = convergence_v2(facts)
        has_construction = any(f.modality == "CONSTRUCTION" for f in facts)
        if conv["converged"]:
            verdict = "PASS"
        elif has_construction:
            verdict = "PARTIAL"
        else:
            verdict = "MISS"
        v1v = v1_by_case[cid]["verdict"]
        results.append({
            "case_id": cid, "company": case["company"],
            "cutoff_date": case["cutoff_date"],
            "v1_verdict": v1v, "v2_verdict": verdict,
            "changed": verdict != v1v,
            "modalities": conv["modalities"], "event_count": conv["event_count"],
            "span_days": conv["span_days"], "checks": conv["checks"],
        })
    tally: dict[str, int] = {}
    for r in results:
        tally[r["v2_verdict"]] = tally.get(r["v2_verdict"], 0) + 1
    return {"label": POST_HOC, "v2_rules_hash": v2_hash(),
            "v1_rules_hash": v1["rules_hash"], "v1_tally": v1["tally"],
            "v2_tally": tally, "cases": results,
            "no_accuracy_claim": ("Ten known portfolio companies cannot produce an "
                                  "accuracy statistic under v1 or v2.")}


# Negative controls, expressed as fact sets rather than live repos so the comparison
# is exact and reproducible offline.
CONTROL_FACTS: dict[str, tuple[str, list[Fact]]] = {
    "NC-1": ("0xSero/turboquant", [
        Fact("CONSTRUCTION", "2026-03-25", True, "", "repo created"),
        Fact("CONSTRUCTION", "2026-03-27", True, "", "2 commits total")]),
    "NC-3": ("zerobootdev/zeroboot", [
        Fact("CONSTRUCTION", "2026-03-15", True, "", "repo created"),
        Fact("FORMATION", "2026-03-19", True, "", "org created"),
        Fact("FORMATION", "2026-03-19", True, "", "domain live")]),
    "NC-3b": ("dipampaul17/KVSplit", [
        Fact("CONSTRUCTION", "2025-05-16", True, "", "repo created"),
        Fact("CONSTRUCTION", "2025-05-21", True, "", "9 commits over 5 days")]),
    "NC-4": ("scrya-com/rotorquant", [
        Fact("CONSTRUCTION", "2026-03-26", True, "", "repo created"),
        Fact("CONSTRUCTION", "2026-04-23", True, "", "abandoned after a month"),
        Fact("FORMATION", "2026-02-04", True, "", "org exists")]),
    "NC-5": ("RyanCodrai/turbovec", [
        Fact("CONSTRUCTION", "2026-03-26", True, "", "repo created"),
        Fact("CONSTRUCTION", "2026-08-21", True, "", "351 owner commits"),
        Fact("IDENTITY", "2026-03-26", True, "", "named owner"),
        Fact("EXTERNAL_VALIDATION", "2026-05-01", True, "", "self-published to PyPI",
             third_party=False)]),
    "NC-7": ("FutureMLS-Lab/OSCAR", [
        Fact("CONSTRUCTION", "2026-05-19", True, "", "repo created"),
        Fact("RESEARCH", "2026-05-18", False, "", "arXiv paper, author overlap verified",
             third_party=True),
        Fact("IDENTITY", "2026-05-19", True, "", "named authors")]),
}


def run_controls_v2() -> dict[str, Any]:
    v1 = json.loads((OUTPUT_DIR / "negative_controls.json").read_text(encoding="utf-8"))
    v1_by_id = {c["control_id"]: c for c in v1["controls"]}
    out = []
    for cid, (subject, facts) in sorted(CONTROL_FACTS.items()):
        conv = convergence_v2(facts)
        v1_state = v1_by_id.get(cid, {}).get("actual_state", "N/A")
        promoted = conv["converged"]
        out.append({
            "control_id": cid, "subject": subject,
            "v1_state": v1_state,
            "v2_converged": promoted,
            "v2_result": "INCORRECTLY_PROMOTED" if promoted else "STILL_REJECTED",
            "failed_checks": [k for k, v in conv["checks"].items() if not v],
            "modalities": conv["modalities"], "event_count": conv["event_count"],
            "rejected_facts": conv["rejected_facts"],
        })
    regressions = [c for c in out if c["v2_result"] == "INCORRECTLY_PROMOTED"]
    return {"label": POST_HOC, "v2_rules_hash": v2_hash(),
            "v1_incorrectly_promoted": v1["tally"].get("INCORRECTLY_PROMOTED", 0),
            "v2_incorrectly_promoted": len(regressions),
            "regressions": regressions, "controls": out,
            "caveat": "Curated control set. This measures design failure modes, not specificity."}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    h = run_holdout_v2()
    c = run_controls_v2()
    (OUT / "v2_holdout_results.json").write_text(
        json.dumps(h, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "v2_negative_controls.json").write_text(
        json.dumps(c, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"v1_tally": h["v1_tally"], "v2_tally": h["v2_tally"],
                      "changed": [r["case_id"] for r in h["cases"] if r["changed"]],
                      "v2_control_regressions": c["v2_incorrectly_promoted"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
