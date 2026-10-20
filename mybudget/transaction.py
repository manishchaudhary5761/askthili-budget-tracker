"""Transactions (lessons 2-3)."""

from __future__ import annotations

import calendar
import datetime as dt
from dataclasses import dataclass
from decimal import Decimal

FREQUENCIES = ("weekly", "monthly")


@dataclass(frozen=True)
class Transaction:
    date: dt.date
    amount: Decimal
    category: str
    description: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.date, dt.date):
            raise ValueError(f"date must be a date, got {self.date!r}")
        if not isinstance(self.amount, Decimal) or not self.amount.is_finite():
            raise ValueError(f"amount must be a finite Decimal, got {self.amount!r}")
        if self.amount == 0:
            raise ValueError("amount must not be zero")
        if not self.category.strip():
            raise ValueError("category must not be empty")

    @property
    def kind(self) -> str:
        return "income" if self.amount > 0 else "expense"

    def occurrences(self, until: dt.date | None = None) -> list[Transaction]:
        """The concrete transactions this one stands for. A plain transaction is just itself."""
        return [self]


@dataclass(frozen=True)
class RecurringTransaction(Transaction):
    frequency: str = "monthly"

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.frequency not in FREQUENCIES:
            raise ValueError(f"frequency must be one of {FREQUENCIES}, got {self.frequency!r}")

    def _nth(self, n: int) -> dt.date:
        if self.frequency == "weekly":
            return self.date + dt.timedelta(weeks=n)
        year_offset, month_index = divmod(self.date.month - 1 + n, 12)
        year, month = self.date.year + year_offset, month_index + 1
        day = min(self.date.day, calendar.monthrange(year, month)[1])
        return dt.date(year, month, day)

    def occurrences(self, until: dt.date | None = None) -> list[Transaction]:
        until = until or self.date
        out: list[Transaction] = []
        n = 0
        while (when := self._nth(n)) <= until:
            out.append(Transaction(when, self.amount, self.category, self.description))
            n += 1
        return out
