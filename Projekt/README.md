# Home Expense Tracker

System monitorowania wydatków domowych zbudowany w Django z wykorzystaniem wzorca architektonicznego MVC.

## Table of Contents
- [Features](#features)
- [Technologies](#technologies)
- [Installation](#installation)
- [Running with Docker](#running-with-docker)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Tests](#tests)

## Features

| Feature | Description |
|---|---|
| **User Authentication** | Registration, login, logout — each user sees only their own data |
| **Expenses** | Add, edit, delete expenses with title, amount, date, category, description |
| **Categories** | Custom categories with color picker |
| **Budgets** | Monthly budget limits per category with progress tracking |
| **Dashboard** | Overview with statistics, pie chart by category, bar chart for last 6 months |
| **Search & Filter** | Filter expenses by title, category, date range; sort by date/amount/title |
| **Currency Rates** | Live exchange rates from NBP (National Bank of Poland) API + PLN converter |
| **Validation** | Server-side and client-side form validation |
| **Admin Panel** | Django admin for all models |

## Technologies

- **Python 3.13** + **Django 6.0**
- **Bootstrap 5.3** — responsive UI
- **Chart.js** — interactive charts
- **Bootstrap Icons** — icon library
- **SQLite** — database
- **NBP API** — free currency exchange rates (no API key required)
- **Docker** — containerization

## Installation

### Requirements
- Python 3.10+
- pip

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/pythofree/LabMVC.git
cd LabMVC/Projekt

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run migrations
python manage.py migrate

# 4. Start the server
python manage.py runserver
```

Open your browser at **http://127.0.0.1:8000**

Register a new account and start tracking your expenses!

## Running with Docker

```bash
# Build and start
docker-compose up --build

# Open http://localhost:8000
```

## Usage

1. **Register** — create your account at `/register/`
2. **Add Categories** — go to Categories and create spending categories (e.g. Food, Transport)
3. **Set Budgets** — set monthly limits per category
4. **Add Expenses** — log your daily expenses
5. **Dashboard** — view charts and statistics
6. **Currency** — check live exchange rates and convert PLN to any currency

## Project Structure (MVC)

```
Projekt/
├── expense_tracker/        # Django project (settings, urls)
├── expenses/               # Main application
│   ├── models.py           # MODEL — Category, Expense, Budget
│   ├── views.py            # CONTROLLER — all request handling logic
│   ├── forms.py            # Form validation
│   ├── urls.py             # URL routing
│   ├── admin.py            # Admin configuration
│   ├── tests.py            # Unit tests (17 tests)
│   └── templates/expenses/ # VIEW — all HTML templates
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

### Models

- **Category** — name, color, user (FK)
- **Expense** — title, amount, date, category (FK), description, user (FK)
- **Budget** — category (FK), monthly_limit, month, year, user (FK)

## Tests

```bash
python manage.py test expenses
```

Runs 17 unit tests covering models, views, and authentication.
