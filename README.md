# AskThili Budget Tracker 💰

A Python budget-tracking application built with Streamlit. Record income and expenses, monitor balances, set category budgets, generate reports, and import transactions from CSV statements.

## Live Demo

[Open AskThili Budget Tracker](https://askthili-budget-tracker-bnkrjfetywxjhmdvkg2z3z.streamlit.app/)

## Features

- **Income and expense tracking:** Record transactions with dates, amounts, categories, and descriptions.
- **Balance calculation:** Calculate the account balance using decimal arithmetic.
- **Budget controls:** Set category spending limits and apply overdraft protection.
- **Financial reports:** Review monthly totals, category spending, and top expenses.
- **Recurring transactions:** Generate weekly or monthly transaction occurrences.
- **CSV statement import:** Validate statement data and report malformed rows.
- **Background imports:** Track import status, progress, results, and errors safely.
- **Data persistence:** Save and load budget data using JSON, with additional Supabase storage integration in the application.
- **Error handling:** Handle invalid transactions, budget violations, and corrupted local save files.
- **Automated tests:** Test core functionality and important failure cases using pytest.

## Tech Stack

- **Language:** Python
- **Web framework:** Streamlit
- **Database integration:** Supabase
- **Local persistence:** JSON
- **Money handling:** `decimal.Decimal`
- **Date handling:** Python `datetime`
- **Testing:** pytest
- **Version control:** Git and GitHub
- **Deployment:** Streamlit Community Cloud

## Project Structure

```text
learnfast/
├── budget_app.py
├── budget_tracker.ipynb
├── requirements.txt
├── tests/
│   └── test_budget.py
└── mybudget/
    ├── __init__.py
    ├── account.py
    ├── exceptions.py
    ├── importer.py
    ├── reports.py
    ├── storage.py
    ├── supabase_storage.py
    └── transaction.py
```

## Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/manishchaudhary5761/askthili-budget-tracker.git
cd askthili-budget-tracker
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it in Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file containing the Supabase settings required by the application. Obtain your own credentials from your Supabase project settings. Never commit `.env` or expose secret keys publicly.

### 5. Run the app

```powershell
python -m streamlit run budget_app.py
```

Open the local address displayed in the terminal, usually `http://localhost:8501`.

## Run Automated Tests

From the project root, with the virtual environment activated:

```powershell
python -m pytest -v
```

The current test suite contains 12 tests covering transactions, balances, overdraft protection, budget limits, save/load behavior, corrupt-file recovery, CSV parsing, background imports, and recurring transactions.

## Design Notes

- **`Transaction` and `RecurringTransaction`:** A recurring transaction extends the regular transaction model with a frequency and occurrence-generation behavior.
- **`Report`:** A shared report abstraction allows different report types to use a consistent interface.
- **`ImportJob`:** Keeps background import status, progress, results, and errors in a thread-safe object instead of having a worker thread directly modify Streamlit session state.
-