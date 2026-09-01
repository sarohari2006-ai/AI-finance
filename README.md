# AI-Based Intelligent Financial Advisory System

An academic mini-project that provides personalized, explainable financial guidance based on a
user's income, expenses, savings, investments, goals, risk tolerance, loans/credit, insurance,
financial literacy, and spending behavior.

> **Disclaimer**: This system provides educational and personalized financial guidance based on
> the information provided by the user. It does not constitute professional financial, investment,
> insurance, tax, or legal advice.

## 1. Problem Statement

Individuals with limited financial literacy struggle to make informed decisions about savings,
investments, insurance, and credit. Existing financial advisory services can be complex,
expensive, inaccessible, and insufficiently personalized.

## 2. Solution

A full-stack web application that:
- Collects a user's financial profile, transactions, goals, loans, insurance, and investments
- Runs the user through a financial-literacy quiz and a risk-tolerance questionnaire
- Analyzes spending behavior using feature engineering + K-Means clustering
- Computes a transparent, weighted **Financial Health Score (0-100)**
- Generates **personalized, explainable recommendations** across savings, investments,
  insurance, and credit/debt, each traceable to the user's own numbers
- Presents everything on a fintech-style dashboard with charts, goal tracking, and alerts

## 3. Architecture

```
frontend/   React + TypeScript + Vite + Tailwind CSS + Recharts + React Router
backend/    Python + FastAPI + SQLAlchemy + scikit-learn/pandas/numpy
database/   SQLite by default (zero-config); PostgreSQL supported via DATABASE_URL
```

See [docs/architecture.md](docs/architecture.md) for the full data pipeline diagram,
[docs/database.md](docs/database.md) for the schema, [docs/api.md](docs/api.md) for every
endpoint, and [docs/ai-recommendation.md](docs/ai-recommendation.md) for exactly how scores and
recommendations are computed (with formulas).

## 4. Features

- JWT authentication with bcrypt-hashed passwords, protected routes, per-user data isolation
- Financial profile, transactions (CRUD + filters), multi-goal tracking with progress bars
- Loans/credit, insurance, and investments tracking
- 12-question financial-literacy assessment with per-question explanations and a Beginner →
  Advanced level classification
- 7-factor risk-tolerance questionnaire producing Low / Moderate / High risk profiles
- Behavioral analytics: 9 engineered features (savings rate, discretionary ratio, spending
  volatility, debt burden, etc.) clustered via K-Means into 5 behavioral archetypes
- Transparent, formula-documented Financial Health Score with a 7-component breakdown
- Hybrid rule-based recommendation engine covering Savings / Investment / Insurance / Credit /
  Goals, each with a "Why am I seeing this?" explanation citing the user's actual numbers
- Dashboard with income/expense, spending-by-category, savings-trend, and investment-growth
  charts, goal cards, top recommendations, behavioral/risk/literacy summaries, and alerts
- Rule-based notification/alert system (budget exceeded, high EMI burden, goal reminders,
  high discretionary spending), deduplicated per 24h window
- Demo/seed data: 3 users with deliberately different financial profiles, so the recommendation
  engine visibly produces different output per user

## 5. Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, TypeScript, Vite, Tailwind CSS v3, Recharts, React Router v7, Axios |
| Backend | Python 3.11, FastAPI, SQLAlchemy 2.0, Pydantic v2 |
| Database | SQLite (default, zero-config) or PostgreSQL (`DATABASE_URL`) |
| AI/ML | scikit-learn (K-Means clustering), pandas, numpy |
| Auth | JWT (python-jose), bcrypt password hashing |
| Testing | pytest (backend), 41 tests covering auth, calculations, isolation, edge cases |

## 6. Setup Instructions

### Prerequisites
- Python 3.11+ (Windows: the `py` launcher)
- Node.js 18+ and npm

### Quickest start (Windows): `run.bat`

From the project root, just double-click **`run.bat`** (or run it from a terminal). It will:
1. Detect Python and Node.js on your PATH
2. Create the backend virtual environment and install all Python dependencies (first run only)
3. Seed the database with question banks and 3 demo users (first run only)
4. Install frontend npm dependencies (first run only)
5. Launch the backend (port 8001) and frontend (port 5173) each in their own window

