"""GitHub adapter.

Two halves, deliberately separated:
  * `collect_*` — network calls via the `gh` CLI (authenticated, 5,000 req/hr).
  * `parse_*`   — pure functions over already-collected JSON. Offline-testable.

Attention metrics (stars/forks/watchers) are collected as DESCRIPTIVE metadata and
are never inputs to any surfacing decision. Construction metrics are computed
separately and transparently.
"""
from __future__ import annotations

import json
import re
import subprocess
from datetime import date
from typing import Any, Iterable, Optional

BOT_RE = re.compile(r"\[bot\]$", re.IGNORECASE)

# Repository fields we keep. Nothing else is stored.
REPO_FIELDS = ("full_name", "stargazers_count", "forks_count", "watchers_count",
               "open_issues_count", "created_at", "pushed_at", "updated_at",
               "language", "license", "owner", "homepage", "description",
               "archived", "fork", "size", "topics", "default_branch")


class GitHubError(RuntimeError):
    pass


def _gh(path: str) -> Any:
    proc = subprocess.run(["gh", "api", path], capture_output=True, text=True)
    if proc.returncode != 0:
        raise GitHubError(f"gh api {path} failed: {proc.stderr.strip()[:200]}")
    return json.loads(proc.stdout)


# ---------------------------------------------------------------- collectors --
def collect_repo(full_name: str) -> dict[str, Any]:
    raw = _gh(f"repos/{full_name}")
    return parse_repo(raw)


def collect_user(login: str) -> dict[str, Any]:
    return parse_user(_gh(f"users/{login}"))


def collect_org(login: str) -> dict[str, Any]:
    return parse_org(_gh(f"orgs/{login}"))


def collect_contributors(full_name: str, limit: int = 10) -> list[dict[str, Any]]:
    raw = _gh(f"repos/{full_name}/contributors?per_page={limit}")
    return parse_contributors(raw)


def collect_commit_activity(full_name: str, since: str, until: str) -> list[str]:
    """Commit dates (YYYY-MM-DD) in a window, excluding bot authors."""
    raw = _gh(f"repos/{full_name}/commits?since={since}&until={until}&per_page=100")
    return parse_commit_dates(raw)


def collect_releases(full_name: str, limit: int = 30) -> list[dict[str, Any]]:
    return parse_releases(_gh(f"repos/{full_name}/releases?per_page={limit}"))


def search_repos(query: str, per_page: int = 30) -> list[dict[str, Any]]:
    from urllib.parse import quote
    raw = _gh(f"search/repositories?q={quote(query)}&sort=stars&order=desc&per_page={per_page}")
    return [parse_repo(r) for r in raw.get("items", [])]


# ------------------------------------------------------------------- parsers --
def parse_repo(raw: dict[str, Any]) -> dict[str, Any]:
    lic = raw.get("license") or {}
    owner = raw.get("owner") or {}
    return {
        "full_name": raw.get("full_name"),
        "owner_login": owner.get("login"),
        "owner_type": owner.get("type"),
        "created_at": (raw.get("created_at") or "")[:10] or None,
        "pushed_at": (raw.get("pushed_at") or "")[:10] or None,
        "language": raw.get("language"),
        "license": lic.get("spdx_id") or "none",
        "homepage": (raw.get("homepage") or "").strip() or None,
        "description": (raw.get("description") or "").strip() or None,
        "archived": bool(raw.get("archived")),
        "is_fork": bool(raw.get("fork")),
        "topics": raw.get("topics") or [],
        # descriptive attention metadata only
        "attention": {
            "stars": raw.get("stargazers_count", 0),
            "forks": raw.get("forks_count", 0),
            "watchers": raw.get("watchers_count", 0),
            "open_issues": raw.get("open_issues_count", 0),
        },
    }


def parse_user(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "login": raw.get("login"),
        "name": (raw.get("name") or "").strip() or None,
        "company": (raw.get("company") or "").strip() or None,
        "blog": (raw.get("blog") or "").strip() or None,
        "location": (raw.get("location") or "").strip() or None,
        "bio": " ".join((raw.get("bio") or "").split()) or None,
        "public_repos": raw.get("public_repos", 0),
        "account_created_at": (raw.get("created_at") or "")[:10] or None,
        "type": raw.get("type"),
        "attention": {"followers": raw.get("followers", 0)},
    }


def parse_org(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "login": raw.get("login"),
        "name": (raw.get("name") or "").strip() or None,
        "blog": (raw.get("blog") or "").strip() or None,
        "location": (raw.get("location") or "").strip() or None,
        "description": " ".join((raw.get("description") or "").split()) or None,
        "public_repos": raw.get("public_repos", 0),
        "created_at": (raw.get("created_at") or "")[:10] or None,
        "attention": {"followers": raw.get("followers", 0)},
    }


def is_bot(login: str) -> bool:
    return bool(login) and bool(BOT_RE.search(login))


def parse_contributors(raw: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for c in raw or []:
        login = c.get("login") or ""
        if is_bot(login):
            continue
        out.append({"login": login, "contributions": c.get("contributions", 0),
                    "type": c.get("type")})
    return out


def parse_commit_dates(raw: Iterable[dict[str, Any]]) -> list[str]:
    dates: list[str] = []
    for c in raw or []:
        author = c.get("author") or {}
        if is_bot(author.get("login") or ""):
            continue
        commit = c.get("commit") or {}
        when = ((commit.get("author") or {}).get("date") or "")[:10]
        if when:
            dates.append(when)
    return dates


def parse_releases(raw: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{"tag": r.get("tag_name"), "published_at": (r.get("published_at") or "")[:10] or None}
            for r in raw or []]


# -------------------------------------------------------- derived construction --
def construction_metrics(repo: dict[str, Any],
                         contributors: list[dict[str, Any]],
                         releases: list[dict[str, Any]],
                         as_of: date) -> dict[str, Any]:
    """Transparent construction metrics. Deliberately excludes every attention field.

    `human_contributors`  : non-bot contributor logins seen
    `top_contributions`   : commits by the single largest human contributor
    `total_contributions` : commits across the returned human contributors
    `longevity_days`      : created_at .. pushed_at
    `days_since_push`     : staleness
    `release_count`       : tagged releases observed
    `active_window_ratio` : longevity as a share of age (1.0 == still moving)
    """
    from .._dates import iso_to_date  # local import to avoid cycles at import time
    created = iso_to_date(repo.get("created_at"))
    pushed = iso_to_date(repo.get("pushed_at"))
    human = [c for c in contributors if not is_bot(c["login"])]
    longevity = (pushed - created).days if created and pushed else None
    age = (as_of - created).days if created else None
    return {
        "human_contributors": len(human),
        "top_contributions": max((c["contributions"] for c in human), default=0),
        "total_contributions": sum(c["contributions"] for c in human),
        "longevity_days": longevity,
        "age_days": age,
        "days_since_push": (as_of - pushed).days if pushed else None,
        "release_count": len(releases),
        "active_window_ratio": (round(longevity / age, 3)
                                if longevity is not None and age and age > 0 else None),
    }
