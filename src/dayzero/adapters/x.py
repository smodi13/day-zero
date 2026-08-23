"""X (Twitter) adapter — DISABLED BY DEFAULT and FAIL-CLOSED.

DAY ZERO must run, and must be useful, without paid X access. Live ingestion runs
only when every one of the following holds:

  1. `DAYZERO_X_ENABLED=1` is explicitly set,
  2. a bearer token is present in the environment,
  3. a pricing reference exists and is not stale,
  4. the estimated cost is computable and within the approved budget,
  5. an explicit approval fingerprint has been recorded.

Any missing precondition returns a refusal, never a partial run. No credential is
ever logged, printed, or written to an output file.

Where live access is unavailable, X evidence enters through manually-recorded,
clearly-labelled seed records (`ingest_mode: MANUAL_RESEARCH_SOURCE`).
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Optional

from ..money import money_str, parse_money

ENV_ENABLE = "DAYZERO_X_ENABLED"
ENV_TOKEN = "X_BEARER_TOKEN"

# Reference rates carried over from the audited engine's pricing config. They are a
# REVIEWER-SUPPLIED reference, not live pricing, and they are past their staleness
# gate — which is itself a reason the guard fails closed.
REFERENCE_RATES = {
    "post_read_usd": "0.005",
    "user_read_usd": "0.010",
    "counts_recent_request_usd": "0.005",
}
REFERENCE_DATE = "2026-07-18"
STALENESS_DAYS = 30


@dataclass(frozen=True)
class XGuardResult:
    allowed: bool
    reason: str
    estimated_cost_usd: Optional[str] = None
    fingerprint: Optional[str] = None


def is_enabled() -> bool:
    return os.environ.get(ENV_ENABLE) == "1"


def has_credentials() -> bool:
    return bool(os.environ.get(ENV_TOKEN, "").strip())


def estimate_cost(*, posts: int = 0, users: int = 0, count_requests: int = 0) -> Decimal:
    total = Decimal("0")
    total += parse_money(REFERENCE_RATES["post_read_usd"]) * posts
    total += parse_money(REFERENCE_RATES["user_read_usd"]) * users
    total += parse_money(REFERENCE_RATES["counts_recent_request_usd"]) * count_requests
    return total


def request_fingerprint(spec: dict[str, Any]) -> str:
    """SHA-256 over the FULL canonical request, not just the query text.

    Changing fields, expansions, page size, or the config version changes the
    fingerprint and therefore invalidates any prior approval.
    """
    blob = json.dumps(spec, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def guard(*, spec: dict[str, Any], budget_usd: str, posts: int = 0, users: int = 0,
          count_requests: int = 0, approved_fingerprint: Optional[str] = None,
          pricing_verified_at: Optional[str] = None,
          today: Optional[str] = None) -> XGuardResult:
    """Fail-closed precondition check. Returns a refusal rather than raising, so the
    build can continue without X."""
    if not is_enabled():
        return XGuardResult(False, f"{ENV_ENABLE} is not set: X ingestion is off by default")
    if not has_credentials():
        return XGuardResult(False, "no X bearer token present in the environment")

    # Pricing staleness: a stale reference cannot authorise spend.
    from datetime import date
    ref = pricing_verified_at or REFERENCE_DATE
    now = date.fromisoformat(today) if today else date.today()
    if (now - date.fromisoformat(ref)).days > STALENESS_DAYS:
        return XGuardResult(False,
                            f"pricing reference {ref} is older than {STALENESS_DAYS} days; "
                            "re-verify X pricing before any spend")

    est = estimate_cost(posts=posts, users=users, count_requests=count_requests)
    budget = parse_money(budget_usd, field="x.budget")
    if est > budget:
        return XGuardResult(False,
                            f"estimated {money_str(est)} exceeds approved budget {money_str(budget)}",
                            money_str(est))

    fp = request_fingerprint(spec)
    if approved_fingerprint != fp:
        return XGuardResult(False,
                            "no matching approval for this exact request fingerprint",
                            money_str(est), fp)
    return XGuardResult(True, "all preconditions satisfied", money_str(est), fp)


def redact(token: Optional[str]) -> str:
    """Never print a credential. Used only in diagnostics output."""
    return "<absent>" if not token else f"<redacted:{len(token)} chars>"
