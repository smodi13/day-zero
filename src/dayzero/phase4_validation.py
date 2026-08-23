"""Phase 4 — UNSEEN v2 validation.

Runs the FROZEN v2 rules, unchanged, over a cohort selected and committed before any
pre-cutoff evidence was retrieved. This is out-of-sample with respect to **v2's rule
design**. It is NOT investment-performance validation: every case is a known Array
portfolio company.

The evaluation semantics are byte-identical to the Phase 3 v2 re-run
(`v2_rerun.run_holdout_v2`): converged -> PASS, construction present -> PARTIAL,
otherwise MISS; no evidence -> UNKNOWN.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from .config import CONFIG_DIR, DATA_DIR, OUTPUT_DIR
from .v2 import Fact, convergence_v2, v2_hash
from .v2_rerun import MODALITY_OF, POST_HOC

MANIFEST = CONFIG_DIR / "phase4_unseen_holdout.yaml"
EVIDENCE = DATA_DIR / "phase4" / "evidence.yaml"
OUT = OUTPUT_DIR / "phase4"

LABEL = ("UNSEEN V2 DESIGN VALIDATION — out-of-sample with respect to v2 RULE DEVELOPMENT. "
         "NOT investment accuracy, alpha, precision, recall or win rate. Every case is a "
         "known Array portfolio company, so hindsight bias remains.")


def facts_for(items: list[dict[str, Any]], cutoff: str) -> list[Fact]:
    facts: list[Fact] = []
    for it in items:
        if it["evidence_date"] > cutoff or not it["artifact_available_at_cutoff"]:
            continue
        modality = MODALITY_OF.get(it["claim_class"], "CONSTRUCTION")
        if it["claim_class"] == "collaboration":
            modality = "COLLABORATION"
        third = it["source_type"] in ("press", "press_release")
        facts.append(Fact(modality=modality, observed_at=it["evidence_date"],
                          actor_controlled=not third, underlying_event_key="",
                          basis=f"{it['claim_type']}: {it['observed_claim'][:80]}",
                          third_party=third))
    return facts


def run() -> dict[str, Any]:
    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["v2_frozen_hash"] == v2_hash(), \
        "v2 rules changed since the cohort was frozen — STOP"
    evidence = (yaml.safe_load(EVIDENCE.read_text(encoding="utf-8")).get("cases", {})
                if EVIDENCE.exists() else {})

    results = []
    for case in manifest["cases"]:
        cid = case["case_id"]
        items = evidence.get(cid, [])
        if not items:
            results.append({
                "case_id": cid, "company": case["company"],
                "cutoff_date": case["cutoff_date"], "verdict": "UNKNOWN",
                "evidence_count": 0, "modalities": [], "event_count": 0, "span_days": 0,
                "checks": {},
                "reason": "no verifiable pre-cutoff evidence: no GitHub organisation could "
                          "be linked to the company under v2 identity rules (name-only "
                          "matches may not merge)"})
            continue
        facts = facts_for(items, case["cutoff_date"])
        conv = convergence_v2(facts)
        has_construction = any(f.modality == "CONSTRUCTION" for f in facts)
        verdict = "PASS" if conv["converged"] else ("PARTIAL" if has_construction else "MISS")
        results.append({
            "case_id": cid, "company": case["company"],
            "cutoff_date": case["cutoff_date"], "verdict": verdict,
            "evidence_count": len(facts), "modalities": conv["modalities"],
            "event_count": conv["event_count"], "span_days": conv["span_days"],
            "checks": conv["checks"],
            "reason": ("all convergence checks satisfied" if conv["converged"]
                       else "failed: " + ", ".join(k for k, v in conv["checks"].items() if not v))})

    tally: dict[str, int] = {}
    for r in results:
        tally[r["verdict"]] = tally.get(r["verdict"], 0) + 1

    v1 = json.loads((OUTPUT_DIR / "holdout_results.json").read_text(encoding="utf-8"))
    v2_exp = json.loads((OUTPUT_DIR / "phase3" / "v2_holdout_results.json")
                        .read_text(encoding="utf-8"))
    payload = {
        "label": LABEL,
        "v2_rules_hash": v2_hash(),
        "cohort_freeze_commit": "63cfcefdb54ce9d95b57e0e9a3b54be3988f2516",
        "cohort_size": len(manifest["cases"]),
        "eligible_count": manifest["eligible_count"],
        "tally": tally,
        "cases": results,
        "for_comparison_only": {
            "v1_original_holdout": v1["tally"],
            "v2_post_hoc_rerun_same_cohort": v2_exp["v2_tally"],
            "note": ("Different cohorts. These are NOT comparable as scores — the original "
                     "ten were infrastructure-heavy, these nine are application-heavy.")},
        "no_statistic_claim": ("Nine known-outcome cases cannot produce an accuracy, "
                              "precision, recall or win-rate statistic, and none is reported."),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "unseen_holdout_results.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    p = run()
    print(json.dumps({"tally": p["tally"],
                      "cases": [(c["case_id"], c["company"], c["verdict"])
                                for c in p["cases"]]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
