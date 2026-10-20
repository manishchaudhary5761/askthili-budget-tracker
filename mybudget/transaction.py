"""Transactions (lessons 2-3)."""

from __future__ import annotations

import calendar
import datetime as dt
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

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
            raise ValueError(
                f"amount must be a finite Decimal, got {self.amount!r}"
            )

        if self.amount == 0:
            raise ValueError("amount must not be zero")

        if not isinstance(self.category, str) or not self.category.strip():
            raise ValueError("category must not be empty")

        if not isinstance(self.description, str):
            raise ValueError("description must be a string")

    @classmethod
    def parse(
        cls,
        date: str,
        amount: str,
        category: str,
        description: str = "",
    ) -> Transaction:
        """Create a transaction from text values."""
        try:
            parsed_date = dt.date.fromisoformat(date)
            parsed_amount = Decimal(amount)
        except (ValueError, TypeError, InvalidOperation) as error:
            raise ValueError(
                f"Invalid transaction data: {error}"
            ) from error

        return cls(
            date=parsed_date,
            amount=parsed_amount,
            category=category,
            description=description,
        )

    @property
    def kind(self) -> str:
        return "income" if self.amount > 0 else "expense"

    def occurrences(
        self,
        until: dt.date | None = None,
    ) -> list[Transaction]:
        """A normal transaction represents itself."""
        return [self]


@dataclass(frozen=True)
class RecurringTransaction(Transaction):
    frequency: str = "monthly"

    def __post_init__(self) -> None:
        super().__post_init__()

        if self.frequency not in FREQUENCIES:
            raise ValueError(
                f"frequency must be one of {FREQUENCIES}, "
                f"got {self.frequency!r}"
            )

    def _nth(self, n: int) -> dt.date:
        if self.frequency == "weekly":
            return self.date + dt.timedelta(weeks=n)

        year_offset, month_index = divmod(
            self.date.month - 1 + n, 12
        )
        year = self.date.year + year_offset
        month = month_index + 1
        day = min(
            self.date.day,
            calendar.monthrange(year, month)[1],
        )

        return dt.date(year, month, day)

    def occurrences(
        self,
        until: dt.date | None = None,
    ) -> list[Transaction]:
        until = until or self.date
        results: list[Transaction] = []
        n = 0

        while (when := self._nth(n)) <= until:
            results.append(
                Transaction(
                    when,
                    self.amount,
                    self.category,
                    self.description,
                )
            )
            n += 1

        return results
