"""DAY ZERO command line.

Pre-freeze (always safe):   build · diagnostics · exports · freeze
Post-freeze only (gated):   holdout · negative-controls · intro-queue

The gated commands refuse to run unless a frozen-rules manifest exists AND the
current configuration still matches it. That refusal is the point.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import date
from pathlib import Path

from . import __version__
from .build import DB_PATH, Builder
from .config import DATA_DIR, OUTPUT_DIR
from .db import connect
from .diagnostics import attention_vs_construction, build_summary, source_yield
from .export import (builders, cost_ledger, graph, projects, render_holdout_md,
                     render_negative_controls_md, signals, write_json, write_text)
from .freeze import FreezeError, create_manifest, load_manifest, require_frozen


def _conn() -> sqlite3.Connection:
    if not DB_PATH.exists():
        sys.exit("No database. Run `python -m dayzero build` first.")
    return connect(DB_PATH)


def cmd_build(args: argparse.Namespace) -> int:
    b = Builder(as_of=date.fromisoformat(args.as_of) if args.as_of else None)
    res = b.run()
    write_json("build_summary.json", {"version": __version__, **res,
                                      "totals": build_summary(b.conn)})
    print(json.dumps(res, indent=2))
    if res["integrity_problems"]:
        return 1
    return 0


def cmd_exports(args: argparse.Namespace) -> int:
    conn = _conn()
    write_json("builders.json", builders(conn))
    write_json("projects.json", projects(conn))
    write_json("graph.json", graph(conn))
    write_json("signals.json", signals(conn))
    write_json("cost_ledger.json", cost_ledger(conn))
    write_json("source_yield.json", source_yield(conn))
    write_json("attention_vs_construction.json", attention_vs_construction(conn))
    print("wrote pre-evaluation exports to", OUTPUT_DIR)
    return 0


def cmd_diagnostics(args: argparse.Namespace) -> int:
    conn = _conn()
    out = {"summary": build_summary(conn), "source_yield": source_yield(conn),
           "attention_vs_construction": attention_vs_construction(conn, limit=12)}
    print(json.dumps(out, indent=2)[:4000])
    return 0


def cmd_freeze(args: argparse.Namespace) -> int:
    m = create_manifest(engine_version=__version__, git_commit=args.commit)
    print(json.dumps(m, indent=2))
    return 0


def cmd_check_freeze(args: argparse.Namespace) -> int:
    try:
        m = require_frozen()
    except FreezeError as e:
        print(f"FAIL CLOSED: {e}")
        return 2
    print(f"frozen rules OK: {m['combined_hash']}")
    return 0


def cmd_holdout(args: argparse.Namespace) -> int:
    from .holdout import run as run_holdout
    import yaml
    try:
        res = run_holdout()
    except FreezeError as e:
        print(f"FAIL CLOSED: {e}")
        return 2
    write_json("holdout_results.json", res)
    outcomes = yaml.safe_load(
        (DATA_DIR / "holdout" / "outcomes.yaml").read_text(encoding="utf-8"))["outcomes"]
    write_text("holdout_report.md", render_holdout_md(res, outcomes))
    print(json.dumps(res["tally"], indent=2))
    return 0


def cmd_negative_controls(args: argparse.Namespace) -> int:
    from .negative_controls import run as run_controls
    conn = _conn()
    b = Builder(db_path=Path(str(DB_PATH) + ".tmp"),
                as_of=date.fromisoformat(args.as_of) if args.as_of else None)
    b.ingest_github()   # rebuild signal index in memory only
    try:
        res = run_controls(conn, b.signal_index,
                           date.fromisoformat(args.as_of) if args.as_of else date.today())
    except FreezeError as e:
        print(f"FAIL CLOSED: {e}")
        return 2
    finally:
        Path(str(DB_PATH) + ".tmp").unlink(missing_ok=True)
    write_json("negative_controls.json", res)
    write_text("negative_controls.md", render_negative_controls_md(res))
    print(json.dumps(res["tally"], indent=2))
    return 0


def cmd_review(args: argparse.Namespace) -> int:
    from .pipeline import run_review
    return run_review(args)


def cmd_intro_queue(args: argparse.Namespace) -> int:
    from .pipeline import run_intro_queue
    return run_intro_queue(args)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="dayzero", description=__doc__)
    p.add_argument("--version", action="version", version=__version__)
    sub = p.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="ingest collected data into the canonical DB")
    b.add_argument("--as-of", default=None)
    b.set_defaults(func=cmd_build)

    sub.add_parser("exports", help="write canonical machine-readable outputs"
                   ).set_defaults(func=cmd_exports)
    sub.add_parser("diagnostics", help="source yield + attention/construction"
                   ).set_defaults(func=cmd_diagnostics)

    f = sub.add_parser("freeze", help="create the frozen rules manifest")
    f.add_argument("--commit", default="PENDING")
    f.set_defaults(func=cmd_freeze)

    sub.add_parser("check-freeze", help="verify rules have not drifted"
                   ).set_defaults(func=cmd_check_freeze)

    h = sub.add_parser("holdout", help="[frozen-rules gated] historical validation")
    h.set_defaults(func=cmd_holdout)

    n = sub.add_parser("negative-controls", help="[frozen-rules gated] control suite")
    n.add_argument("--as-of", default=None)
    n.set_defaults(func=cmd_negative_controls)

    r = sub.add_parser("review", help="[frozen-rules gated] run eligibility over the universe")
    r.add_argument("--as-of", default=None)
    r.set_defaults(func=cmd_review)

    q = sub.add_parser("intro-queue", help="[frozen-rules gated] build the intro queue")
    q.add_argument("--as-of", default=None)
    q.set_defaults(func=cmd_intro_queue)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
