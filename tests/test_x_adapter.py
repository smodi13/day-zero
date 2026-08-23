"""X is off by default, fails closed, cannot promote alone, and leaks no credential."""
import os
from datetime import date
from decimal import Decimal

import pytest

from dayzero.adapters import x
from dayzero.money import MoneyError, money_str, parse_money
from dayzero.review import Candidate, evaluate
from dayzero.signals import DerivedSignal


def test_disabled_by_default(monkeypatch):
    monkeypatch.delenv(x.ENV_ENABLE, raising=False)
    assert x.is_enabled() is False
    r = x.guard(spec={"q": "a"}, budget_usd="5", posts=10)
    assert r.allowed is False and "off by default" in r.reason


def test_fails_closed_without_credentials(monkeypatch):
    monkeypatch.setenv(x.ENV_ENABLE, "1")
    monkeypatch.delenv(x.ENV_TOKEN, raising=False)
    assert x.guard(spec={"q": "a"}, budget_usd="5").allowed is False


def test_fails_closed_on_stale_pricing(monkeypatch):
    monkeypatch.setenv(x.ENV_ENABLE, "1")
    monkeypatch.setenv(x.ENV_TOKEN, "tok")
    r = x.guard(spec={"q": "a"}, budget_usd="5", posts=1,
                pricing_verified_at="2026-01-01", today="2026-08-23")
    assert r.allowed is False and "stale" in r.reason or "older than" in r.reason


def test_fails_closed_over_budget(monkeypatch):
    monkeypatch.setenv(x.ENV_ENABLE, "1")
    monkeypatch.setenv(x.ENV_TOKEN, "tok")
    r = x.guard(spec={"q": "a"}, budget_usd="0.01", posts=1000,
                pricing_verified_at="2026-08-20", today="2026-08-23")
    assert r.allowed is False and "exceeds approved budget" in r.reason


def test_fails_closed_without_matching_approval(monkeypatch):
    monkeypatch.setenv(x.ENV_ENABLE, "1")
    monkeypatch.setenv(x.ENV_TOKEN, "tok")
    r = x.guard(spec={"q": "a"}, budget_usd="50", posts=10,
                pricing_verified_at="2026-08-20", today="2026-08-23",
                approved_fingerprint="wrong")
    assert r.allowed is False and "fingerprint" in r.reason


def test_full_preconditions_allow(monkeypatch):
    monkeypatch.setenv(x.ENV_ENABLE, "1")
    monkeypatch.setenv(x.ENV_TOKEN, "tok")
    spec = {"q": "a", "fields": ["id"], "page_size": 10, "config_version": 1}
    fp = x.request_fingerprint(spec)
    r = x.guard(spec=spec, budget_usd="50", posts=10,
                pricing_verified_at="2026-08-20", today="2026-08-23",
                approved_fingerprint=fp)
    assert r.allowed is True


def test_fingerprint_changes_with_any_request_field():
    a = x.request_fingerprint({"q": "a", "page_size": 10})
    b = x.request_fingerprint({"q": "a", "page_size": 100})
    assert a != b


def test_credentials_are_never_echoed():
    assert "secret" not in x.redact("secret-token-value")
    assert x.redact(None) == "<absent>"


def test_exact_decimal_cost_math():
    assert x.estimate_cost(posts=3) == Decimal("0.015")
    assert money_str(x.estimate_cost(posts=1, users=1)) == "0.015000"
    with pytest.raises(MoneyError):
        parse_money(0.1)  # float source rejected


def test_x_alone_cannot_produce_intro_ready():
    sigs = [DerivedSignal("B-01", "BUILD", "r", "repository", "2026-01-01", "x", "OBSERVED", ""),
            DerivedSignal("D-01", "TECHNICAL_DEPTH", "r", "repository", "2026-01-01", "x", "OBSERVED", ""),
            DerivedSignal("F-01", "FORMATION", "r", "repository", "2026-02-01", "x", "OBSERVED", ""),
            DerivedSignal("F-02", "FORMATION", "o", "organization", "2026-03-01", "x", "OBSERVED", "")]
    c = Candidate("k", "p", {"description": "agent sandbox isolation", "topics": [],
                             "language": "Rust", "homepage": "https://x.dev",
                             "construction": {"days_since_push": 3}},
                  sigs, "high", "unregistered", "FORMING", ["agent_execution_isolation"],
                  {"technical_question": "q", "commercial_or_formation_question": "q"},
                  None, {"x"})
    d = evaluate(c, date(2026, 8, 23))
    assert d.state != "INTRO_READY"
    assert d.drop_reason == "SINGLE_CHANNEL_ONLY"


def test_no_x_records_were_ingested(conn):
    n = conn.execute("SELECT COUNT(*) FROM social_signals WHERE channel='x'").fetchone()[0]
    assert n == 0
