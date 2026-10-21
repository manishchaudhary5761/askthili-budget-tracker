# AskThili Budget Tracker 💰

A Python-based budget tracking application built with Streamlit. Track income and expenses, monitor your balance, review transaction history, and generate simple financial reports through a web interface.

## 🚀 Live Demo

**[Open AskThili Budget Tracker](https://askthili-budget-tracker-bnkrjfetywxjhmdvkg2z3z.streamlit.app/)**

## ✨ Features

- **Income and expense tracking** — record transactions by date, amount, and category.
- **Balance summary** — view your current account balance.
- **Transaction history** — review recorded transactions in a table.
- **Financial reports** — view monthly net totals and spending by category.
- **Data persistence** — save and load account data using JSON.
- **Input validation and error handling** — handle invalid transaction inputs and budget-related errors.
- **Interactive web interface** — use a Streamlit sidebar form to add transactions.

## 🛠️ Tech Stack

- **Language:** Python
- **Web framework:** Streamlit
- **Data storage:** JSON file
- **Date and money handling:** Python `datetime` and `Decimal`
- **Version control:** Git and GitHub
- **Deployment:** Streamlit Community Cloud

## 📂 Project Structure

```text
learnfast/
├── budget_app.py
├── budget_tracker.ipynb
├── requirements.txt
└── mybudget/
    ├── __init__.py
    ├── transaction.py
    ├── account.py
    ├── reports.py
    ├── exceptions.py
    └── storage.py
```

## 💻 Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/manishchaudhary5761/askthili-budget-tracker.git
cd askthili-budget-tracker
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Start the application

```bash
python -m streamlit run budget_app.py
```

Open the local URL displayed in your terminal, usually `http://localhost:8501`.

## 🧪 Testing

The project has been developed incrementally, with tests and manual checks for transaction validation, balance calculations, JSON persistence, transaction history, and report selection.

## 🔒 Data Storage Note

The application uses a JSON file for persistence. Local files on hosted platforms may not be permanent across restarts or redeployments. A database-backed storage solution would be a future improvement.

Avoid entering sensitive financial information into this demo.

## 🔮 Future Improvements

- Monthly budget limits and spending alerts
- Visual charts for income and expenses
- CSV import and export
- Improved automated test coverage
- Database-backed persistent storage
- More detailed reporting and filtering

## 👨‍💻 Author

**Manish Chaudhary**

GitHub: [@manishchaudhary5761](https://github.com/manishchaudhary5761)

---

*Built as a hands-on Python learning project to practice object-oriented programming, exception handling, data persistence, reporting, and web application deployment.*
