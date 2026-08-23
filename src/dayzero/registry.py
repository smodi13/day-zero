"""Organization registry and matching.

Concept ported from the audited X engine: exact or dot-boundary domain matching and
exact GitHub-owner matching. **Substring matching is forbidden** — it is the fastest
route to a false statement about who owns what.

The registry answers one question: is this artifact owned by an ESTABLISHED
organization rather than by a new formation? (Phase 1 negative control NC-6.)
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from .urlutil import bare_host

# Established organizations whose artifacts are corporate open-source releases,
# foundations, or academic groups — not new company formations.
ESTABLISHED_GITHUB_OWNERS = {
    # large technology companies
    "microsoft", "google", "googleapis", "googleworkspace", "alibaba", "bytedance",
    "tencent", "tencentcloud", "yandex", "aws", "amzn", "apple", "meta",
    "facebook", "nvidia", "nvlabs", "ibm", "intel", "huawei", "huawei-csl",
    "volcengine", "datadog", "vercel", "cloudflare", "gitlab", "github",
    "anthropics", "openai", "wso2", "cybereason-public", "comet-ml", "firecrawl",
    "astral-sh", "withastro", "chromedevtools", "servicenow", "jamf", "elastic",
    # foundations / community umbrellas
    "kubernetes-sigs", "open-telemetry", "opentelemetry", "cncf", "apache",
    "linuxfoundation", "eunomia-bpf", "responsibleai", "ccfos",
}

ESTABLISHED_DOMAINS = {
    "microsoft.com", "google.com", "alibaba.com", "bytedance.com", "tencent.com",
    "datadoghq.com", "vercel.com", "cloudflare.com", "gitlab.com", "github.com",
    "anthropic.com", "openai.com", "wso2.com", "kubernetes.io", "apache.org",
}

# Academic / research group markers seen in org names and descriptions.
RESEARCH_GROUP_MARKERS = ("lab", "laboratory", "university", "institute", "research group")


@dataclass(frozen=True)
class RegistryMatch:
    entity: str
    match_type: str   # github_owner | domain | research_marker
    scope: str        # established_organization | foundation_or_community | research_group


def match_github_owner(owner: str) -> Optional[RegistryMatch]:
    """Exact, case-insensitive. Substring matching is not permitted."""
    if not owner:
        return None
    o = owner.strip().lower()
    if o in ESTABLISHED_GITHUB_OWNERS:
        return RegistryMatch(o, "github_owner", "established_organization")
    return None


def match_domain(url_or_host: str) -> Optional[RegistryMatch]:
    """Exact host or dot-boundary subdomain. Never substring."""
    host = bare_host(url_or_host)
    if not host:
        return None
    for dom in ESTABLISHED_DOMAINS:
        if host == dom or host.endswith("." + dom):
            return RegistryMatch(dom, "domain", "established_organization")
    return None


def looks_like_research_group(org_name: str, description: str = "") -> bool:
    blob = f"{org_name or ''} {description or ''}".lower()
    return any(re.search(rf"\b{re.escape(m)}\b", blob) for m in RESEARCH_GROUP_MARKERS)


def owner_scope(owner_login: str, org_name: str = "", description: str = "",
                homepage: str = "", public_repos: int = 0,
                org_age_days: Optional[int] = None) -> str:
    """Resolve an artifact's owner scope. Conservative and explainable.

    `unregistered` means "not recognised as established" — NOT "definitely a startup".
    """
    if match_github_owner(owner_login) or match_domain(homepage):
        return "established_organization"
    if looks_like_research_group(org_name, description):
        return "research_group"
    # A large, long-lived org with many repos is very unlikely to be a Day-0 formation.
    if public_repos >= 40 and (org_age_days or 0) > 730:
        return "established_organization"
    return "unregistered"
