
"""Reports: abstraction and polymorphism."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict
from decimal import Decimal

from .account import Account


class Report(ABC):
    title = "Report"

    @abstractmethod
    def generate(self, account: Account) -> list[tuple[str, Decimal]]:
        """Return report rows."""

    def render(self, account: Account) -> str:
        rows = self.generate(account)
        lines = [self.title, "-" * len(self.title)]
        lines += [
            f"{label:<20}{amount:>14,.2f}"
            for label, amount in rows
        ]

        if not rows:
            lines.append("(no transactions)")

        return "\n".join(lines)


class MonthlyReport(Report):
    title = "Net by month"

    def generate(self, account: Account) -> list[tuple[str, Decimal]]:
        totals: dict[str, Decimal] = defaultdict(Decimal)

        for transaction in account.transactions:
            month = transaction.date.strftime("%Y-%m")
            totals[month] += transaction.amount

        return sorted(totals.items())


class CategoryReport(Report):
    title = "Spending by category"

    def generate(self, account: Account) -> list[tuple[str, Decimal]]:
        totals: dict[str, Decimal] = defaultdict(Decimal)

        for transaction in account.transactions:
            if transaction.amount < 0:
                totals[transaction.category] += -transaction.amount

        return sorted(
            totals.items(),
            key=lambda row: row[1],
            reverse=True,
        )


class TopExpensesReport(Report):
    title = "Biggest expenses"

    def __init__(self, n: int = 5):
        if n < 0:
            raise ValueError("n must not be negative")
        self.n = n

    def generate(self, account: Account) -> list[tuple[str, Decimal]]:
        expenses = [
            (f"{transaction.date} {transaction.category}", -transaction.amount)
            for transaction in account.transactions
            if transaction.amount < 0
        ]

        return sorted(
            expenses,
            key=lambda row: row[1],
            reverse=True,
        )[:self.n]
