"""arXiv adapter.

Uses the official export API. The site's robots.txt sets `Crawl-delay: 15` for HTML;
we never scrape /abs, and we keep a courtesy delay between API queries.

Title-phrase queries MUST be quoted (`ti:"AgentSight"`). Unquoted multi-word queries
are treated as OR by the API and return date-sorted noise — verified in Phase 1.
"""
from __future__ import annotations

import subprocess
import time
import urllib.parse
import xml.etree.ElementTree as ET
from typing import Any, Optional

NS = {"a": "http://www.w3.org/2005/Atom"}
API = "https://export.arxiv.org/api/query"
COURTESY_DELAY_SECONDS = 3.0


class ArxivError(RuntimeError):
    pass


def _fetch(url: str, timeout: int = 40) -> str:
    proc = subprocess.run(["curl", "-sS", "-m", str(timeout), url],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        raise ArxivError(f"curl failed: {proc.stderr.strip()[:200]}")
    return proc.stdout


def search_title(phrase: str, max_results: int = 4) -> list[dict[str, Any]]:
    q = urllib.parse.quote(f'ti:"{phrase}"')
    return parse_feed(_fetch(f"{API}?search_query={q}&max_results={max_results}"))


def parse_feed(xml_text: str) -> list[dict[str, Any]]:
    """Pure parser — offline-testable."""
    root = ET.fromstring(xml_text)
    out: list[dict[str, Any]] = []
    for e in root.findall("a:entry", NS):
        pub = (e.findtext("a:published", default="", namespaces=NS) or "")[:10]
        url = e.findtext("a:id", default="", namespaces=NS) or ""
        title = " ".join((e.findtext("a:title", default="", namespaces=NS) or "").split())
        authors = [a.findtext("a:name", default="", namespaces=NS)
                   for a in e.findall("a:author", NS)]
        out.append({
            "arxiv_id": url.rsplit("/", 1)[-1],
            "url": url,
            "title": title,
            "published_at": pub,
            "authors": [a for a in authors if a],
        })
    return out


def polite_sleep() -> None:
    time.sleep(COURTESY_DELAY_SECONDS)


def author_overlaps(paper_authors: list[str], contributor_names: list[str]) -> list[str]:
    """Exact, case-insensitive full-name overlap ONLY.

    Deliberately strict: partial or surname matching would merge distinct people,
    which entity resolution ER-2 forbids.
    """
    a = {n.strip().lower() for n in paper_authors if n}
    b = {n.strip().lower() for n in contributor_names if n}
    return sorted(a & b)
