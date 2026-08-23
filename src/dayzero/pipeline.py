"""Review and Intro Queue execution. Both are frozen-rules gated.

The separation that matters:

  * SYSTEM ELIGIBILITY comes entirely from the frozen configuration.
  * ANALYST SELECTION is a human act, recorded separately, and can only choose
    among eligible candidates or explain an override.

An analyst override never edits the system state — it is stored alongside it with
the original state, the analyst state, a reason, and the evidence.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import date
from typing import Any, Optional

import yaml

from . import ids
from .build import DB_PATH, Builder
from .config import DATA_DIR, load
from .db import connect
from .export import md_table, write_json, write_text
from .freeze import FreezeError, require_frozen
from .negative_controls import _candidate_from_repo
from .review import current_three, drop_reason_for_watch, evaluate
from .signals import themes_for
from .timeutil import now_utc, to_rfc3339

ANALYST_PATH = DATA_DIR / "manual" / "analyst_assessments.yaml"


def _analyst_records() -> dict[str, dict[str, Any]]:
    if not ANALYST_PATH.exists():
        return {}
    data = yaml.safe_load(ANALYST_PATH.read_text(encoding="utf-8")) or {}
    return {r["subject"]: r for r in (data.get("records") or [])}


def _signal_index(as_of: date) -> dict[str, list]:
    """Rebuild the derived-signal index in memory without touching the canonical DB."""
    b = Builder(db_path=DATA_DIR / "_scratch.db", as_of=as_of)
    b.ingest_github()
    (DATA_DIR / "_scratch.db").unlink(missing_ok=True)
    return b.signal_index


def evaluate_universe(conn: sqlite3.Connection, as_of: date) -> list[dict[str, Any]]:
    manifest = require_frozen()
    idx = _signal_index(as_of)
    analyst = _analyst_records()
    out: list[dict[str, Any]] = []
    for row in conn.execute("SELECT full_name FROM repositories ORDER BY full_name"):
        full_name = row["full_name"]
        cand = _candidate_from_repo(conn, full_name, idx, as_of)
        if cand is None:
            continue
        ar = analyst.get(full_name)
        cand.analyst_review = ar
        d = evaluate(cand, as_of)
        rec = {
            "subject": full_name,
            "system_state": d.state,
            "system_drop_reason": d.drop_reason or drop_reason_for_watch(d),
            "failed_requirements": d.failed,
            "passed_requirements": d.passed,
            "notes": d.notes,
            "identity_confidence": cand.identity_confidence,
            "formation_state": cand.formation_state,
            "owner_scope": cand.owner_scope,
            "themes": cand.themes,
            "signal_types": sorted({s.signal_type for s in cand.signals}),
            "channels": sorted(cand.channels_present),
            "rules_hash": manifest["combined_hash"],
        }
        if ar and ar.get("analyst_state"):
            rec["analyst_override"] = {
                "original_system_state": d.state,
                "analyst_state": ar["analyst_state"],
                "reason": ar.get("override_reason", ""),
                "evidence": ar.get("override_evidence", ""),
                "analyst_rank": ar.get("analyst_rank"),
            }
        out.append(rec)
    return out


def run_review(args: argparse.Namespace) -> int:
    if not DB_PATH.exists():
        print("No database. Run `python -m dayzero build` first.")
        return 1
    conn = connect(DB_PATH)
    as_of = date.fromisoformat(args.as_of) if getattr(args, "as_of", None) else date.today()
    try:
        recs = evaluate_universe(conn, as_of)
    except FreezeError as e:
        print(f"FAIL CLOSED: {e}")
        return 2
    tally: dict[str, int] = {}
    for r in recs:
        tally[r["system_state"]] = tally.get(r["system_state"], 0) + 1
    write_json("review_queue.json", {"as_of": as_of.isoformat(), "tally": tally,
                                     "records": recs})
    print(json.dumps(tally, indent=2))
    return 0


def run_intro_queue(args: argparse.Namespace) -> int:
    if not DB_PATH.exists():
        print("No database. Run `python -m dayzero build` first.")
        return 1
    conn = connect(DB_PATH)
    as_of = date.fromisoformat(args.as_of) if getattr(args, "as_of", None) else date.today()
    try:
        manifest = require_frozen()
        recs = evaluate_universe(conn, as_of)
    except FreezeError as e:
        print(f"FAIL CLOSED: {e}")
        return 2
    analyst = _analyst_records()

    def final_state(r: dict[str, Any]) -> str:
        ov = r.get("analyst_override")
        return ov["analyst_state"] if ov else r["system_state"]

    intro = [r for r in recs if final_state(r) == "INTRO_READY"]
    watch = [r for r in recs if final_state(r) == "WATCH"]
    for r in intro:
        a = analyst.get(r["subject"], {})
        r["analyst_rank"] = a.get("analyst_rank", 999)
        r["card"] = a.get("card", {})
    for r in watch:
        a = analyst.get(r["subject"], {})
        r["why_interesting"] = a.get("why_interesting", "")
        r["why_not_intro_ready"] = a.get("why_not_intro_ready",
                                         "; ".join(r["failed_requirements"]))
        r["next_signal_to_watch"] = a.get("next_signal_to_watch", "")

    c3 = current_three(intro)
    payload = {
        "as_of": as_of.isoformat(),
        "rules_hash": manifest["combined_hash"],
        "intro_ready_count": len(intro),
        "current_3_emitted": len(c3) == 3,
        "contacted_anyone": False,
        "intro_queue": sorted(intro, key=lambda r: r.get("analyst_rank", 999)),
        "current_3": c3,
    }
    write_json("intro_queue.json", payload)
    write_json("watchlist.json", {"as_of": as_of.isoformat(), "count": len(watch),
                                  "records": sorted(watch, key=lambda r: r["subject"])})
    write_text("intro_queue.md", render_intro_queue_md(payload))
    write_text("watchlist.md", render_watchlist_md(watch))
    print(json.dumps({"intro_ready": len(intro), "watch": len(watch),
                      "current_3": len(c3)}, indent=2))
    return 0


def render_intro_queue_md(p: dict[str, Any]) -> str:
    lines = ["# Founder Intro Queue", "",
             f"**As of:** {p['as_of']}  ",
             f"**Frozen rules hash:** `{p['rules_hash']}`  ",
             f"**Anyone contacted:** {'yes' if p['contacted_anyone'] else 'no'}",
             "",
             "> The queue holds however many leads survive review — 0, 1, 2, 3 or more. "
             "It is never padded to reach three.",
             ""]
    if not p["intro_queue"]:
        lines += ["## Result", "", "**No lead cleared the frozen eligibility bar this cycle.**", ""]
        return "\n".join(lines)
    lines += [f"## {len(p['intro_queue'])} lead(s) cleared eligibility", ""]
    for r in p["intro_queue"]:
        card = r.get("card") or {}
        lines += [f"### {r['subject']}", ""]
        for k in ("builder_or_team", "project", "why_now", "technical_artifact",
                  "technical_depth", "formation_evidence", "array_relevance",
                  "why_company_first_sourcing_may_miss_it", "strongest_positive",
                  "strongest_negative", "technical_question",
                  "commercial_or_formation_question",
                  "what_must_be_verified_before_introduction"):
            if card.get(k):
                lines.append(f"- **{k.replace('_', ' ').title()}:** {card[k]}")
        lines += ["", f"- System state: `{r['system_state']}` · formation "
                      f"`{r['formation_state']}` · identity `{r['identity_confidence']}`",
                  f"- Signals: {', '.join(r['signal_types'])}", ""]
    if p["current_3_emitted"]:
        lines += ["## CURRENT 3", "",
                  md_table(["Rank", "Subject"],
                           [[i + 1, r["subject"]] for i, r in enumerate(p["current_3"])]), ""]
    else:
        lines += ["## CURRENT 3", "",
                  "Not emitted: fewer than three leads cleared the bar. "
                  "The standard was not lowered to fill slots.", ""]
    return "\n".join(lines)


def render_watchlist_md(watch: list[dict[str, Any]]) -> str:
    rows = [[r["subject"], r.get("why_not_intro_ready", ""),
             ", ".join(r["failed_requirements"]) or "-"]
            for r in sorted(watch, key=lambda r: r["subject"])]
    return "\n".join([
        "# Watchlist", "",
        "Technically interesting, not intro-ready. Technical depth is not formation "
        "readiness, and these are kept separate so the Intro Queue does not become a "
        "catch-all.", "",
        md_table(["Subject", "Why not intro-ready", "Failed requirements"], rows), ""])
