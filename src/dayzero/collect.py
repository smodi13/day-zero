"""Collection driver: pulls verified facts from live sources into data/collected/.

Network-bound. Run explicitly via `python -m dayzero collect`. The rest of the
pipeline reads only the collected JSON, so every other command (and the entire
standard test suite) runs offline and deterministically.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Iterable

from .adapters import github
from .config import DATA_DIR
from .cost import CostLedger
from .timeutil import now_utc, to_rfc3339

COLLECTED = DATA_DIR / "collected"


def _write(name: str, payload) -> Path:
    COLLECTED.mkdir(parents=True, exist_ok=True)
    path = COLLECTED / name
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def collect_github(repo_names: Iterable[str], ledger: CostLedger,
                   as_of: date | None = None) -> dict:
    as_of = as_of or now_utc().date()
    repos, contribs, releases, owners, orgs = {}, {}, {}, {}, {}
    errors = []
    requests = 0
    for full_name in repo_names:
        try:
            r = github.collect_repo(full_name); requests += 1
            c = github.collect_contributors(full_name); requests += 1
            rel = github.collect_releases(full_name); requests += 1
        except Exception as exc:  # noqa: BLE001 - collection must not abort the run
            errors.append({"repo": full_name, "error": str(exc)[:200]})
            continue
        r["construction"] = github.construction_metrics(r, c, rel, as_of)
        r["collected_at"] = to_rfc3339(now_utc())
        repos[full_name] = r
        contribs[full_name] = c
        releases[full_name] = rel
        owner = r["owner_login"]
        if r["owner_type"] == "Organization" and owner not in orgs:
            try:
                orgs[owner] = github.collect_org(owner); requests += 1
            except Exception as exc:  # noqa: BLE001
                errors.append({"org": owner, "error": str(exc)[:200]})
        for c_row in c[:3]:
            login = c_row["login"]
            if login not in owners:
                try:
                    owners[login] = github.collect_user(login); requests += 1
                except Exception as exc:  # noqa: BLE001
                    errors.append({"user": login, "error": str(exc)[:200]})
    ledger.record(source="github", api="rest", requests=requests, units=requests,
                  unit_label="api_request", estimated_cost_usd="0")
    _write("github_repos.json", repos)
    _write("github_contributors.json", contribs)
    _write("github_releases.json", releases)
    _write("github_users.json", owners)
    _write("github_orgs.json", orgs)
    _write("collection_errors.json", errors)
    return {"repos": len(repos), "users": len(owners), "orgs": len(orgs),
            "requests": requests, "errors": len(errors)}
