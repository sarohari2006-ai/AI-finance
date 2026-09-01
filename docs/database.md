# Database Design

SQLAlchemy ORM models in `backend/app/models/models.py`. Default engine is SQLite
(`ai_finance.db` in `backend/`); set `DATABASE_URL` to a PostgreSQL DSN to switch (schema is
identical — SQLAlchemy handles the dialect differences).

## Entity-relationship summary

```
User (1) ──── (1)  FinancialProfile
User (1) ──── (N)  Transaction
User (1) ──── (N)  FinancialGoal
User (1) ──── (N)  Loan
User (1) ──── (N)  Insurance
User (1) ──── (N)  Investment
User (1) ──── (N)  LiteracyAttempt
User (1) ──── (N)  RiskAssessment
User (1) ──── (N)  BehaviorAnalysis
User (1) ──── (N)  Recommendation
User (1) ──── (N)  Notification

LiteracyQuestion (standalone reference table, seeded once)
RiskQuestion (standalone reference table, seeded once)
```

Every user-owned table has a `user_id` foreign key to `users.id` with `ondelete="CASCADE"` —
deleting a user cleans up all their data. Every user-scoped query in the API layer filters by
`user_id`, enforcing per-user data isolation at the application layer in addition to the schema.

## Tables

### `users`
| Column | Type | Notes |
|---|---|---|
| id | PK | |
| name | string(120) | |
| email | string(255) | unique, indexed |
| hashed_password | string(255) | bcrypt hash, never plaintext |
| age | int, nullable | |
| occupation | string(120), nullable | |
| created_at / updated_at | datetime | |

### `financial_profiles`
One-to-one with `users` (unique `user_id`). Holds `education_level`, `monthly_income`,
`monthly_expenses`, `current_savings`, `monthly_investment_contribution`, `emergency_fund`.

### `transactions`
`date`, `category` (food/shopping/transport/entertainment/utilities/rent/healthcare/education/
subscriptions/travel/salary/other), `amount`, `type` (income/expense enum), `description`.
Composite index on `(user_id, date)` for efficient date-range filtering.

### `financial_goals`
`name`, `goal_type`, `target_amount`, `current_amount`, `target_date`, `priority` (low/medium/
high enum), `status` (in_progress/achieved/behind enum).

### `loans`
`loan_type`, `principal_amount`, `outstanding_amount`, `interest_rate`, `emi`, `start_date`,
`tenure_months`.

### `insurances`
`insurance_type` (health/life/vehicle/home/other), `provider`, `coverage_amount`,
`premium_amount`, `premium_frequency`, `start_date`, `end_date`.

### `investments`
`investment_type` (stocks/mutual_funds/fd/ppf/gold/crypto/other), `name`, `invested_amount`,
`current_value`, `start_date`.

### `literacy_questions` (reference data, seeded)
`question`, `options` (JSON-encoded list), `correct_answer`, `explanation`, `topic`.

### `literacy_attempts`
One row per quiz submission: `score_percentage`, `level` (beginner/basic/intermediate/advanced
enum), `answers` (JSON), `total_questions`, `correct_count`. The most recent attempt per user
determines their current literacy level.

### `risk_questions` (reference data, seeded)
`question`, `options` (JSON-encoded list of `{text, score}`), `factor` (e.g.
investment_experience, income_stability).

### `risk_assessments`
One row per submission: `total_score`, `risk_level` (low/moderate/high enum), `answers` (JSON).

### `behavior_analyses`
One row per analysis run: the 9 engineered features (see
[ai-recommendation.md](ai-recommendation.md)), plus `cluster_label` and `cluster_id` from K-Means.

### `recommendations`
`title`, `category` (savings/investment/insurance/credit/goal), `recommendation`, `priority`
(high/medium/low), `reason`, `supporting_metrics` (JSON), `expected_benefit`, `action`,
`explanation_type` (rule_based/ml_based/hybrid), `is_read`. Regenerated (old rows deleted, new
rows inserted) each time `/api/recommendations` or `/api/dashboard` is called, so it always
reflects the user's current data.

### `notifications`
`type` (budget_exceeded/emi_reminder/goal_reminder/unusual_spending/savings_goal), `title`,
`message`, `is_read`, `severity` (info/warning/critical). Rule-based alerts are deduplicated per
24-hour window on `(user_id, type, title)` so polling doesn't spam duplicates.

## Indexes

- `users.email` — unique, for login lookups
- `financial_profiles.user_id` — unique, enforces the 1:1 relationship
- `transactions.user_id`, composite `(user_id, date)` — for per-user, date-filtered queries
- All other user-owned tables index `user_id` for per-user scoping

## Constraints

- Foreign keys with `ondelete="CASCADE"` on every user-owned table
- Pydantic schemas enforce non-negative amounts, valid enum values, and required fields at the
  API boundary before anything reaches the database
