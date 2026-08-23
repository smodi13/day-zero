"""Canonical exports.

JSON is the single source of truth. Markdown is GENERATED from it, so a fact never
exists in two places that can drift apart.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Optional

from .config import OUTPUT_DIR


def write_json(name: str, payload: Any) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / name
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    return path


def write_text(name: str, text: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / name
    path.write_text(text, encoding="utf-8")
    return path


def builders(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = []
    for r in conn.execute(
            "SELECT b.person_id, b.display_name, b.identity_confidence,"
            " b.career_signal_class, b.career_signal_evidence_id,"
            " i.channel, i.handle, i.profile_url"
            " FROM builders b JOIN identities i ON i.person_id=b.person_id"
            " ORDER BY i.handle"):
        rows.append(dict(r))
    return rows


def projects(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = []
    for r in conn.execute(
            "SELECT r.repo_id, r.full_name, r.owner_login, r.owner_type, r.created_at,"
            " r.pushed_at, r.language, r.license, r.homepage, r.description,"
            " a.stars, a.forks, a.watchers, a.open_issues,"
            " c.human_contributors, c.top_contributions, c.total_contributions,"
            " c.longevity_days, c.age_days, c.days_since_push, c.release_count,"
            " c.active_window_ratio"
            " FROM repositories r"
            " LEFT JOIN repo_attention a ON a.repo_id=r.repo_id"
            " LEFT JOIN repo_construction c ON c.repo_id=r.repo_id"
            " ORDER BY r.full_name"):
        d = dict(r)
        rows.append({
            "repo_id": d["repo_id"], "full_name": d["full_name"],
            "owner_login": d["owner_login"], "owner_type": d["owner_type"],
            "created_at": d["created_at"], "pushed_at": d["pushed_at"],
            "language": d["language"], "license": d["license"],
            "homepage": d["homepage"], "description": d["description"],
            # attention and construction are kept in separate objects, deliberately
            "attention": {k: d[k] for k in ("stars", "forks", "watchers", "open_issues")},
            "construction": {k: d[k] for k in (
                "human_contributors", "top_contributions", "total_contributions",
                "longevity_days", "age_days", "days_since_push", "release_count",
                "active_window_ratio")},
        })
    return rows


def graph(conn: sqlite3.Connection) -> dict[str, Any]:
    nodes, edges = [], []
    for r in conn.execute("SELECT person_id id, display_name label,"
                          " 'person' kind FROM builders"):
        nodes.append(dict(r))
    for r in conn.execute("SELECT repo_id id, full_name label, 'repository' kind"
                          " FROM repositories"):
        nodes.append(dict(r))
    for r in conn.execute("SELECT org_id id, login label, 'organization' kind"
                          " FROM organizations"):
        nodes.append(dict(r))
    for r in conn.execute("SELECT paper_id id, arxiv_id label, 'paper' kind FROM papers"):
        nodes.append(dict(r))
    for r in conn.execute(
            "SELECT relationship_id id, from_id, from_type, kind, to_id, to_type,"
            " evidence_id, observed_at FROM relationships ORDER BY relationship_id"):
        edges.append(dict(r))
    return {"nodes": sorted(nodes, key=lambda n: (n["kind"], n["id"])), "edges": edges}


def signals(conn: sqlite3.Connection) -> dict[str, Any]:
    out: dict[str, list] = {}
    for table in ("technical_signals", "formation_signals", "commercialization_signals"):
        out[table] = [dict(r) for r in conn.execute(
            f"SELECT * FROM {table} ORDER BY signal_id")]
    out["formation_state_history"] = [dict(r) for r in conn.execute(
        "SELECT * FROM formation_state_history ORDER BY project_id, as_of")]
    return out


def cost_ledger(conn: sqlite3.Connection) -> dict[str, Any]:
    rows = [dict(r) for r in conn.execute("SELECT * FROM cost_ledger ORDER BY at, row_id")]
    by_source: dict[str, dict[str, Any]] = {}
    for r in rows:
        b = by_source.setdefault(r["source"], {"requests": 0, "estimated_cost_usd": "0.000000",
                                               "actual_cost_usd": "UNKNOWN"})
        b["requests"] += r["requests"] or 0
    return {"events": rows, "by_source": by_source,
            "note": ("Free sources record 0. Costs that cannot be determined record "
                     "UNKNOWN and are never invented.")}


# --------------------------------------------------------------- markdown ----
def md_table(headers: list[str], rows: list[list[str]]) -> str:
    out = ["| " + " | ".join(headers) + " |",
           "| " + " | ".join("---" for _ in headers) + " |"]
    for r in rows:
        out.append("| " + " | ".join(str(x).replace("|", "\\|") for x in r) + " |")
    return "\n".join(out)


def render_holdout_md(results: dict[str, Any], outcomes: dict[str, str]) -> str:
    rows = []
    for c in results["cases"]:
        rows.append([c["case_id"], c["company"], c["cutoff_date"],
                     c.get("prereg_expected_verdict") or "-", c["verdict"],
                     c["evidence_count"], ", ".join(c.get("channels") or []) or "-"])
    tally = results["tally"]
    md = [
        "# Historical Holdout — Results",
        "",
        f"**Rules hash (frozen before the run):** `{results['rules_hash']}`",
        f"**Manifest created:** {results['manifest_created_at']}",
        "",
        f"> {results['interpretation_caveat']}",
        "",
        "## Tally",
        "",
        md_table(["Verdict", "Count"], [[k, v] for k, v in sorted(tally.items())]),
        "",
        "## Case by case",
        "",
        md_table(["Case", "Company", "Cutoff", "Pre-registered", "Verdict",
                  "As-of evidence items", "Independent channels"], rows),
        "",
        "## Outcomes (recorded AFTER the verdicts; referenced by no rule)",
        "",
        md_table(["Case", "Outcome"],
                 [[k, outcomes.get(k, "-")] for k in sorted(outcomes)]),
        "",
    ]
    return "\n".join(md)


def render_negative_controls_md(results: dict[str, Any]) -> str:
    rows = [[c["control_id"], c["name"], c["subject"], c["expected_drop_reason"],
             c["actual_state"], c.get("actual_drop_reason") or "-", c["result"]]
            for c in results["controls"]]
    return "\n".join([
        "# Negative Controls — Results",
        "",
        f"**Rules hash:** `{results['rules_hash']}`",
        "",
        f"> {results['caveat']}",
        "",
        md_table(["Result", "Count"],
                 [[k, v] for k, v in sorted(results["tally"].items())]),
        "",
        md_table(["ID", "Control", "Subject", "Expected reason", "State",
                  "Actual reason", "Result"], rows),
        "",
    ])
