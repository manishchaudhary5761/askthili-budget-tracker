
"""The Streamlit app for the Budget Tracker."""

from __future__ import annotations
import hashlib

import datetime as dt
import os
import time

import streamlit as st

from mybudget import (
    Account,
    BudgetError,
    CategoryReport,
    MonthlyReport,
    RecurringTransaction,
    Transaction,
    save,
)
from mybudget.importer import ImportJob
from mybudget.supabase_storage import add_transactions, load_transactions

SAVE_PATH = os.environ.get("THILIBUDGET_SAVE", "budget.json")

REPORTS = {
    "Net by month": MonthlyReport(),
    "Spending by category": CategoryReport(),
}

st.set_page_config(page_title="Budget Tracker", page_icon="💰")
st.title("Budget Tracker")


# Load transactions from Supabase once per Streamlit session.
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

# Keep the import job available across Streamlit reruns.
if "import_job" not in st.session_state:
    st.session_state.import_job = ImportJob()

if "saved_csv_hashes" not in st.session_state:
    st.session_state.saved_csv_hashes = set()

job: ImportJob = st.session_state.import_job


# Sidebar: add a single or recurring transaction.
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

            # Validate and add transactions in memory.
            added = account.add(transaction, until=until)

            # Save only the new transactions to Supabase.
            try:
                add_transactions(added)
            except Exception:
                # Roll back the in-memory batch if cloud saving fails.
                added_ids = {id(item) for item in added}
                account._transactions = [
                    item
                    for item in account._transactions
                    if id(item) not in added_ids
                ]
                raise

            # Keep a local JSON backup.
            save(account, SAVE_PATH)
            st.success(f"Added {len(added)} transaction(s).")

        except (BudgetError, ValueError, TypeError, RuntimeError) as exc:
            st.error(str(exc))
        except Exception as exc:
            st.error(f"Could not save the transaction: {exc}")


# CSV importer: parse statements in the background.
st.subheader("Import bank statement (CSV)")

uploaded_file = st.file_uploader(
    "Choose a CSV file",
    type=["csv"],
    key="bank_statement_upload",
)

if uploaded_file is not None and job.status == "idle":
    if st.button("Import transactions", key="start_csv_import"):
        try:
            csv_text = uploaded_file.getvalue().decode("utf-8-sig")
            job.start(csv_text)
            st.rerun()
        except Exception as exc:
            st.error(f"Could not start import: {exc}")

if job.status == "running":
    st.progress(job.progress, text="Importing transactions...")
    time.sleep(0.3)
    st.rerun()



elif job.status == "done":
    st.success(
        f"CSV parsed successfully: {len(job.result or [])} transaction(s)."
    )

    uploaded_file = st.session_state.get("bank_statement_upload")
    csv_hash = None

    if uploaded_file is not None:
        csv_hash = hashlib.sha256(
            uploaded_file.getvalue()
        ).hexdigest()

    saved_hashes = st.session_state.saved_csv_hashes

    if csv_hash and csv_hash in saved_hashes:
        st.success("This CSV has already been saved during this session.")
    else:
        st.warning(
            "Preview only: these transactions have not been saved yet."
        )

        if st.button(
            "Save imported transactions to Supabase",
            key="save_csv_import",
        ):
            imported_transactions = job.result or []

            if not imported_transactions:
                st.warning("There are no transactions to save.")
            elif not csv_hash:
                st.error("Please select the CSV file again.")
            elif csv_hash in st.session_state.saved_csv_hashes:
                st.warning("This CSV has already been saved.")
            else:
                try:
                    add_transactions(imported_transactions)

                    account.add_many(
                        imported_transactions,
                        enforce_limits=False,
                    )
                    save(account, SAVE_PATH)

                    st.session_state.saved_csv_hashes.add(csv_hash)
                    st.session_state.csv_import_saved = True

                    st.success(
                        f"Saved {len(imported_transactions)} transaction(s)!"
                    )
                    st.rerun()

                except Exception as exc:
                    st.error(f"Could not complete the import: {exc}")
                    st.warning(
                        "Check Supabase before retrying. The cloud insert "
                        "may have succeeded even if a later step failed."
                    )

    if st.button("Dismiss import preview", key="dismiss_import_preview"):
        job.reset()
        st.session_state.csv_import_saved = False
        st.rerun()



elif job.status == "failed":
    st.error(f"CSV import failed: {job.error}")

    if st.button("Dismiss import error", key="dismiss_csv_error"):
        job.reset()
        st.rerun()


# Account summary and transaction history.
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


# Reports.
choice = st.selectbox("Report", list(REPORTS))
st.code(REPORTS[choice].render(account))
