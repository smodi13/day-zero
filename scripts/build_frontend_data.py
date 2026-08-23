"""Deterministic frontend data export.

Canonical research outputs -> validated, minimal JSON for the static site.

Two rules this script exists to enforce:
  1. No research value is ever typed into a React component. Everything the site
     asserts comes from `outputs/**` via this script.
  2. Only what a public route needs is exported. The 267-identity universe, the source
     registry, the evidence store and the database never reach the browser.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
WEB_DATA = ROOT / "web" / "src" / "data"
SANDLOCK_SOURCE_AUDIT = ROOT / "research" / "sandlock" / "source_audit.md"
HEADROOM_MANIFEST = ROOT / "experiments" / "headroom" / "datasets" / "manifest.json"

# Fields that must never appear in an exported record.
FORBIDDEN_KEYS = {"email", "phone", "address", "location", "followers", "score",
                  "founder_score", "probability"}


def load(rel: str) -> Any:
    return json.loads((OUT / rel).read_text(encoding="utf-8"))


def git_commits() -> dict[str, str]:
    out = subprocess.run(["git", "log", "--format=%H %s", "-40"], cwd=ROOT,
                         capture_output=True, text=True).stdout.splitlines()
    wanted = {
        "phase1": "Phase 1: research, ontology",
        "commit_a": "Build DAY ZERO sourcing engine and freeze",
        "commit_b": "Run frozen sourcing validation",
        "commit_c": "Pre-register DAY ZERO technical reproduction",
        "commit_d": "Design DAY ZERO v2 sourcing rules",
        "commit_e": "Run technical reproduction and deep diligence",
        "commit_f": "Freeze unseen v2 validation cohort",
        "commit_g": "Run unseen v2 validation and identity audit",
    }
    found: dict[str, str] = {}
    for line in out:
        sha, _, subject = line.partition(" ")
        for key, prefix in wanted.items():
            if subject.startswith(prefix):
                found.setdefault(key, sha)
    return found


def scrub(obj: Any) -> Any:
    """Refuse to export a forbidden field rather than silently dropping it."""
    if isinstance(obj, dict):
        for k in obj:
            if k.lower() in FORBIDDEN_KEYS:
                raise SystemExit(f"forbidden key in export: {k}")
        return {k: scrub(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [scrub(v) for v in obj]
    return obj


def sandlock_sources() -> list[dict[str, str]]:
    """Parse the S-numbered source rows out of the sandlock source audit, so the
    public pages can cite [S5] etc. without shipping the whole registry."""
    rows: list[dict[str, str]] = []
    for line in SANDLOCK_SOURCE_AUDIT.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 3 and cells[0].startswith("**S") and cells[0].endswith("**"):
            sid = cells[0].strip("*")
            src = cells[1].replace("`", "")
            if len(cells) == 4:
                rows.append({"id": sid, "source": src, "type": cells[2],
                             "establishes": cells[3]})
            else:  # secondary-source table: no type column
                rows.append({"id": sid, "source": src, "type": "secondary",
                             "establishes": cells[2]})
    if len(rows) < 17:
        raise SystemExit(f"sandlock source audit parse failure: {len(rows)} rows")
    return rows


def build() -> dict[str, Any]:
    intro = load("intro_queue.json")
    p2 = load("phase2_summary.json")
    v1h = load("holdout_results.json")
    nc = load("negative_controls.json")
    hs = load("phase3/headroom_summary.json")
    hsupp = load("phase3/headroom_supplementary.json")
    hres = load("phase3/headroom_results.json")
    sd = load("phase3/sandlock_diligence.json")
    scl = load("phase3/sandlock_claims.json")
    scomp = load("phase3/sandlock_competitors.json")
    v2h = load("phase3/v2_holdout_results.json")
    v2nc = load("phase3/v2_negative_controls.json")
    v2m = load("phase3/v2_rule_manifest.json")
    unseen = load("phase4/unseen_holdout_results.json")
    ident = load("phase4/identity_audit.json")
    dom = load("phase4/domain_audit.json")
    avc = load("attention_vs_construction.json")
    sy = load("source_yield.json")
    frozen = load("frozen_rules_manifest.json")
    hmanifest = json.loads(HEADROOM_MANIFEST.read_text(encoding="utf-8"))

    # ---- Current 3: only the fields a public card needs -------------------
    current3 = []
    for r in intro["current_3"]:
        card = r.get("card") or {}
        current3.append({
            "subject": r["subject"],
            "builder": card.get("builder_or_team", ""),
            "project": card.get("project", ""),
            "whyNow": card.get("why_now", ""),
            "artifact": card.get("technical_artifact", ""),
            "technicalDepth": card.get("technical_depth", ""),
            "formationEvidence": card.get("formation_evidence", ""),
            "arrayRelevance": card.get("array_relevance", ""),
            "whyMissed": card.get("why_company_first_sourcing_may_miss_it", ""),
            "strongestPositive": card.get("strongest_positive", ""),
            "strongestNegative": card.get("strongest_negative", ""),
            "technicalQuestion": r.get("technical_question", ""),
            "commercialQuestion": r.get("commercial_or_formation_question", ""),
            "mustVerify": card.get("what_must_be_verified_before_introduction", ""),
            "signals": r["signal_types"],
            "channels": r["channels"],
            "formationState": r["formation_state"],
            "systemState": r["system_state"],
            "analystOverride": bool(r.get("analyst_override")),
        })

    # ---- headroom: per-category distributions + per-sample points ---------
    tok = "o200k_base"
    cats = ("structured_json", "coding_context", "agent_context")
    hv = hs["by_variant"]["HEADROOM_A"][tok]
    headroom_categories = {
        c: {
            "vsRaw": hv[c]["vs_raw"],
            "vsMinified": hv[c]["vs_minified"],
            "minifyOnlyVsRaw": hv[c]["minify_only_vs_raw"],
            "retention": hs["by_variant"]["HEADROOM_A"]["probe_retention"]["by_category"][c],
        } for c in cats
    }
    samples = [{
        "id": r["sample_id"], "category": r["category"],
        "raw": r[f"{tok}_raw"], "minified": r[f"{tok}_minified"],
        "headroom": r[f"{tok}_headroom"],
        "vsRaw": r[f"{tok}_vs_raw"], "vsMinified": r[f"{tok}_vs_minified"],
        "vsCompact": r.get(f"{tok}_vs_compact"),  # only JSON-parseable samples
        "gzipVsRaw": r[f"{tok}_gzip_b64_vs_raw"],
        "retention": r["probe_rate"],
    } for r in hres["records"] if r["variant"] == "HEADROOM_A"]

    payload = {
        "generatedFrom": ("outputs/** + experiments/headroom/datasets/manifest.json"
                          " + research/sandlock/source_audit.md"),
        "commits": git_commits(),
        "hashes": {
            "v1Frozen": frozen["combined_hash"],
            "v2Rules": v2m["combined_hash"],
            "experimentProtocol": hs["protocol_sha256"],
            "experimentDataset": hs["manifest_sha256"],
        },
        "current3": current3,
        "introQueue": {
            "count": intro["intro_ready_count"],
            "current3Emitted": intro["current_3_emitted"],
            "contactedAnyone": intro["contacted_anyone"],
        },
        "sandlock": {
            "recommendation": sd["recommendation"],
            "recommendationVocabulary": sd["recommendation_vocabulary"],
            "financingWording": ("No public institutional financing identified in the "
                                 "reviewed sources."),
            "financingStatusCode": sd["company_status"]["public_institutional_financing"],
            "biggestRisk": sd["biggest_risk"],
            "construction": sd["construction"],
            "attention": sd["attention"],
            "companyStatus": sd["company_status"],
            "defensibility": sd["defensibility"],
            "guard": sd["thematic_mirroring_guard"],
            "agentsight": sd["agentsight_relationship"],
            "claims": scl["claims"],
            "competitors": scomp["alternatives"],
            "sources": sandlock_sources(),
        },
        "headroom": {
            "verdict": hs["verdict"],
            "dataset": {
                "sampleCount": hmanifest["sample_count"],
                "totalBytes": hmanifest["total_bytes"],
                "categories": hmanifest["categories"],
                "tokenizers": ["o200k_base", "cl100k_base"],
                "primaryTokenizer": hs["primary_tokenizer"],
                "baselines": ["RAW", "MINIFIED", "COMPACT_JSON", "GZIP_B64"],
                "primaryBaseline": "MINIFIED",
            },
            "claims": hs["claims"],
            "supported": hs["claims_supported"],
            "failed": hs["claims_failed"],
            "headline": hs["headline"],
            "categories": headroom_categories,
            "samples": samples,
            "retention": hs["by_variant"]["HEADROOM_A"]["probe_retention"]["overall_rate"],
            "errors": len(hs["errors"]),
            "environment": hs["environment"],
            "supplementary": hsupp["diagnostics"],
            "untested": hsupp["untested_configurations"],
            "sourceClaims": [
                {"id": "CLAIM-SRC-A",
                 "text": ("Compress tool outputs, logs, files, and RAG chunks before they "
                          "reach the LLM. 20% fewer tokens for coding agents, 60-95% fewer "
                          "tokens for JSON, same answers. Library, proxy, MCP server."),
                 "source": "GitHub repository description"},
                {"id": "CLAIM-SRC-B",
                 "text": ("60–95% fewer tokens (for JSON data), 15-20% fewer tokens "
                          "(for coding agents)"),
                 "source": "README.md, branch main"},
            ],
        },
        "methodology": {
            "v1": {"tally": v1h["tally"], "hash": v1h["rules_hash"],
                   "label": "FROZEN v1 — original 10-case holdout"},
            "v2Exploratory": {"tally": v2h["v2_tally"], "v1Tally": v2h["v1_tally"],
                              "cases": v2h["cases"], "label": "POST-HOC EXPLORATORY"},
            "unseen": {"tally": unseen["tally"], "cases": unseen["cases"],
                       "label": unseen["label"], "cohortSize": unseen["cohort_size"],
                       "eligible": unseen["eligible_count"],
                       "freezeCommit": unseen["cohort_freeze_commit"],
                       "noStatistic": unseen["no_statistic_claim"]},
            "negativeControls": {"v1": nc["tally"], "v2Regressions":
                                 v2nc["v2_incorrectly_promoted"],
                                 "v2Controls": v2nc["controls"]},
        },
        "signals": {
            "channels": sy["channels"],
            "identity": ident,
            "domain": dom,
            "attentionVsConstruction": {
                "high": avc["high_attention_low_construction"][:6],
                "low": avc["low_attention_high_construction"][:6],
                "note": avc["note"],
            },
        },
        "scale": {
            "repositories": p2["universe"]["repositories"],
            "identities": p2["universe"]["identities"],
            "evidence": p2["universe"]["evidence"],
            "relationships": p2["universe"]["relationships"],
            "sources": p2["universe"]["sources"],
            "introReadyAwu": p2["funnel"]["intro_ready_awu"],
        },
    }
    return scrub(payload)


def main() -> int:
    payload = build()
    WEB_DATA.mkdir(parents=True, exist_ok=True)
    blob = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    raw = blob.encode("utf-8")
    (WEB_DATA / "research.json").write_text(blob, encoding="utf-8")
    digest = hashlib.sha256(raw).hexdigest()
    (WEB_DATA / "export_manifest.json").write_text(
        json.dumps({"sha256": digest, "bytes": len(raw),
                    "source": "outputs/**", "deterministic": True},
                   indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"bytes": len(raw), "sha256": digest[:16],
                      "current3": len(payload["current3"]),
                      "headroomSamples": len(payload["headroom"]["samples"])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
