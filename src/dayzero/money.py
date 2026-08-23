"""Exact decimal currency. Concept ported from the audited X engine.

Monetary values are never floats. Cost that is genuinely unknown is recorded as
UNKNOWN, never as a guessed number, and never as 0.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any, Optional

PLACES = 6
UNKNOWN = "UNKNOWN"
_PLACEHOLDERS = {"placeholder", "tbd", "unset", "n/a", "na", "none", "null", "pending"}


class MoneyError(ValueError):
    pass


def parse_money(raw: Any, *, field: str = "value", allow_zero: bool = True) -> Decimal:
    if isinstance(raw, bool):
        raise MoneyError(f"{field}: boolean is not a monetary value")
    if raw is None:
        raise MoneyError(f"{field}: missing monetary value")
    if isinstance(raw, float):
        raise MoneyError(f"{field}: float not allowed; quote as a decimal string")
    if isinstance(raw, Decimal):
        d = raw
    else:
        s = str(raw).strip()
        if not s:
            raise MoneyError(f"{field}: empty monetary value")
        if s.lower() in _PLACEHOLDERS:
            raise MoneyError(f"{field}: placeholder {s!r} is not an amount")
        try:
            d = Decimal(s)
        except InvalidOperation as exc:
            raise MoneyError(f"{field}: {s!r} is not a valid decimal") from exc
    if not d.is_finite():
        raise MoneyError(f"{field}: non-finite value not allowed")
    if d < 0:
        raise MoneyError(f"{field}: negative value not allowed")
    if d == 0 and not allow_zero:
        raise MoneyError(f"{field}: zero not allowed here")
    return d


def money_str(value: Optional[Decimal], places: int = PLACES) -> str:
    """Serialize a Decimal as fixed-point. None serializes to the UNKNOWN marker."""
    if value is None:
        return UNKNOWN
    if isinstance(value, float):
        raise MoneyError("refusing to serialize a float as money")
    return str(value.quantize(Decimal(1).scaleb(-places)))
