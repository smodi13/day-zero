"""Frozen-rules manifest and drift guard.

The historical holdout and the negative-control suite may only run against a
recorded, hashed rule configuration. If the working config no longer matches the
manifest, those commands FAIL CLOSED — the manifest is never silently regenerated.

This is the mechanism that makes "the rules existed before the results" checkable by
someone who was not in the room.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

from .config import CONFIG_DIR, FROZEN_RULE_FILES, OUTPUT_DIR
from .timeutil import now_utc, to_rfc3339

MANIFEST_PATH = OUTPUT_DIR / "frozen_rules_manifest.json"
SCHEMA_VERSION = "dayzero-rules-1"


class FreezeError(RuntimeError):
    pass


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def file_hash(name: str) -> str:
    """Hash the PARSED content, not the bytes — comments and whitespace are not rules."""
    data = yaml.safe_load((CONFIG_DIR / name).read_text(encoding="utf-8"))
    return hashlib.sha256(_canonical(data).encode("utf-8")).hexdigest()


def current_hashes() -> dict[str, str]:
    return {name: file_hash(name) for name in sorted(FROZEN_RULE_FILES)}


def combined_hash(hashes: dict[str, str]) -> str:
    return hashlib.sha256(_canonical(hashes).encode("utf-8")).hexdigest()


def create_manifest(engine_version: str, git_commit: str = "PENDING") -> dict[str, Any]:
    hashes = current_hashes()
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "engine_version": engine_version,
        "git_commit": git_commit,
        "created_at": to_rfc3339(now_utc()),
        "files": hashes,
        "combined_hash": combined_hash(hashes),
    }
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(_canonical(manifest) + "\n", encoding="utf-8")
    return manifest


def load_manifest() -> dict[str, Any]:
    if not MANIFEST_PATH.exists():
        raise FreezeError(
            "No frozen rules manifest found. Historical validation cannot proceed "
            "until the evaluation rules are explicitly frozen "
            "(`python -m dayzero freeze`).")
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def require_frozen() -> dict[str, Any]:
    """Fail closed on any drift. Never regenerates the manifest."""
    manifest = load_manifest()
    now = current_hashes()
    drifted = [n for n, h in now.items() if manifest["files"].get(n) != h]
    missing = [n for n in manifest["files"] if n not in now]
    if drifted or missing:
        raise FreezeError(
            "Frozen evaluation configuration has changed. Historical validation "
            "cannot proceed without explicitly creating a new methodological "
            f"version. Drifted: {drifted or '[]'}; missing: {missing or '[]'}")
    if combined_hash(now) != manifest["combined_hash"]:
        raise FreezeError(
            "Frozen evaluation configuration has changed (combined hash mismatch). "
            "Historical validation cannot proceed without explicitly creating a new "
            "methodological version.")
    return manifest
