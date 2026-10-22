
"""Supabase storage for AskThili Budget Tracker demo transactions."""

from __future__ import annotations

import datetime as dt
import os
from decimal import Decimal

from dotenv import load_dotenv
from supabase import Client, create_client

from .transaction import Transaction

# Load .env when running locally. Streamlit Cloud can use its Secrets settings.
load_dotenv()


def get_client() -> Client:
    """Connect to Supabase using environment variables."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise RuntimeError(
            "Supabase configuration is missing. Set SUPABASE_URL "
            "and SUPABASE_KEY in your .env file or Streamlit Secrets."
        )

    return create_client(url, key)


def load_transactions() -> list[Transaction]:
    """Fetch demo transactions from Supabase."""
    response = (
        get_client()
        .table("transactions")
        .select("transaction_date, amount, category, description")
        .order("transaction_date")
        .order("id")
        .execute()
    )

    transactions = []

    for row in response.data:
        transactions.append(
            Transaction(
                date=dt.date.fromisoformat(row["transaction_date"]),
                amount=Decimal(str(row["amount"])),
                category=row["category"],
                description=row.get("description") or "",
            )
        )

    return transactions


def add_transactions(transactions: list[Transaction]) -> None:
    """Insert new transactions into Supabase."""
    if not transactions:
        return

    rows = [
        {
            "transaction_date": transaction.date.isoformat(),
            "amount": str(transaction.amount),
            "category": transaction.category,
            "description": transaction.description,
        }
        for transaction in transactions
    ]

    get_client().table("transactions").insert(rows).execute()
