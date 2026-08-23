"""EXP-1 runner. Executes the pre-registered protocol; changes nothing about it.

Reads config/experiments/headroom_v1.yaml and the frozen dataset manifest, applies each
baseline and headroom to every sample under every tokenizer, scores probe retention, and
writes raw results. Analysis is a separate step so measurement and interpretation cannot
be conflated.

Run inside the isolated venv that has headroom-ai + tiktoken installed.
"""
from __future__ import annotations

import base64
import gzip
import hashlib
import json
import platform
import re
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "datasets" / "manifest.json"
RESULTS = HERE / "results"


# ------------------------------------------------------------------ baselines --
def minify(content: str, fmt: str) -> str:
    if fmt.startswith("json"):
        try:
            return json.dumps(json.loads(content), separators=(",", ":"))
        except Exception:
            pass
    # text: collapse runs of spaces and blank lines. Nothing semantic is removed.
    out = re.sub(r"[ \t]+", " ", content)
    out = re.sub(r"\n{3,}", "\n\n", out)
    return "\n".join(line.rstrip() for line in out.split("\n")).strip()


def compact_json(content: str, fmt: str) -> str | None:
    if not fmt.startswith("json"):
        return None
    try:
        return json.dumps(json.loads(content), separators=(",", ":"), sort_keys=False)
    except Exception:
        return None


def gzip_b64(content: str) -> str:
    return base64.b64encode(gzip.compress(content.encode("utf-8"), 9)).decode("ascii")


# ----------------------------------------------------------------- tokenizers --
def load_tokenizers() -> dict[str, Any]:
    import tiktoken
    return {name: tiktoken.get_encoding(name)
            for name in ("o200k_base", "cl100k_base")}


# -------------------------------------------------------------------- headroom --
def headroom_path_a(content: str) -> tuple[str, list[str], float]:
    """Public library API on a realistic agent message sequence (tool output)."""
    from headroom import compress
    messages = [
        {"role": "user", "content": "run the tool and answer from its output"},
        {"role": "assistant", "content": None,
         "tool_calls": [{"id": "t1", "type": "function",
                         "function": {"name": "run_tool", "arguments": "{}"}}]},
        {"role": "tool", "tool_call_id": "t1", "content": content},
    ]
    t0 = time.perf_counter()
    r = compress(messages, model_limit=200000)
    ms = (time.perf_counter() - t0) * 1000
    tool_msgs = [m for m in r.messages if m.get("role") == "tool"]
    out = tool_msgs[-1]["content"] if tool_msgs else ""
    if not isinstance(out, str):
        out = json.dumps(out)
    return out, list(r.transforms_applied), ms


def headroom_path_b(content: str, lossless_only: bool) -> tuple[str, str, float]:
    """JSON component API on raw content."""
    from headroom import SmartCrusher
    sc = SmartCrusher()
    t0 = time.perf_counter()
    r = sc.crush(content, query="", lossless_only=lossless_only)
    ms = (time.perf_counter() - t0) * 1000
    return r.compressed, str(r.strategy), ms


# ---------------------------------------------------------------------- probes --
def score_probes(text: str, probes: list[str]) -> dict[str, Any]:
    retained = [p for p in probes if p in text]
    lost = [p for p in probes if p not in text]
    return {"n": len(probes), "retained": len(retained),
            "rate": (len(retained) / len(probes)) if probes else None,
            "lost_probes": lost}


def environment() -> dict[str, Any]:
    import tiktoken
    import headroom
    return {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "machine": platform.machine(),
        "headroom_ai": getattr(headroom, "__version__", "unknown"),
        "tiktoken": tiktoken.__version__,
        "gpu": False,
        "paid_api_calls": 0,
    }


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    encoders = load_tokenizers()
    RESULTS.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []

    for s in manifest["samples"]:
        content = (ROOT / s["path"]).read_text(encoding="utf-8")
        assert hashlib.sha256(content.encode()).hexdigest() == s["sha256"], \
            f"{s['sample_id']}: sample content changed since the manifest was frozen"

        variants: dict[str, dict[str, Any]] = {
            "RAW": {"text": content, "meta": None, "ms": 0.0},
            "MINIFIED": {"text": minify(content, s["format"]), "meta": None, "ms": 0.0},
            "GZIP_B64": {"text": gzip_b64(content), "meta": None, "ms": 0.0},
        }
        cj = compact_json(content, s["format"])
        if cj is not None:
            variants["COMPACT_JSON"] = {"text": cj, "meta": None, "ms": 0.0}

        try:
            out, transforms, ms = headroom_path_a(content)
            variants["HEADROOM_A"] = {"text": out, "meta": transforms, "ms": ms}
        except Exception as exc:                                   # noqa: BLE001
            errors.append({"sample_id": s["sample_id"], "path": "A",
                           "error": f"{type(exc).__name__}: {exc}"[:300]})

        for lossless in (False, True):
            key = "HEADROOM_B_LOSSLESS" if lossless else "HEADROOM_B_DEFAULT"
            try:
                out, strategy, ms = headroom_path_b(content, lossless)
                variants[key] = {"text": out, "meta": strategy, "ms": ms}
            except Exception as exc:                               # noqa: BLE001
                errors.append({"sample_id": s["sample_id"], "path": key,
                               "error": f"{type(exc).__name__}: {exc}"[:300]})

        for variant, v in variants.items():
            probe = score_probes(v["text"], s["probes"])
            row = {
                "sample_id": s["sample_id"], "category": s["category"],
                "format": s["format"], "variant": variant,
                "bytes": len(v["text"].encode("utf-8")),
                "meta": v["meta"], "compression_time_ms": round(v["ms"], 3),
                "probe_n": probe["n"], "probe_retained": probe["retained"],
                "probe_rate": probe["rate"], "probe_lost": probe["lost_probes"],
            }
            for tname, enc in encoders.items():
                row[f"tokens_{tname}"] = len(enc.encode(v["text"]))
            rows.append(row)

    payload = {
        "experiment_id": "EXP-1",
        "protocol_sha256": hashlib.sha256(
            (ROOT / "config/experiments/headroom_v1.yaml").read_bytes()).hexdigest(),
        "manifest_sha256": manifest["manifest_sha256"],
        "environment": environment(),
        "sample_count": manifest["sample_count"],
        "row_count": len(rows),
        "errors": errors,
        "rows": rows,
    }
    (RESULTS / "raw_results.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"samples": manifest["sample_count"], "rows": len(rows),
                      "errors": len(errors)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
