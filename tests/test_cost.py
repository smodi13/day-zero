"""Exact Decimal currency. Free is 0. Unknown is UNKNOWN. Nothing is invented."""
from decimal import Decimal

import pytest

from dayzero.cost import CostLedger
from dayzero.money import UNKNOWN, MoneyError, money_str, parse_money


def test_floats_are_rejected():
    with pytest.raises(MoneyError):
        parse_money(0.005)


def test_negative_is_rejected():
    with pytest.raises(MoneyError):
        parse_money("-1")


def test_placeholder_is_rejected():
    with pytest.raises(MoneyError):
        parse_money("TBD")


def test_zero_is_a_valid_free_cost():
    assert parse_money("0") == Decimal("0")


def test_unknown_serializes_as_unknown_not_zero():
    assert money_str(None) == UNKNOWN
    assert money_str(None) != "0.000000"


def test_ledger_sums_exactly(tmp_path):
    led = CostLedger(tmp_path / "l.jsonl", "run")
    led.record(source="github", api="rest", requests=10, units=10,
               unit_label="api_request", estimated_cost_usd="0")
    led.record(source="x", api="search", requests=1, units=100,
               unit_label="post", estimated_cost_usd="0.5")
    total, unknown = led.total_estimated()
    assert total == Decimal("0.5") and unknown == 0


def test_ledger_counts_unknown_costs_separately(tmp_path):
    led = CostLedger(tmp_path / "l.jsonl", "run")
    led.record(source="x", api="search", requests=1, units=1, unit_label="post",
               estimated_cost_usd=None)
    total, unknown = led.total_estimated()
    assert total == Decimal("0") and unknown == 1


def test_recorded_costs_are_all_free_in_this_build(conn):
    rows = conn.execute("SELECT estimated_cost_usd, source FROM cost_ledger").fetchall()
    assert rows
    for cost, source in rows:
        assert cost == "0.000000", f"{source} recorded a non-zero estimated cost"


def test_actual_cost_is_unknown_not_zero(conn):
    rows = conn.execute("SELECT actual_cost_usd FROM cost_ledger").fetchall()
    for (actual,) in rows:
        assert actual == UNKNOWN
