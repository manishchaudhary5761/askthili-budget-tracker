
"""Persistence: save and load budget accounts safely."""

from __future__ import annotations

import json
import os
import shutil
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from pathlib import Path

from .account import Account
from .exceptions import BudgetError
from .transaction import Transaction

SCHEMA_VERSION = 1


@dataclass
class LoadResult:
    account: Account
    problems: list[str] = field(default_factory=list)


def save(account: Account, path: str | Path) -> None:
    path = Path(path)
    payload = {
        "version": SCHEMA_VERSION,
        "name": account.name,
        "allow_overdraft": account.allow_overdraft,
        "budgets": {category: str(value) for category, value in account.budgets.items()},
        "transactions": [
            {
                "date": transaction.date.isoformat(),
                "amount": str(transaction.amount),
                "category": transaction.category,
                "description": transaction.description,
            }
            for transaction in account.transactions
        ],
    }

    temporary_path = path.with_name(path.name + ".tmp")
    temporary_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    os.replace(temporary_path, path)


def load(path: str | Path) -> LoadResult:
    path = Path(path)

    if not path.exists():
        return LoadResult(Account())

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("top level is not an object")
    except (OSError, ValueError, UnicodeDecodeError) as error:
        quarantine = path.with_name(path.name + ".corrupt")
        os.replace(path, quarantine)
        return LoadResult(
            Account(),
            [f"{path.name} was unreadable ({error}); kept as {quarantine.name}"],
        )

    account = Account(
        name=str(data.get("name", "Main")),
        allow_overdraft=bool(data.get("allow_overdraft", False)),
    )
    problems: list[str] = []

    budgets = data.get("budgets") or {}
    if not isinstance(budgets, dict):
        problems.append("budgets skipped: expected a JSON object")
        budgets = {}

    for category, limit in budgets.items():
        try:
            account.set_budget(category, Decimal(limit))
        except (InvalidOperation, TypeError, ValueError, BudgetError) as error:
            problems.append(f"budget {category!r} skipped: {error}")

    records = data.get("transactions") or []
    if not isinstance(records, list):
        problems.append("transactions skipped: expected a JSON list")
        records = []

    good_transactions = []

    for index, record in enumerate(records):
        try:
            if not isinstance(record, dict):
                raise TypeError("record must be a JSON object")

            good_transactions.append(
                Transaction.parse(
                    record["date"],
                    record["amount"],
                    record["category"],
                    record.get("description", ""),
                )
            )
        except (KeyError, TypeError, AttributeError, ValueError, BudgetError) as error:
            problems.append(f"transaction #{index + 1} skipped: {error!r}")

    account.add_many(good_transactions, enforce_limits=False)
    return LoadResult(account, problems)

def save_with_backup(account: Account, path: str | Path) -> None:
    """Back up the existing file before saving new account data."""
    path = Path(path)

    if path.exists():
        backup_path = path.with_name(path.name + ".bak")
        shutil.copy2(path, backup_path)

    save(account, path)