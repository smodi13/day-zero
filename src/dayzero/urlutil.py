"""URL normalization. Concept ported from the audited X engine.

Uses only information already present in the record; never issues a network request
to resolve a redirect. x.com / twitter.com / t.co are never treated as a product
domain, and an unresolved shortener never invents an entity.
"""
from __future__ import annotations

from typing import Optional
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

TRACKING_PARAMS = {"utm_source", "utm_medium", "utm_campaign", "utm_term",
                   "utm_content", "fbclid", "gclid", "ref", "ref_src"}
NON_PRODUCT_HOSTS = {"x.com", "twitter.com", "t.co"}
CODE_HOSTS = {"github.com", "gitlab.com", "codeberg.org"}
# Discussion platforms are not a project's own domain.
POSTING_PLATFORMS = {"news.ycombinator.com", "producthunt.com", "reddit.com",
                     "linktr.ee", "medium.com", "substack.com"}


def bare_host(url: str) -> str:
    if not url:
        return ""
    host = urlparse(url if "//" in url else "https://" + url).netloc.lower()
    return host[4:] if host.startswith("www.") else host


def normalize_url(url: str) -> str:
    if not url:
        return ""
    if "//" not in url:
        url = "https://" + url
    p = urlparse(url)
    host = p.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    path = "" if p.path in ("", "/") else p.path.rstrip("/")
    query = urlencode([(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True)
                       if k.lower() not in TRACKING_PARAMS])
    return urlunparse(((p.scheme or "https").lower(), host, path, "", query, ""))


def github_owner_repo(url: str) -> Optional[str]:
    """Return `owner/repo` (or `owner`) for a code-host URL. Case preserved."""
    if bare_host(url) not in CODE_HOSTS:
        return None
    parts = [s for s in urlparse(url).path.strip("/").split("/") if s]
    if len(parts) >= 2:
        return f"{parts[0]}/{parts[1]}"
    return parts[0] if parts else None


def is_product_domain(url: str) -> bool:
    host = bare_host(url)
    return bool(host) and host not in NON_PRODUCT_HOSTS and host not in POSTING_PLATFORMS
