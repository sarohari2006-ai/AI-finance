# Architecture

## System overview

```
┌──────────────┐        HTTPS/JSON        ┌───────────────────┐        SQL        ┌────────────┐
│   Frontend    │ ───────────────────────▶ │      Backend       │ ─────────────────▶ │  Database  │
│  React + TS   │ ◀─────────────────────── │  FastAPI + SQLAlch │ ◀───────────────── │ SQLite/PG  │
└──────────────┘                          └───────────────────┘                    └────────────┘
```

- **Frontend** (`frontend/`): React 19 + TypeScript SPA built with Vite, styled with Tailwind
  CSS, charted with Recharts, routed with React Router. Talks to the backend exclusively over a
  typed Axios client (`src/services/`). A JWT is stored in `localStorage` and attached to every
  request via an Axios interceptor; a 401 response clears it and redirects to `/login`.
- **Backend** (`backend/`): FastAPI application exposing a REST API under `/api`. Organized into
  `api/` (route handlers), `models/` (SQLAlchemy ORM models), `schemas/` (Pydantic request/response
  models), `services/` (deterministic calculations, financial health, notifications, and the
  pipeline orchestrator), `analytics/` (behavioral feature engineering + clustering), `ml/` (the
  recommendation engine), `auth/` (JWT + password hashing), and `database/` (SQLAlchemy session
  management).
- **Database**: SQLAlchemy ORM over SQLite by default (zero-config, file-based, fine for a
  single-instance academic project) or PostgreSQL when `DATABASE_URL` is set.

## Data pipeline

Every dashboard/recommendation/behavior-analysis request runs the same pipeline
(`backend/app/services/pipeline.py`):

```
Raw user data (profile, transactions, goals, loans, insurance, investments)
        │
        ▼
Validation                  Pydantic schemas at the API boundary (types, ranges, required fields)
        │
        ▼
Cleaning / Normalization     Falls back from empty transaction history to profile-level
                              monthly figures; category maps normalize essential vs. discretionary
        │
        ▼
Feature Engineering          app/analytics/behavior.py — 9 behavioral features computed from
                              transactions, loans, and profile (savings rate, discretionary ratio,
                              spending volatility, debt burden, etc.)
        │
        ▼
Behavioral Analysis (ML)     K-Means clustering (scikit-learn) assigns one of 5 archetypes
        │
        ▼
Risk Assessment               User-submitted questionnaire → Low/Moderate/High risk level
                              (deterministic scoring, not ML)
        │
        ▼
Financial Health Calculation  app/services/financial_health.py — 7 weighted, independently
                              documented component scores combined into a 0-100 score
        │
        ▼
Recommendation Engine         app/ml/recommendation_engine.py — rule engine combining all of the
                              above into category-tagged, prioritized recommendations
        │
        ▼
Explainability                Every recommendation carries `reason` + `supporting_metrics` sourced
                              directly from the user's own computed values
        │
        ▼
Dashboard                     app/api/dashboard.py aggregates all of the above into one response
```

This pipeline re-runs on each relevant request rather than being precomputed on a schedule —
appropriate for the data volumes in this academic project (a single user's transactions), and it
guarantees the dashboard is always consistent with the latest data (no caching staleness).

## Request lifecycle example: `GET /api/dashboard`

1. `get_current_user` (auth dependency) decodes the JWT and loads the `User` row; a missing/
   invalid token returns 401 before any handler code runs.
2. `build_context()` loads the user's profile, transactions, loans, insurance, investments, and
   goals, and computes every deterministic metric (savings rate, DTI, emergency-fund months,
   goal progress, etc.) — all scoped to `user_id`, so no cross-user data ever enters the response.
3. `compute_health_score()` turns that context into the 7-component Financial Health Score.
4. `refresh_recommendations()` re-runs the recommendation engine and persists fresh
   `Recommendation` rows (replacing the previous set) so `/recommendations/{id}` stays consistent
   with what the dashboard just showed.
3. `generate_alerts()` evaluates rule-based alert conditions, writing new `Notification` rows
   (deduplicated within a 24h window per alert type+title).
4. The handler assembles all of the above into `DashboardOut` and FastAPI serializes it as JSON.

## Security model

- Passwords are hashed with bcrypt (`passlib`/`bcrypt`), never stored or returned in plaintext.
- JWTs are signed with `SECRET_KEY` (HS256) and expire after `ACCESS_TOKEN_EXPIRE_MINUTES`
  (default 24h).
- Every data-access endpoint filters by `Transaction.user_id == current_user.id` (and equivalent
  for other tables) at the query level — a user cannot even enumerate another user's record IDs,
  since a mismatched `user_id` returns 404, not 403 (no existence leak).
- CORS is restricted to local dev origins via `main.py`'s `allow_origin_regex`; tighten this to an
  explicit origin list before any real deployment.

## Notification architecture

`app/services/notifications.py` defines an abstract `NotificationChannel` with one method,
`send()`. The default `InAppNotificationChannel` implementation persists notifications to the
`notifications` table for the frontend to poll. Swapping in a real email/SMS/push provider later
means implementing one new `NotificationChannel` subclass — no other code changes, and the app
never blocks on external notification credentials being unavailable.
