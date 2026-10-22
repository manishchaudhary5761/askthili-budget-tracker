
"""The Streamlit app for the Budget Tracker."""

from __future__ import annotations

import datetime as dt
import os

import streamlit as st

from mybudget import (
    Account,
    BudgetError,
    CategoryReport,
    MonthlyReport,
    RecurringTransaction,
    Transaction,
    load,
    save,
)
from mybudget.supabase_storage import add_transactions, load_transactions

SAVE_PATH = os.environ.get("THILIBUDGET_SAVE", "budget.json")

REPORTS = {
    "Net by month": MonthlyReport(),
    "Spending by category": CategoryReport(),
}

st.set_page_config(page_title="Budget Tracker", page_icon="💰")
st.title("Budget Tracker")


# Load the account once per Streamlit session.
if "account" not in st.session_state:
    try:
        cloud_transactions = load_transactions()

        account = Account()
        account.add_many(cloud_transactions, enforce_limits=False)

        st.session_state.account = account
        st.session_state.load_problems = []
        st.session_state.supabase_ready = True

    except Exception as exc:
        st.error(f"Could not load transactions from Supabase: {exc}")
        st.stop()

account: Account = st.session_state.account


with st.sidebar:
    st.header("Add a transaction")

    with st.form("add", clear_on_submit=True):
        when = st.date_input("Date", dt.date.today())
        kind = st.radio("Type", ["expense", "income"])
        amount = st.text_input("Amount", placeholder="12.50")
        category = st.text_input("Category", placeholder="groceries")
        description = st.text_input("Description")
        repeat = st.selectbox("Repeats", ["no", "weekly", "monthly"])

        until = (
            st.date_input("Repeat until", dt.date.today())
            if repeat != "no"
            else None
        )

        submitted = st.form_submit_button("Add")

    if submitted:
        try:
            amount_text = amount.strip()
            signed_amount = (
                "-" + amount_text if kind == "expense" else amount_text
            )

            if repeat == "no":
                transaction = Transaction.parse(
                    when.isoformat(),
                    signed_amount,
                    category,
                    description,
                )
            else:
                transaction = RecurringTransaction.parse(
                    when.isoformat(),
                    signed_amount,
                    category,
                    description,
                    frequency=repeat,
                )

            # Add and validate transactions before saving them.
            added = account.add(transaction, until=until)

            # Insert only this new batch, never the entire account.
            try:
                add_transactions(added)
            except Exception:
                # Roll back this batch in memory if cloud saving fails.
                added_ids = {id(item) for item in added}
                account._transactions = [
                    item
                    for item in account._transactions
                    if id(item) not in added_ids
                ]
                raise

            # Keep a local JSON copy as a backup.
            save(account, SAVE_PATH)

            st.success(f"Added {len(added)} transaction(s).")

        except (BudgetError, ValueError, TypeError, RuntimeError) as exc:
            st.error(str(exc))
        except Exception as exc:
            st.error(f"Could not save the transaction: {exc}")


st.subheader("Account Summary")
st.metric("Balance", f"{account.balance:,.2f}")

if account.transactions:
    st.dataframe(
        [
            {
                "date": transaction.date,
                "amount": float(transaction.amount),
                "category": transaction.category,
                "description": transaction.description,
            }
            for transaction in reversed(account.transactions)
        ],
        use_container_width=True,
    )
else:
    st.info("No transactions yet — add one in the sidebar.")

choice = st.selectbox("Report", list(REPORTS))
st.code(REPORTS[choice].render(account))
