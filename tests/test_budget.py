
import datetime as dt
from decimal import Decimal

import pytest

from mybudget import (
    Account,
    BudgetExceededError,
    InsufficientFundsError,
    RecurringTransaction,
    Transaction,
    load,
    save,
)
from mybudget.exceptions import StatementImportError
from mybudget.importer import ImportJob, parse_statement


def make_transaction(amount="-100.00", category="groceries"):
    return Transaction(
        date=dt.date(2026, 1, 10),
        amount=Decimal(amount),
        category=category,
        description="test transaction",
    )


def test_transaction_kind():
    assert make_transaction("500.00").kind == "income"
    assert make_transaction("-100.00").kind == "expense"


def test_account_balance():
    account = Account("Test Budget")
    account.add(make_transaction("500.00"))
    account.add(make_transaction("-100.00"))

    assert account.balance == Decimal("400.00")


def test_insufficient_funds_rejected():
    account = Account("Test Budget")

    with pytest.raises(InsufficientFundsError):
        account.add(make_transaction("-100.00"))

    assert account.balance == Decimal("0")


def test_budget_limit_enforced():
    account = Account("Test Budget", allow_overdraft=True)
    account.set_budget("groceries", Decimal("100.00"))
    account.add(make_transaction("-80.00"))

    with pytest.raises(BudgetExceededError):
        account.add(make_transaction("-30.00"))

    # The rejected transaction must not be added.
    assert account.balance == Decimal("-80.00")


def test_save_and_load_round_trip(tmp_path):
    path = tmp_path / "budget.json"
    original = Account("My Test Budget", allow_overdraft=True)
    original.add(make_transaction("250.00"))
    original.add(make_transaction("-40.00"))
    original.set_budget("groceries", Decimal("300.00"))

    save(original, path)
    restored = load(path)

    assert restored.account.name == "My Test Budget"
    assert restored.account.allow_overdraft is True
    assert restored.account.balance == Decimal("210.00")
    assert restored.account.budgets["groceries"] == Decimal("300.00")
    assert restored.problems == []


def test_load_missing_file_returns_empty_account(tmp_path):
    result = load(tmp_path / "does_not_exist.json")

    assert result.account.balance == Decimal("0")
    assert result.problems == []


def test_corrupt_save_file_is_quarantined(tmp_path):
    path = tmp_path / "budget.json"
    path.write_text("{ this is not valid JSON", encoding="utf-8")

    result = load(path)

    assert result.account.balance == Decimal("0")
    assert not path.exists()
    assert (tmp_path / "budget.json.corrupt").exists()
    assert len(result.problems) == 1


def test_parse_valid_csv():
    csv_text = (
        "date,description,amount,category\n"
        "2026-01-10,Salary,2000.00,income\n"
        "2026-01-11,Groceries,-50.00,groceries\n"
    )

    transactions = parse_statement(csv_text)

    assert len(transactions) == 2
    assert transactions[0].amount == Decimal("2000.00")
    assert transactions[1].category == "groceries"


def test_parse_malformed_csv_reports_line():
    csv_text = (
        "date,description,amount,category\n"
        "2026-01-10,Salary,not-a-number,income\n"
    )

    with pytest.raises(StatementImportError) as error:
        parse_statement(csv_text)

    assert error.value.line == 2


def test_import_job_success():
    csv_text = (
        "date,description,amount,category\n"
        "2026-01-10,Salary,2000.00,income\n"
    )
    job = ImportJob()

    job.start(csv_text)
    job.join(timeout=5)

    assert job.status == "done"
    assert job.error is None
    assert len(job.result) == 1
    assert job.progress == 1.0


def test_import_job_failure():
    csv_text = (
        "date,description,amount,category\n"
        "2026-01-10,Salary,invalid,income\n"
    )
    job = ImportJob()

    job.start(csv_text)
    job.join(timeout=5)

    assert job.status == "failed"
    assert "StatementImportError" in job.error
    assert job.result is None


def test_recurring_transaction_creates_occurrences():
    recurring = RecurringTransaction(
        date=dt.date(2026, 1, 1),
        amount=Decimal("1000.00"),
        category="salary",
        description="Monthly salary",
        frequency="monthly",
    )

    occurrences = recurring.occurrences(dt.date(2026, 3, 31))

    assert len(occurrences) == 3
    assert [item.date.month for item in occurrences] == [1, 2, 3]
