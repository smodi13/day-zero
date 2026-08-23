"""Build the EXP-1 dataset with provenance and ground-truth probes.

Deterministic: the same inputs produce the same manifest, with a SHA-256 per sample.
Probes are defined HERE, before any compression runs, so they cannot be chosen to
flatter a result.

Every sample is public data, self-produced output, or a file from a permissively
licensed public repository. No private data, nothing behind authentication.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DATA = Path(__file__).resolve().parent / "datasets"
SAMPLES = DATA / "samples"

# Permissively licensed public source files, pinned by repo + path.
CODE_FILES = [
    ("Eventual-Inc/Daft", "Apache-2.0", "src/daft-core/src/series/mod.rs"),
    ("Eventual-Inc/Daft", "Apache-2.0", "daft/dataframe/dataframe.py"),
    ("multikernel/sandlock", "Apache-2.0", "README.md"),
    ("eunomia-bpf/agentsight", "MIT", "README.md"),
    ("uccl-project/uccl", "Apache-2.0", "README.md"),
]


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def probe_ok(text: str, probe: str) -> bool:
    return probe in text


def add(samples: list[dict], sid: str, category: str, fmt: str, content: str,
        provenance: dict[str, Any], probes: list[str]) -> None:
    """Probes must all be present in the ORIGINAL, or the sample is malformed."""
    missing = [p for p in probes if not probe_ok(content, p)]
    if missing:
        raise SystemExit(f"{sid}: probe(s) not present in original: {missing[:2]}")
    path = SAMPLES / f"{sid}.txt"
    path.write_text(content, encoding="utf-8")
    samples.append({
        "sample_id": sid, "category": category, "format": fmt,
        "bytes": len(content.encode("utf-8")), "sha256": sha(content),
        "path": str(path.relative_to(ROOT)), "provenance": provenance,
        "probes": probes,
    })


def gh_raw(repo: str, path: str) -> str | None:
    r = subprocess.run(["gh", "api", f"repos/{repo}/contents/{path}",
                        "--jq", ".content"], capture_output=True, text=True)
    if r.returncode != 0:
        return None
    import base64
    try:
        return base64.b64decode(r.stdout).decode("utf-8", errors="replace")
    except Exception:
        return None


def local(cmd: list[str]) -> str:
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True).stdout


def main() -> int:
    SAMPLES.mkdir(parents=True, exist_ok=True)
    samples: list[dict] = []

    # ---------------------------------------------------- structured_json ----
    repos = json.loads((ROOT / "data/collected/github_repos.json").read_text())
    users = json.loads((ROOT / "data/collected/github_users.json").read_text())
    contribs = json.loads((ROOT / "data/collected/github_contributors.json").read_text())
    papers = json.loads((ROOT / "data/collected/arxiv_papers.json").read_text())

    names = sorted(repos)
    slices = [
        ("json_repos_40", {k: repos[k] for k in names[:40]}),
        ("json_repos_all", repos),
        ("json_users_120", {k: users[k] for k in sorted(users)[:120]}),
        ("json_contributors", contribs),
        ("json_papers", papers),
    ]
    for sid, obj in slices:
        pretty = json.dumps(obj, indent=2, sort_keys=True)
        key = sorted(obj)[-1]
        add(samples, sid, "structured_json", "json_pretty", pretty,
            {"kind": "github_api_response", "collected_in": "phase2",
             "file": "data/collected/*.json", "public": True},
            probes=[key, json.dumps(sorted(obj)[0])[1:-1]])

    for name in ("signals.json", "graph.json", "source_yield.json",
                 "attention_vs_construction.json", "holdout_results.json",
                 "negative_controls.json", "review_queue.json"):
        p = ROOT / "outputs" / name
        if not p.exists():
            continue
        content = p.read_text(encoding="utf-8")
        obj = json.loads(content)
        flat = json.dumps(obj)
        probes = []
        m = re.findall(r'"([A-Za-z0-9_./-]{6,40})"', flat)
        probes = list(dict.fromkeys(m))[-3:] or ["{"]
        add(samples, f"json_out_{name[:-5]}", "structured_json", "json_pretty", content,
            {"kind": "dayzero_canonical_output", "file": f"outputs/{name}",
             "public": True, "self_produced": True}, probes=probes)

    # ------------------------------------------------------ coding_context ----
    for repo, lic, path in CODE_FILES:
        text = gh_raw(repo, path)
        if not text or len(text) < 800:
            continue
        sid = "code_" + re.sub(r"[^a-z0-9]+", "_", f"{repo}_{path}".lower()).strip("_")[:60]
        words = re.findall(r"\b(?:def|fn|class|impl|struct)\s+([A-Za-z_][A-Za-z0-9_]*)", text)
        probes = list(dict.fromkeys(words))[:3] or [text.strip().split("\n")[0][:30]]
        add(samples, sid, "coding_context", "source_file", text,
            {"kind": "public_repo_file", "repo": repo, "path": path,
             "license": lic, "public": True}, probes=probes)

    for rel in ("src/dayzero/signals.py", "src/dayzero/review.py",
                "src/dayzero/build.py", "src/dayzero/holdout.py",
                "src/dayzero/db.py", "tests/test_review_rules.py"):
        text = (ROOT / rel).read_text(encoding="utf-8")
        sid = "code_self_" + rel.split("/")[-1].replace(".py", "")
        defs = re.findall(r"^def ([a-z_]+)", text, re.M)[:3]
        add(samples, sid, "coding_context", "source_file", text,
            {"kind": "self_produced", "file": rel, "public": True},
            probes=defs or ["import"])

    diff = local(["git", "show", "--stat", "74c4627"])
    add(samples, "code_git_show_stat", "coding_context", "diff", diff,
        {"kind": "self_produced", "command": "git show --stat 74c4627", "public": True},
        probes=["74c4627"[:7]] if "74c4627"[:7] in diff else [diff.strip().split("\n")[0][:20]])

    # ------------------------------------------------------- agent_context ----
    pytest_out = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--no-header"],
        cwd=ROOT, capture_output=True, text=True,
        env={**__import__("os").environ, "PYTHONPATH": "src"}).stdout
    if len(pytest_out) > 2000:
        add(samples, "agent_pytest_verbose", "agent_context", "tool_output", pytest_out,
            {"kind": "self_produced", "command": "pytest tests/ -v", "public": True},
            probes=["passed"] + re.findall(r"(test_[a-z_]+)", pytest_out)[-2:])

    for cmd, sid in (
        (["git", "log", "--stat", "-8"], "agent_git_log"),
        (["git", "ls-files"], "agent_git_ls_files"),
        (["git", "log", "--format=%H %ad %s", "--date=iso", "-40"], "agent_git_log_oneline"),
    ):
        out = local(cmd)
        if len(out) < 500:
            continue
        add(samples, sid, "agent_context", "tool_output", out,
            {"kind": "self_produced", "command": " ".join(cmd), "public": True},
            probes=[out.strip().split("\n")[0][:24], out.strip().split("\n")[-1][:24]])

    # log-shaped output with a needle: the classic "find the FATAL line" case
    lines = []
    for i in range(400):
        lvl = "INFO" if i % 37 else "WARN"
        lines.append(f"2026-08-23T10:{i//60:02d}:{i%60:02d}Z {lvl} worker-{i%8} "
                     f"handled request req-{1000+i} in {12 + i % 40}ms status=200")
    lines.insert(317, "2026-08-23T10:05:17Z FATAL worker-3 unrecoverable: "
                      "disk quota exceeded on /var/lib/agentstore err=ENOSPC-4711")
    log = "\n".join(lines)
    add(samples, "agent_log_needle", "agent_context", "log",
        log, {"kind": "synthetic", "generator": "build_datasets.py", "public": True},
        probes=["ENOSPC-4711", "FATAL", "req-1399"])

    for cmd, sid in (
        ([sys.executable, "-m", "dayzero", "diagnostics"], "agent_cli_diagnostics"),
        (["ls", "-lR", "src", "tests", "config"], "agent_ls_recursive"),
        ([sys.executable, "-m", "pip", "list"], "agent_pip_list"),
    ):
        out = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                             env={**__import__("os").environ, "PYTHONPATH": "src"}).stdout
        if len(out) < 500:
            continue
        add(samples, sid, "agent_context", "tool_output", out,
            {"kind": "self_produced", "command": " ".join(str(c) for c in cmd),
             "public": True},
            probes=[out.strip().split("\n")[0][:24], out.strip().split("\n")[-1][:24]])

    # a second needle log, different shape: stack-trace style
    frames = []
    for i in range(120):
        frames.append(f'  File "/app/service/handler_{i}.py", line {40+i}, in dispatch_{i}')
        frames.append(f"    return self._route(request, ctx_{i})")
    tb = ("Traceback (most recent call last):\n" + "\n".join(frames) +
          "\nValueError: unroutable request kind=BATCH_7788 tenant=acme-eu-west")
    add(samples, "agent_traceback_needle", "agent_context", "log", tb,
        {"kind": "synthetic", "generator": "build_datasets.py", "public": True},
        probes=["BATCH_7788", "tenant=acme-eu-west", "handler_119.py"])

    # repetitive API tool output: the shape headroom targets most directly
    api = json.dumps({"pages": [{"page": p_, "items": [
        {"sku": f"SKU-{p_:02d}-{j:03d}", "qty": (p_ * j) % 17, "warehouse": "EU-1",
         "status": "in_stock" if j % 5 else "backorder"} for j in range(25)]}
        for p_ in range(14)]}, indent=2)
    add(samples, "agent_api_pages", "agent_context", "json_pretty", api,
        {"kind": "synthetic", "generator": "build_datasets.py", "public": True},
        probes=["SKU-13-024", "backorder", "EU-1"])

    trace = json.dumps({"run_id": "r-9931", "steps": [
        {"step": i, "tool": ["read_file", "grep", "run_tests", "edit"][i % 4],
         "args": {"path": f"src/mod_{i}.py", "pattern": "def handler"},
         "status": "ok" if i != 57 else "error",
         "error": None if i != 57 else "PermissionError: /etc/shadow",
         "duration_ms": 12 + i, "tokens": 300 + i * 3} for i in range(90)]},
        indent=2)
    add(samples, "agent_trace_needle", "agent_context", "json_pretty", trace,
        {"kind": "synthetic", "generator": "build_datasets.py", "public": True},
        probes=["PermissionError: /etc/shadow", "r-9931", "src/mod_89.py"])

    manifest = {
        "experiment_id": "EXP-1",
        "sample_count": len(samples),
        "categories": {c: sum(1 for s in samples if s["category"] == c)
                       for c in sorted({s["category"] for s in samples})},
        "total_bytes": sum(s["bytes"] for s in samples),
        "samples": sorted(samples, key=lambda s: s["sample_id"]),
    }
    manifest["manifest_sha256"] = hashlib.sha256(
        json.dumps(manifest["samples"], sort_keys=True).encode()).hexdigest()
    (DATA / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: manifest[k] for k in
                      ("sample_count", "categories", "total_bytes", "manifest_sha256")},
                     indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
