
"""The account (lessons 2-5): budget and overdraft protection."""

from __future__ import annotations

import datetime as dt
from collections import defaultdict
from decimal import Decimal

from .exceptions import (
    BudgetExceededError,
    InsufficientFundsError,
    InvalidTransactionError,
)
from .transaction import Transaction


class Account:
    def __init__(self, name: str = "Main", allow_overdraft: bool = False):
        self.name = name
        self.allow_overdraft = allow_overdraft
        self._transactions: list[Transaction] = []
        self._budgets: dict[str, Decimal] = {}

    @property
    def balance(self) -> Decimal:
        return sum((t.amount for t in self._transactions), Decimal(0))

    @property
    def transactions(self) -> tuple[Transaction, ...]:
        return tuple(self._transactions)

    @property
    def budgets(self) -> dict[str, Decimal]:
        return dict(self._budgets)

    def spent(self, category: str, year: int, month: int) -> Decimal:
        """Return total spending in a category for a calendar month."""
        return sum(
            (
                -t.amount
                for t in self._transactions
                if t.category == category
                and t.amount < 0
                and (t.date.year, t.date.month) == (year, month)
            ),
            Decimal(0),
        )

    def set_budget(self, category: str, monthly_limit: Decimal) -> None:
        if not monthly_limit.is_finite() or monthly_limit <= 0:
            raise InvalidTransactionError("A budget limit must be positive and finite")
        self._budgets[category.strip().lower()] = monthly_limit

    def add(
        self, transaction: Transaction, until: dt.date | None = None
    ) -> list[Transaction]:
        """Add a transaction or all its recurring occurrences."""
        return self.add_many(transaction.occurrences(until))

    def add_many(
        self, transactions, *, enforce_limits: bool = True
    ) -> list[Transaction]:
        """Add a batch atomically: either all transactions are accepted or none."""
        batch = sorted(transactions, key=lambda t: t.date)

        if enforce_limits:
            self._check(batch)

        self._transactions.extend(batch)
        return batch

    def _check(self, batch: list[Transaction]) -> None:
        balance = self.balance
        spent_in_batch: dict[tuple[str, int, int], Decimal] = defaultdict(Decimal)

        for transaction in batch:
            balance += transaction.amount

            if transaction.amount >= 0:
                continue

            if not self.allow_overdraft and balance < 0:
                raise InsufficientFundsError(
                    balance - transaction.amount,
                    -transaction.amount,
                )

            category = transaction.category.strip().lower()
            limit = self._budgets.get(category)

            if limit is not None:
                key = (category, transaction.date.year, transaction.date.month)

                if key not in spent_in_batch:
                    spent_in_batch[key] = self.spent(*key)

                spent_in_batch[key] += -transaction.amount

                if spent_in_batch[key] > limit:
                    raise BudgetExceededError(
                        category,
                        limit,
                        spent_in_batch[key],
                    )
