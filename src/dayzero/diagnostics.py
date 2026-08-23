"""Source-yield and attention-vs-construction diagnostics.

Deliberately separates DISCOVERY contribution (which channel first surfaced the
entity) from EVIDENCE contribution (which channel supplied the supporting facts).
A channel can be excellent at one and useless at the other.
"""
from __future__ import annotations

import sqlite3
from typing import Any

from .money import UNKNOWN


def source_yield(conn: sqlite3.Connection) -> dict[str, Any]:
    rows: dict[str, dict[str, Any]] = {}

    def bucket(name: str) -> dict[str, Any]:
        return rows.setdefault(name, {
            "channel": name, "raw_records": 0, "evidence_records": 0,
            "unique_subjects": 0, "resolved_identities": 0, "unresolved_identities": 0,
            "technical_artifacts": 0, "formation_signals": 0, "stale_signals": 0,
            "duplicates_suppressed": 0, "estimated_cost_usd": "0",
        })

    # discovery contribution: every repository was discovered through GitHub search
    gh = bucket("github")
    gh["raw_records"] = conn.execute("SELECT COUNT(*) FROM repositories").fetchone()[0]
    gh["unique_subjects"] = gh["raw_records"]
    gh["resolved_identities"] = conn.execute(
        "SELECT COUNT(*) FROM builders WHERE identity_confidence='high'").fetchone()[0]
    gh["unresolved_identities"] = conn.execute(
        "SELECT COUNT(*) FROM builders WHERE identity_confidence='low'").fetchone()[0]
    gh["technical_artifacts"] = conn.execute(
        "SELECT COUNT(DISTINCT subject_id) FROM technical_signals").fetchone()[0]

    # evidence contribution, by the source type actually cited
    for r in conn.execute(
            "SELECT s.source_type st, COUNT(*) n FROM evidence e"
            " JOIN sources s ON s.source_id=e.source_id GROUP BY 1"):
        ch = {"arxiv_paper": "research", "x_post": "x",
              "hackathon_official": "hackathon", "event_listing": "events"}.get(
                  r["st"], "github" if r["st"].startswith("github") else "web")
        bucket(ch)["evidence_records"] += r["n"]

    for r in conn.execute(
            "SELECT channel, COUNT(*) n, SUM(stale) s FROM formation_signals GROUP BY 1"):
        b = bucket(r["channel"])
        b["formation_signals"] += r["n"]
        b["stale_signals"] += (r["s"] or 0)

    research = bucket("research")
    research["raw_records"] = conn.execute("SELECT COUNT(*) FROM papers").fetchone()[0]
    research["unique_subjects"] = research["raw_records"]

    xb = bucket("x")
    xb["raw_records"] = conn.execute(
        "SELECT COUNT(*) FROM social_signals WHERE channel='x'").fetchone()[0]
    xb["note"] = "X ingestion is off by default and no credentials were present"

    hk = bucket("hackathon")
    hk["raw_records"] = conn.execute("SELECT COUNT(*) FROM hackathons").fetchone()[0]
    hk["note"] = "manual only by robots policy; no automated adapter exists"

    ev = bucket("events")
    ev["raw_records"] = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]

    for r in conn.execute(
            "SELECT source, SUM(requests) rq, COUNT(*) n FROM cost_ledger GROUP BY 1"):
        b = bucket("research" if r["source"] == "arxiv" else r["source"])
        b["api_requests"] = r["rq"]
        b["estimated_cost_usd"] = "0.000000"
    return {"channels": [rows[k] for k in sorted(rows)]}


def attention_vs_construction(conn: sqlite3.Connection, limit: int = 20) -> dict[str, Any]:
    """Descriptive only. High construction is NOT a claim about investment quality."""
    rows = []
    for r in conn.execute(
            "SELECT r.full_name, a.stars, a.forks, c.top_contributions,"
            " c.total_contributions, c.longevity_days, c.days_since_push,"
            " c.human_contributors"
            " FROM repositories r JOIN repo_attention a ON a.repo_id=r.repo_id"
            " JOIN repo_construction c ON c.repo_id=r.repo_id"):
        stars = r["stars"] or 0
        top = r["top_contributions"] or 0
        rows.append({
            "repo": r["full_name"], "stars": stars, "forks": r["forks"],
            "top_contributions": top, "total_contributions": r["total_contributions"],
            "longevity_days": r["longevity_days"], "days_since_push": r["days_since_push"],
            "human_contributors": r["human_contributors"],
            # ratio is a DESCRIPTIVE diagnostic, never an input to any decision
            "stars_per_commit": round(stars / top, 1) if top else None,
        })
    ranked = [x for x in rows if x["stars_per_commit"] is not None]
    high_attention_low_construction = sorted(
        ranked, key=lambda x: -x["stars_per_commit"])[:limit]
    low_attention_high_construction = sorted(
        [x for x in ranked if x["top_contributions"] >= 100],
        key=lambda x: x["stars_per_commit"])[:limit]
    return {
        "note": ("Descriptive divergence only. High construction is not a claim about "
                 "investment quality, and low attention is not a claim about obscurity."),
        "high_attention_low_construction": high_attention_low_construction,
        "low_attention_high_construction": low_attention_high_construction,
        "repos_measured": len(ranked),
    }


def build_summary(conn: sqlite3.Connection) -> dict[str, Any]:
    def one(sql: str) -> int:
        return conn.execute(sql).fetchone()[0]
    return {
        "repositories": one("SELECT COUNT(*) FROM repositories"),
        "builders": one("SELECT COUNT(*) FROM builders"),
        "identities": one("SELECT COUNT(*) FROM identities"),
        "organizations": one("SELECT COUNT(*) FROM organizations"),
        "papers": one("SELECT COUNT(*) FROM papers"),
        "sources": one("SELECT COUNT(*) FROM sources"),
        "evidence": one("SELECT COUNT(*) FROM evidence"),
        "relationships": one("SELECT COUNT(*) FROM relationships"),
        "technical_signals": one("SELECT COUNT(*) FROM technical_signals"),
        "formation_signals": one("SELECT COUNT(*) FROM formation_signals"),
        "commercialization_signals": one("SELECT COUNT(*) FROM commercialization_signals"),
        "technical_assessments": one("SELECT COUNT(*) FROM technical_assessments"),
        "formation_state_rows": one("SELECT COUNT(*) FROM formation_state_history"),
        "social_signals": one("SELECT COUNT(*) FROM social_signals"),
        "hackathons": one("SELECT COUNT(*) FROM hackathons"),
        "events": one("SELECT COUNT(*) FROM events"),
        "status_checks": one("SELECT COUNT(*) FROM status_checks"),
    }
