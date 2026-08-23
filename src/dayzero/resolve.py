"""Conservative entity resolution.

Default is DO NOT MERGE. An unmerged graph with duplicates is a manageable problem;
a wrongly merged graph makes false statements about real people and is undetectable
downstream.

Accepted merge evidence (ER-1), any one of:
  1. explicit self-published cross-link between the two profiles
  2. both identities are public members of the same SMALL organization
  3. exact artifact cross-reference (paper page links the repo, repo commits carry the login)
  4. explicit bio statement naming the other handle

Forbidden merge evidence (ER-2): display-name similarity, avatar, city, employer,
technical topic, or any combination thereof.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, Optional

from .urlutil import bare_host, normalize_url

MERGED = "MERGED"
POSSIBLE_MATCH = "POSSIBLE_MATCH"
REJECTED = "REJECTED"

SMALL_ORG_MAX_PUBLIC_MEMBERS = 25

_HANDLE_RE = re.compile(r"(?:^|[\s(/@])(?:@|x\.com/|twitter\.com/|github\.com/)([A-Za-z0-9_-]{2,39})")


@dataclass(frozen=True)
class MergeDecision:
    status: str
    rule: Optional[str]
    basis: str


def _urls_in(*texts: Optional[str]) -> set[str]:
    out: set[str] = set()
    for t in texts:
        if not t:
            continue
        for m in re.findall(r"https?://[^\s,;)\]]+", t):
            out.add(normalize_url(m))
    return out


def explicit_cross_link(profile_a_urls: Iterable[str], b_profile_url: str) -> bool:
    """True if A's self-published links point at B's profile."""
    target = normalize_url(b_profile_url)
    if not target:
        return False
    return any(normalize_url(u) == target for u in profile_a_urls)


def site_links_both(site_urls: Iterable[str], a_url: str, b_url: str) -> bool:
    urls = {normalize_url(u) for u in site_urls}
    return normalize_url(a_url) in urls and normalize_url(b_url) in urls


def bio_names_handle(bio: Optional[str], handle: str) -> bool:
    """True if a self-published bio explicitly names the other handle."""
    if not bio or not handle:
        return False
    found = {f.lower() for f in _HANDLE_RE.findall(" " + bio)}
    return handle.lower() in found


def decide_merge(*, a_profile_url: str, b_profile_url: str,
                 a_self_links: Iterable[str] = (),
                 b_self_links: Iterable[str] = (),
                 shared_small_org: bool = False,
                 artifact_cross_reference: bool = False,
                 a_bio: Optional[str] = None, b_handle: Optional[str] = None,
                 name_similarity: bool = False) -> MergeDecision:
    """Apply ER-1 / ER-2. Name similarity NEVER merges."""
    if explicit_cross_link(a_self_links, b_profile_url) or \
       explicit_cross_link(b_self_links, a_profile_url):
        return MergeDecision(MERGED, "self_published_link",
                             "one profile's self-published links point at the other")
    if shared_small_org:
        return MergeDecision(MERGED, "shared_small_org",
                             f"both are public members of the same org (<{SMALL_ORG_MAX_PUBLIC_MEMBERS} members)")
    if artifact_cross_reference:
        return MergeDecision(MERGED, "artifact_cross_reference",
                             "paper/homepage links the exact artifact whose commits carry the login")
    if a_bio and b_handle and bio_names_handle(a_bio, b_handle):
        return MergeDecision(MERGED, "explicit_bio", "bio explicitly names the other handle")
    if name_similarity:
        # ER-2: this is exactly the evidence that must NOT merge.
        return MergeDecision(POSSIBLE_MATCH, None,
                             "display-name similarity only; ER-2 forbids merging on this")
    return MergeDecision(REJECTED, None, "no accepted merge evidence")


# ------------------------------------------------------------ name collisions --
@dataclass(frozen=True)
class CollisionCheck:
    collides: bool
    basis: str


def project_collision(name_a: str, name_b: str,
                      domain_a: str = "", domain_b: str = "",
                      round_size_a: Optional[str] = None,
                      round_size_b: Optional[str] = None) -> CollisionCheck:
    """Two entities sharing a name are assumed DISTINCT unless a strong key matches.

    Regression fixtures: Array's portfolio contains two companies called "Agency" and
    two called "Eventual" — the latter pair colliding on name AND round size.
    """
    if name_a.strip().lower() != name_b.strip().lower():
        return CollisionCheck(False, "different names")
    da, db = bare_host(domain_a), bare_host(domain_b)
    if da and db and da == db:
        return CollisionCheck(False, "same name and same canonical domain: same entity")
    reason = "same name, different/unknown domain -> treat as DISTINCT entities"
    if round_size_a and round_size_b and round_size_a == round_size_b:
        reason += "; identical round size is NOT merge evidence (ER-2)"
    return CollisionCheck(True, reason)


def identity_confidence(*, has_real_name: bool, has_self_published_site: bool,
                        has_org_membership: bool, cross_channel_links: int) -> str:
    """Conservative. LOW is disqualifying for the Intro Queue — you cannot introduce
    someone you cannot name."""
    if has_real_name and (has_self_published_site or cross_channel_links >= 1):
        return "high"
    if has_real_name or has_org_membership or has_self_published_site:
        return "medium"
    return "low"
