"""Deterministic identifiers.

Every id is a stable function of natural keys, so a rebuild from the same collected
data produces byte-identical output (tested by `test_determinism`).
"""
from __future__ import annotations

import hashlib


def _h(*parts: str) -> str:
    joined = "\x1f".join(p.strip() for p in parts)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()[:16]


def entity_id(kind: str, natural_key: str) -> str:
    return f"{kind}:{_h(kind, natural_key)}"


def identity_id(channel: str, handle: str) -> str:
    return entity_id("identity", f"{channel.lower()}/{handle.lower()}")


def person_id(anchor_channel: str, anchor_handle: str) -> str:
    return entity_id("person", f"{anchor_channel.lower()}/{anchor_handle.lower()}")


def repo_id(full_name: str) -> str:
    return entity_id("repo", full_name.lower())


def org_id(host: str, login: str) -> str:
    return entity_id("org", f"{host.lower()}/{login.lower()}")


def paper_id(arxiv_id: str) -> str:
    return entity_id("paper", arxiv_id.lower())


def project_id(name: str, anchor: str) -> str:
    return entity_id("project", f"{name.lower()}|{anchor.lower()}")


def company_id(name: str, domain: str) -> str:
    return entity_id("company", f"{name.lower()}|{domain.lower()}")


def source_id(url: str) -> str:
    return entity_id("src", url.lower())


def evidence_id(entity: str, claim_type: str, src: str, evidence_date: str) -> str:
    return entity_id("ev", f"{entity}|{claim_type}|{src}|{evidence_date}")


def signal_id(subject: str, signal_type: str, observed_at: str) -> str:
    return entity_id("sig", f"{subject}|{signal_type}|{observed_at}")


def relationship_id(a: str, kind: str, b: str) -> str:
    return entity_id("rel", f"{a}|{kind}|{b}")
