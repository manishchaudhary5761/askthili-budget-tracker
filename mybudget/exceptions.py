
"""Custom exceptions for the budget tracker."""

from decimal import Decimal


class BudgetError(Exception):
    """Base class for budget tracker errors."""


class InvalidTransactionError(BudgetError, ValueError):
    """Raised when transaction data is invalid."""


class InsufficientFundsError(BudgetError):
    """Raised when an expense would cause an overdraft."""

    def __init__(self, balance: Decimal, needed: Decimal):
        self.balance = balance
        self.needed = needed
        super().__init__(
            f"Balance {balance:,.2f} cannot cover an expense of {needed:,.2f}"
        )


class BudgetExceededError(BudgetError):
    """Raised when spending exceeds a category's monthly budget."""

    def __init__(self, category: str, limit: Decimal, would_be: Decimal):
        self.category = category
        self.limit = limit
        self.would_be = would_be
        super().__init__(
            f"'{category}' budget is {limit:,.2f} this month; "
            f"this would make it {would_be:,.2f}"
        )


class StatementImportError(BudgetError):
    """Raised when a bank statement cannot be imported."""

    def __init__(self, message: str, line: int | None = None):
        self.line = line
        super().__init__(f"line {line}: {message}" if line else message)


class DuplicateTransactionError(BudgetError):
    """Raised when a transaction has already been recorded."""

    def __init__(self, transaction):
        self.transaction = transaction
        super().__init__(
            f"Already recorded: {transaction.date} "
            f"{transaction.category} {transaction.amount}"
        )