Re-running it later skips steps that are already done and just starts both servers — so it's
also the everyday "start the app" command, not just a one-time installer. Run **`stop.bat`** to
close both server windows. No manual `pip install` / `npm install` / `venv` steps needed as long
as Python and Node.js themselves are installed on the machine.

### Manual setup

#### Backend

```powershell
cd backend
py -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
copy .env.example .env          # optional — defaults to local SQLite automatically
.\venv\Scripts\python.exe scripts\seed.py     # creates DB, seeds questions + 3 demo users
.\venv\Scripts\python.exe -m uvicorn app.main:app --port 8001
```

The API is now live at `http://127.0.0.1:8001`, with interactive docs at
`http://127.0.0.1:8001/docs`.

To use PostgreSQL instead of SQLite, set `DATABASE_URL` in `backend/.env`:
```
DATABASE_URL=postgresql://user:password@localhost:5432/ai_finance
```

#### Frontend

```powershell
cd frontend
npm install
copy .env.example .env          # points VITE_API_BASE_URL at the backend
npm run dev
```

Open the URL Vite prints (typically `http://localhost:5173`).

### Demo Credentials

All demo accounts use the password `password123`:

| Email | Profile |
|---|---|
| `asha@example.com` | Low income, high expenses, low savings, low risk tolerance |
| `rohan@example.com` | Moderate income, balanced expenses, moderate risk tolerance |
| `priya@example.com` | High income, strong savings, higher risk tolerance |

Re-running `scripts/seed.py` is idempotent — it skips users/questions that already exist.

## 7. Testing

```powershell
cd backend
.\venv\Scripts\python.exe -m pytest tests/ -v
```

41 tests covering: registration/login, password hashing, protected-route auth, per-user data
isolation (a user cannot read/modify another user's records), deterministic financial
calculations (savings rate, DTI, emergency-fund months, goal progress), financial health scoring,
and edge cases (zero income, negative amounts, missing fields, new user with no transactions/
goals/investments, multiple loans, over-achieved goals).

## 8. AI/ML Methodology (summary)

See [docs/ai-recommendation.md](docs/ai-recommendation.md) for full detail. In short:

- **Deterministic calculations** (no ML): savings rate, debt-to-income ratio, emergency-fund
  coverage, goal contribution requirements, financial health score components.
- **ML**: K-Means clustering (scikit-learn) over 9 engineered behavioral features, fit against
  5 hand-defined reference archetype centroids, to classify each user into a behavioral
  archetype (Disciplined Saver, High Discretionary Spender, Inconsistent Saver, Debt-Heavy,
  Balanced Planner).
- **Recommendation engine**: a rule engine that combines the deterministic metrics, the ML-derived
  behavioral label, the user's risk profile, and literacy level to select and word
  recommendations. Every recommendation carries the exact supporting numbers that triggered it —
  there is no black-box scoring of *whether* to recommend something.

This is intentionally a transparent hybrid system rather than a deep-learning model — the
available dataset (a single user's self-reported financial data) does not justify a more complex
model, and the project explicitly prioritizes explainability over false sophistication.

## 9. Known Limitations

- Single-currency (₹) assumption; no multi-currency support
- No real bank/brokerage integrations — all data is user-entered or seeded demo data
- Notification delivery is in-app only (persisted to the database); the `NotificationChannel`
  abstraction in `backend/app/services/notifications.py` is ready for a real email/push/SMS
  provider to be plugged in without touching calling code
- K-Means clustering re-fits on every request against a small fixed reference set rather than a
  persisted, incrementally-trained model — appropriate for this dataset size, but not how a
  production system with millions of users would do it
- No forgot-password email flow (endpoint is intentionally out of scope per the academic nature
  of this project)

## 10. Future Improvements

- Real notification channels (email/SMS/push) behind the existing abstraction
- Persisted/versioned ML models with periodic retraining as transaction history grows
- Multi-currency and localization support
- Bank/brokerage account aggregation (e.g. via Plaid-style integrations)
- SHAP/LIME-based explanations if a genuine ML-scored ranking model is introduced later
