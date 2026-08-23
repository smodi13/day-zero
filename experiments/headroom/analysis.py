"""EXP-1 analysis. A pure function of raw_results.json and the frozen config.

Knows nothing about how the numbers were produced; applies only the pre-registered
thresholds. Reports distributions, never a single combined score.
"""
from __future__ import annotations

import json
import statistics
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
RAW = Path(__file__).resolve().parent / "results" / "raw_results.json"
CONFIG = ROOT / "config" / "experiments" / "headroom_v1.yaml"
OUT = ROOT / "outputs" / "phase3"

HEADROOM_VARIANTS = ("HEADROOM_A", "HEADROOM_B_DEFAULT", "HEADROOM_B_LOSSLESS")


def dist(values: list[float]) -> dict[str, Any]:
    vals = [v for v in values if v is not None]
    if not vals:
        return {"n": 0}
    vals_sorted = sorted(vals)
    q = statistics.quantiles(vals_sorted, n=4) if len(vals_sorted) >= 4 else [None] * 3
    return {"n": len(vals), "median": round(statistics.median(vals_sorted), 2),
            "p25": round(q[0], 2) if q[0] is not None else None,
            "p75": round(q[2], 2) if q[2] is not None else None,
            "min": round(min(vals_sorted), 2), "max": round(max(vals_sorted), 2)}


def reduction(before: int, after: int) -> float | None:
    return None if not before else round(100.0 * (1 - after / before), 2)


