"""Configuration loading and rule-freezing.

The evaluation rules that govern the historical holdout are serialized and hashed
BEFORE the holdout runs. The hash is recorded in the holdout output, so any later
edit to a rule file is detectable.
"""
from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = REPO_ROOT / "config"
DATA_DIR = REPO_ROOT / "data"
OUTPUT_DIR = REPO_ROOT / "outputs"

# Files whose content defines the frozen evaluation behaviour.
FROZEN_RULE_FILES = (
    "signal_types.yaml",
    "formation_states.yaml",
    "technical_dimensions.yaml",
    "source_quality.yaml",
    "intro_queue_rules.yaml",
    "holdout_rules.yaml",
    "negative_control_rules.yaml",
    "career_signal_classes.yaml",
    "review_states.yaml",
)


class ConfigError(RuntimeError):
    pass


@lru_cache(maxsize=None)
def load(name: str) -> dict[str, Any]:
    path = CONFIG_DIR / name
    if not path.exists():
        raise ConfigError(f"missing config: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ConfigError(f"config {name} did not parse to a mapping")
    return data


def frozen_rules_payload() -> dict[str, Any]:
    """Canonical, order-stable representation of every frozen rule file."""
    return {name: load(name) for name in sorted(FROZEN_RULE_FILES)}


def frozen_rules_hash() -> str:
    blob = json.dumps(frozen_rules_payload(), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def signal_family(signal_type: str) -> str:
    sig = load("signal_types.yaml")["signals"].get(signal_type)
    if not sig:
        raise ConfigError(f"unknown signal type: {signal_type}")
    return sig["family"]


def barred_attention_fields() -> set[str]:
    return set(load("signal_types.yaml")["barred_from_surfacing"])


def forbidden_score_fields() -> set[str]:
    return set(load("technical_dimensions.yaml")["forbidden_fields"])
