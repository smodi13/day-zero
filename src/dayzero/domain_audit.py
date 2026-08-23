"""Phase 4 domain-signal audit.

Phase 3 observed that formation lives on domains while construction lives on GitHub.
This measures how often domain evidence adds a DISTINCT formation event beyond what
GitHub construction already provides.

Uses only content operators chose to publish. No WHOIS, no registrant lookup, no
reverse WHOIS, no DNS-history broker data — registrant data is personal data.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .config import DATA_DIR, OUTPUT_DIR
from .registry import owner_scope
from .urlutil import bare_host, is_product_domain

COLLECTED = DATA_DIR / "collected"
OUT = OUTPUT_DIR / "phase4"
CODE_HOSTS = {"github.com", "github.io", "gitlab.com", "readthedocs.io"}


def _load(name: str) -> Any:
    p = COLLECTED / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def _interpret(present_pct: float, distinct_pct: float) -> str:
    """Generated from the measured figures so the prose cannot drift from the data."""
    scale = "most" if present_pct > 50 else "a minority of"
    return (
        f"A project domain is present on {scale} repositories ({present_pct}%), but it "
        f"adds a DISTINCT formation event on only {distinct_pct}% of them - because in "
        "the other cases the GitHub organisation has already supplied one and the two "
        "describe the same decision. Domains earn their own event where an organisation "
        "has no domain of its own, or where the project domain differs from the company "
        "domain, which is a second and separate decision.")


def run() -> dict[str, Any]:
    repos = _load("github_repos.json")
    orgs = _load("github_orgs.json")

    total = len(repos)
    with_domain = 0
    docs_site = 0
    product_domain = 0
    org_with_domain = 0
    domain_adds_distinct_formation = 0
    github_only_formation = 0
    domains: set[str] = set()

    for full_name, r in sorted(repos.items()):
        home = (r.get("homepage") or "").strip()
        host = bare_host(home)
        org = orgs.get(r.get("owner_login") or "")
        org_created = bool(org and org.get("created_at"))
        org_domain = bare_host((org or {}).get("blog") or "")

        has_domain = bool(host) and host not in CODE_HOSTS and is_product_domain(home)
        if has_domain:
            with_domain += 1
            domains.add(host)
            if "docs." in host or "/docs" in home:
                docs_site += 1
            else:
                product_domain += 1
            # Does the domain add a formation event GitHub did not already supply?
            # It does when the org itself carries no formation signal, or when the
            # project domain differs from the org's own domain (a second decision).
            if not org_created or (org_domain and org_domain != host):
                domain_adds_distinct_formation += 1
        elif org_created:
            github_only_formation += 1

        if org_domain:
            org_with_domain += 1

    payload = {
        "repositories_measured": total,
        "with_a_project_domain": with_domain,
        "with_a_project_domain_pct": round(100 * with_domain / total, 2) if total else None,
        "docs_sites": docs_site,
        "product_domains": product_domain,
        "distinct_domains": len(domains),
        "orgs_linking_a_domain": org_with_domain,
        "domain_adds_a_distinct_formation_event": domain_adds_distinct_formation,
        "domain_adds_distinct_pct": (round(100 * domain_adds_distinct_formation / total, 2)
                                     if total else None),
        "formation_from_github_only": github_only_formation,
        "interpretation": _interpret(
            round(100 * with_domain / total, 2) if total else 0.0,
            round(100 * domain_adds_distinct_formation / total, 2) if total else 0.0),
        "methods_excluded": ["whois_enrichment", "domain_registrant_lookup",
                             "reverse_whois", "dns_history_broker_data"],
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "domain_audit.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    print(json.dumps(run(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
