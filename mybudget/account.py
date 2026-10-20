"""The account (lessons 2-3)."""

from __future__ import annotations

import datetime as dt
from decimal import Decimal

from .transaction import Transaction


class Account:
    def __init__(self, name: str = "Main"):
        self.name = name
        self._transactions: list[Transaction] = []

    @property
    def balance(self) -> Decimal:
        return sum((t.amount for t in self._transactions), Decimal(0))

    @property
    def transactions(self) -> tuple[Transaction, ...]:
        return tuple(self._transactions)

    def add(self, transaction: Transaction, until: dt.date | None = None) -> list[Transaction]:
        """Add a transaction (or, for a recurring one, every occurrence up to ``until``)."""
        return self.add_many(transaction.occurrences(until))

    def add_many(self, transactions) -> list[Transaction]:
        batch = sorted(transactions, key=lambda t: t.date)
        self._transactions.extend(batch)
        return batch
