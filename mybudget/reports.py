"""Reports (lesson 3): abstraction."""

from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal

from .account import Account


class Report(ABC):
    title = "Report"

    @abstractmethod
    def generate(self, account: Account) -> list[tuple[str, Decimal]]:
        """Return (label, amount) rows. Each subclass decides what the rows mean."""

    def render(self, account: Account) -> str:
        rows = self.generate(account)
        lines = [self.title, "-" * len(self.title)]
        lines += [f"{label:<20}{amount:>14,.2f}" for label, amount in rows]
        if not rows:
            lines.append("(no transactions)")
        return "\n".join(lines)

class CategoryReport(Report):
    title = "Spending by Category"

    def generate(self, account: Account) -> list[tuple[str, Decimal]]:
        totals: dict[str, Decimal] ={}

        for transaction in account.transactions:
            category = transaction.category
            totals[category] = (
                totals.get(category, Decimal("0.00"))
                + transaction.amount
            )

        return sorted(totals.items())


class BalanceReport(Report):
    title = "Account Balance"

    def generate(self, account: Account) -> list[tuple[str, Decimal]]:
        income = sum(
            (t.amount for t in account.transactions if t.amount > 0),
            Decimal("0.00")
        )

        expenses = sum(
            (t.amount for t in account.transactions if t.amount < 0),
            Decimal("0.00")
        )

        return [
            ("Total income", income),
            ("Total expenses", expenses),
            ("Final balance", account.balance),
        ]
