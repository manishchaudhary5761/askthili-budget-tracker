
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

SAVE_PATH = os.environ.get("THILIBUDGET_SAVE", "budget.json")

REPORTS = {
    "Net by month": MonthlyReport(),
    "Spending by category": CategoryReport(),
}

st.set_page_config(page_title="Budget Tracker", page_icon="💰")
st.title("Budget Tracker")

# Keep the account available when Streamlit reruns the app.
if "account" not in st.session_state:
    result = load(SAVE_PATH)
    st.session_state.account = result.account
    st.session_state.load_problems = result.problems

account: Account = st.session_state.account

for problem in st.session_state.get("load_problems", []):
    st.warning(problem)

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

            added = account.add(transaction, until=until)
            save(account, SAVE_PATH)
            st.success(f"Added {len(added)} transaction(s).")

        except (BudgetError, ValueError, TypeError) as exc:
            st.error(str(exc))

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
