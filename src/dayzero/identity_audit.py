"""Phase 4 identity-join audit.

Measures empirically what Phase 2 could only assert: how many live builder identities can
be resolved across platforms using ONLY legitimate first-party evidence, and how many are
X-linkable.

Explicitly not used: data brokers, people-search sites, private email databases, guessed
matches, facial recognition, location inference, or arbitrary X username search. An X
handle counts only when a trusted professional artifact links to it.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .config import DATA_DIR, OUTPUT_DIR
from .urlutil import bare_host, normalize_url
from .v2 import (POSSIBLE_MATCH, STRONG_ARTIFACT_MATCH, UNRESOLVED,
                 VERIFIED_CROSS_LINK, IdentityEvidence, identity_state_v2)

COLLECTED = DATA_DIR / "collected"
OUT = OUTPUT_DIR / "phase4"

SOCIAL_HOSTS = {"x.com": "x", "twitter.com": "x", "linkedin.com": "linkedin",
                "bsky.app": "bluesky", "mastodon.social": "mastodon"}
# Hosts that are a person's own professional surface, not a social profile.
PERSONAL_SITE_EXCLUDE = {"github.com", "github.io"} | set(SOCIAL_HOSTS)
_AT_HANDLE = re.compile(r"(?:^|\s)@([A-Za-z0-9_]{2,15})\b")


def _load(name: str) -> Any:
    p = COLLECTED / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def evidence_for(login: str, user: dict, repos: dict, contribs: dict) -> list[IdentityEvidence]:
    """Collect ONLY first-party, legitimately public identity evidence."""
    ev: list[IdentityEvidence] = []
    name = user.get("name")
    blog = (user.get("blog") or "").strip()
    profile = f"https://github.com/{login}"

    if blog:
        host = bare_host(blog)
        if host in SOCIAL_HOSTS:
            # The person's own GitHub profile links their social account: a first-party link.
            ev.append(IdentityEvidence(
                "github_profile_blog_points_at_the_other_profile", name, True,
                f"github:{login}->{SOCIAL_HOSTS[host]}"))
        elif host and host not in PERSONAL_SITE_EXCLUDE:
            ev.append(IdentityEvidence("personal_site_links_both_profiles", name, True,
                                       f"github:{login}->{host}"))
    if name:
        ev.append(IdentityEvidence("github_profile_name", name, False, f"github:{login}"))
    # A named human who owns/maintains a repository is a second independent artifact.
    for full_name, rows in contribs.items():
        for r in rows[:3]:
            if r["login"] == login and (r.get("contributions") or 0) >= 40 and name:
                ev.append(IdentityEvidence("github_top_contributor", name, False,
                                           f"repo:{full_name}"))
                break
    # A repository homepage on a non-code domain is a project/company surface.
    for full_name, repo in repos.items():
        home = (repo.get("homepage") or "").strip()
        if not home or repo.get("owner_login") != login:
            continue
        host = bare_host(home)
        if host and host not in PERSONAL_SITE_EXCLUDE and name:
            ev.append(IdentityEvidence("readme_author_link_to_a_profile", name, False,
                                       f"domain:{host}"))
            break
    return ev


def x_linkable(login: str, user: dict) -> tuple[bool, str]:
    """True ONLY when a trusted professional artifact explicitly links an X account.

    A bare @handle in a bio is NOT accepted: on GitHub those are overwhelmingly GitHub
    org handles, not X accounts, and guessing would be exactly the fuzzy matching v2
    forbids.
    """
    blog = (user.get("blog") or "").strip()
    if blog and bare_host(blog) in ("x.com", "twitter.com"):
        return True, f"github profile blog field -> {normalize_url(blog)}"
    return False, ""


def run() -> dict[str, Any]:
    users = _load("github_users.json")
    repos = _load("github_repos.json")
    contribs = _load("github_contributors.json")

    states: dict[str, int] = {VERIFIED_CROSS_LINK: 0, STRONG_ARTIFACT_MATCH: 0,
                              POSSIBLE_MATCH: 0, UNRESOLVED: 0}
    x_hits: list[dict[str, str]] = []
    bio_at_handles = 0
    personal_sites = 0
    per_identity: list[dict[str, Any]] = []

    for login, user in sorted(users.items()):
        ev = evidence_for(login, user, repos, contribs)
        st = identity_state_v2(ev)
        states[st["state"]] += 1
        linkable, basis = x_linkable(login, user)
        if linkable:
            x_hits.append({"handle_source": "github_profile_blog", "basis": basis})
        if _AT_HANDLE.search(" " + (user.get("bio") or "")):
            bio_at_handles += 1
        blog = (user.get("blog") or "").strip()
        if blog and bare_host(blog) not in PERSONAL_SITE_EXCLUDE:
            personal_sites += 1
        per_identity.append({"state": st["state"], "mergeable": st["may_merge"],
                             "x_linkable": linkable})

    total = len(users)
    mergeable = states[VERIFIED_CROSS_LINK] + states[STRONG_ARTIFACT_MATCH]
    payload = {
        "universe": "Phase 2 live collected identities (unchanged)",
        "total_identities": total,
        "states": states,
        "mergeable_identities": mergeable,
        "mergeable_pct": round(100 * mergeable / total, 2) if total else None,
        "x_linkable_count": len(x_hits),
        "x_linkable_pct": round(100 * len(x_hits) / total, 2) if total else None,
        "context": {
            "identities_with_a_personal_or_project_site": personal_sites,
            "identities_with_an_at_handle_in_bio": bio_at_handles,
            "why_at_handles_are_not_counted": (
                "On GitHub a bare @handle in a bio is overwhelmingly a GitHub organisation "
                "handle, not an X account. Treating them as X accounts would be the fuzzy "
                "matching v2 forbids."),
        },
        "methods_excluded": ["data_brokers", "people_search_sites", "private_email_databases",
                             "guessed_username_matching", "arbitrary_x_username_search",
                             "facial_recognition", "location_inference"],
        "no_private_identifiers_exported": True,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "identity_audit.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    print(json.dumps(run(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