def main() -> int:
    raw = json.loads(RAW.read_text(encoding="utf-8"))
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    th = cfg["thresholds"]

    by_sample: dict[str, dict[str, dict]] = {}
    for r in raw["rows"]:
        by_sample.setdefault(r["sample_id"], {})[r["variant"]] = r

    tokenizers = [t["id"] for t in cfg["tokenizers"]]
    records: list[dict[str, Any]] = []
    for sid, variants in sorted(by_sample.items()):
        base = variants["RAW"]
        for hv in HEADROOM_VARIANTS:
            if hv not in variants:
                continue
            h = variants[hv]
            rec = {"sample_id": sid, "category": base["category"],
                   "format": base["format"], "variant": hv,
                   "meta": h.get("meta"),
                   "probe_rate": h["probe_rate"], "probe_lost": h["probe_lost"],
                   "probe_rate_minified": variants["MINIFIED"]["probe_rate"],
                   "compression_time_ms": h["compression_time_ms"]}
            for t in tokenizers:
                k = f"tokens_{t}"
                rec[f"{t}_raw"] = base[k]
                rec[f"{t}_minified"] = variants["MINIFIED"][k]
                rec[f"{t}_headroom"] = h[k]
                rec[f"{t}_vs_raw"] = reduction(base[k], h[k])
                rec[f"{t}_vs_minified"] = reduction(variants["MINIFIED"][k], h[k])
                if "COMPACT_JSON" in variants:
                    rec[f"{t}_vs_compact"] = reduction(variants["COMPACT_JSON"][k], h[k])
                rec[f"{t}_minify_only_vs_raw"] = reduction(base[k], variants["MINIFIED"][k])
                if "GZIP_B64" in variants:
                    rec[f"{t}_gzip_b64_vs_raw"] = reduction(
                        base[k], variants["GZIP_B64"][k])
            records.append(rec)

    def slice_dist(variant: str, category: str | None, field: str) -> dict[str, Any]:
        vals = [r[field] for r in records
                if r["variant"] == variant
                and (category is None or r["category"] == category)
                and r.get(field) is not None]
        return dist(vals)

    summary: dict[str, Any] = {
        "experiment_id": "EXP-1",
        "protocol_sha256": raw["protocol_sha256"],
        "manifest_sha256": raw["manifest_sha256"],
        "environment": raw["environment"],
        "errors": raw["errors"],
        "note": "Distributions only. No combined score exists, by pre-registration.",
        "by_variant": {},
    }
    categories = sorted({r["category"] for r in records})
    for hv in HEADROOM_VARIANTS:
        block: dict[str, Any] = {}
        for t in tokenizers:
            tb: dict[str, Any] = {"overall": {
                "vs_raw": slice_dist(hv, None, f"{t}_vs_raw"),
                "vs_minified": slice_dist(hv, None, f"{t}_vs_minified"),
                "minify_only_vs_raw": slice_dist(hv, None, f"{t}_minify_only_vs_raw"),
            }}
            for c in categories:
                tb[c] = {
                    "vs_raw": slice_dist(hv, c, f"{t}_vs_raw"),
                    "vs_minified": slice_dist(hv, c, f"{t}_vs_minified"),
                    "minify_only_vs_raw": slice_dist(hv, c, f"{t}_minify_only_vs_raw"),
                }
            block[t] = tb
        probes = [r["probe_rate"] for r in records
                  if r["variant"] == hv and r["probe_rate"] is not None]
        lost = [{"sample_id": r["sample_id"], "category": r["category"],
                 "lost": r["probe_lost"]}
                for r in records if r["variant"] == hv and r["probe_lost"]]
        block["probe_retention"] = {
            "overall_rate": round(sum(probes) / len(probes), 4) if probes else None,
            "samples_with_loss": len(lost), "losses": lost,
            "by_category": {c: round(
                sum(r["probe_rate"] for r in records
                    if r["variant"] == hv and r["category"] == c) /
                max(1, sum(1 for r in records
                           if r["variant"] == hv and r["category"] == c)), 4)
                for c in categories},
        }
        block["compression_time_ms"] = slice_dist(hv, None, "compression_time_ms")
        summary["by_variant"][hv] = block

    # ------------------------- pre-registered claim evaluation ---------------
    t0 = tokenizers[0]
    primary = "HEADROOM_A"
    js_vs_min = slice_dist(primary, "structured_json", f"{t0}_vs_minified").get("median")
    js_vs_raw = slice_dist(primary, "structured_json", f"{t0}_vs_raw").get("median")
    code_vs_raw = slice_dist(primary, "coding_context", f"{t0}_vs_raw").get("median")
    agent_vs_raw = slice_dist(primary, "agent_context", f"{t0}_vs_raw").get("median")
    retention = summary["by_variant"][primary]["probe_retention"]["overall_rate"]

    band = th["structured_json_vs_raw_band_pct"]
    claims = {
        "CLAIM-A": {"supported": bool(js_vs_raw and js_vs_raw > 0),
                    "value": js_vs_raw, "threshold": "> 0% vs raw (structured_json)"},
        "CLAIM-B": {"supported": bool(js_vs_min is not None and
                                      js_vs_min >= th["structured_json_vs_minified_median_pct"]),
                    "value": js_vs_min,
                    "threshold": f">= {th['structured_json_vs_minified_median_pct']}% vs minified"},
        "CLAIM-C": {"supported": bool(retention is not None and
                                      retention >= th["probe_retention_pass"]),
                    "value": retention,
                    "threshold": f">= {th['probe_retention_pass']} probe retention"},
        "CLAIM-D": {"supported": bool(js_vs_raw is not None and
                                      band[0] <= js_vs_raw <= band[1]),
                    "value": js_vs_raw, "threshold": f"{band[0]}-{band[1]}% vs raw"},
        "CLAIM-E": {"supported": bool(code_vs_raw is not None and
                                      code_vs_raw >= th["coding_context_vs_raw_median_pct"]),
                    "value": code_vs_raw,
                    "threshold": f">= {th['coding_context_vs_raw_median_pct']}% vs raw"},
    }
    supported = [k for k, v in claims.items() if v["supported"]]
    failed = [k for k, v in claims.items() if not v["supported"]]

    if raw["errors"] and len(raw["errors"]) > raw["sample_count"]:
        verdict = "INCONCLUSIVE"
    elif (js_vs_min is not None and js_vs_min < 5.0) or \
         (retention is not None and retention < th["probe_retention_fail"]):
        verdict = "NOT_REPRODUCED"
    elif not failed:
        verdict = "REPRODUCED"
    elif supported:
        verdict = "PARTIALLY_REPRODUCED"
    else:
        verdict = "NOT_REPRODUCED"

    summary["primary_variant"] = primary
    summary["primary_tokenizer"] = t0
    summary["headline"] = {
        "structured_json_vs_raw_median_pct": js_vs_raw,
        "structured_json_vs_minified_median_pct": js_vs_min,
        "coding_context_vs_raw_median_pct": code_vs_raw,
        "agent_context_vs_raw_median_pct": agent_vs_raw,
        "probe_retention_rate": retention,
    }
    summary["claims"] = claims
    summary["claims_supported"] = supported
    summary["claims_failed"] = failed
    summary["verdict"] = verdict

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "headroom_results.json").write_text(
        json.dumps({"records": records}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "headroom_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"verdict": verdict, "headline": summary["headline"],
                      "supported": supported, "failed": failed}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
