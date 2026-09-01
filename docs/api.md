# API Documentation

Base URL: `http://127.0.0.1:8001/api` (local dev). Interactive Swagger UI at `/docs`, ReDoc at
`/redoc`. All endpoints except `/auth/register` and `/auth/login` require a bearer token:

```
Authorization: Bearer <access_token>
```

## Auth

| Method | Path | Description |
|---|---|---|
| POST | `/auth/register` | Create account. Body: `name, email, password, age?, occupation?`. Returns `{access_token, user}`. |
| POST | `/auth/login` | Body: `email, password`. Returns `{access_token, user}`. |
| GET | `/auth/me` | Returns the current authenticated user. |

## Financial Profile

| Method | Path | Description |
|---|---|---|
| GET | `/profile` | Get (or lazily create) the current user's financial profile. |
| PUT | `/profile` | Partial update: `education_level, monthly_income, monthly_expenses, current_savings, monthly_investment_contribution, emergency_fund`. |

## Transactions

| Method | Path | Description |
|---|---|---|
| GET | `/transactions?category=&type=&start_date=&end_date=` | List, with optional filters. |
| POST | `/transactions` | Create. Body: `date, category, amount (>0), type (income\|expense), description?`. |
| PUT | `/transactions/{id}` | Partial update. 404 if not owned by the caller. |
| DELETE | `/transactions/{id}` | Delete. 404 if not owned by the caller. |

## Goals

| Method | Path | Description |
|---|---|---|
| GET | `/goals` | List, each with computed `progress_percentage`, `remaining_amount`, `recommended_monthly_contribution`. |
| POST | `/goals` | Create. Body: `name, goal_type, target_amount, current_amount, target_date, priority`. |
| PUT | `/goals/{id}` | Partial update. Auto-marks `status: achieved` when `current_amount >= target_amount`. |
| DELETE | `/goals/{id}` | Delete. |

## Loans

| Method | Path | Description |
|---|---|---|
| GET | `/loans` | List. |
| POST | `/loans` | Create. Body: `loan_type, principal_amount, outstanding_amount, interest_rate, emi, start_date?, tenure_months?`. |
| DELETE | `/loans/{id}` | Delete. |

## Insurance

| Method | Path | Description |
|---|---|---|
| GET | `/insurance` | List. |
| POST | `/insurance` | Create. Body: `insurance_type, provider?, coverage_amount, premium_amount, premium_frequency, start_date?, end_date?`. |
| DELETE | `/insurance/{id}` | Delete. |

## Investments

| Method | Path | Description |
|---|---|---|
| GET | `/investments` | List, each with computed `returns_percentage`. |
| POST | `/investments` | Create. Body: `investment_type, name?, invested_amount, current_value, start_date?`. |
| DELETE | `/investments/{id}` | Delete. |

## Financial Literacy

| Method | Path | Description |
|---|---|---|
| GET | `/literacy/questions` | List all questions (no answers included). |
| POST | `/literacy/submit` | Body: `{answers: {question_id: selected_option_text}}`. Returns score, level, and a per-question breakdown with explanations. |
| GET | `/literacy/result` | Latest result summary (no breakdown). 404 if never attempted. |

## Risk Assessment

| Method | Path | Description |
|---|---|---|
| GET | `/risk/questions` | List all questions with scored options. |
| POST | `/risk/submit` | Body: `{answers: {question_id: selected_option_index}}`. Returns total score and risk level. |
| GET | `/risk/result` | Latest result. 404 if never attempted. |

## Behavioral Analysis

| Method | Path | Description |
|---|---|---|
| GET | `/behavior-analysis` | Runs the feature engineering + K-Means pipeline fresh and returns the 9 features, cluster label, and plain-language insights. |

## Financial Health

| Method | Path | Description |
|---|---|---|
| GET | `/financial-health` | Returns `{score, category, components, explanation}` — see [ai-recommendation.md](ai-recommendation.md) for the formula. |

## Recommendations

| Method | Path | Description |
|---|---|---|
| GET | `/recommendations` | Regenerates and returns all current recommendations, sorted by priority. |
| GET | `/recommendations/{id}` | Get one recommendation (marks it read). 404 if not owned by the caller. |

## Notifications

| Method | Path | Description |
|---|---|---|
| GET | `/notifications` | Regenerates rule-based alerts (deduplicated per 24h), returns the 50 most recent. |
| PUT | `/notifications/{id}/read` | Mark one notification as read. |

## Dashboard

| Method | Path | Description |
|---|---|---|
| GET | `/dashboard` | Aggregates financial health, income/expense/savings/investment trends, spending by category, goals, top 5 recommendations, behavioral profile, risk level, literacy level, and recent alerts into one response. |

## Error format

Validation errors (422) follow FastAPI/Pydantic's standard shape:
```json
{"detail": [{"loc": ["body", "amount"], "msg": "...", "type": "..."}]}
```
Application errors (400/401/404) return `{"detail": "human-readable message"}`.
