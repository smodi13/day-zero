from __future__ import annotations
from datetime import date
from typing import Optional


def iso_to_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    return date.fromisoformat(value[:10])
