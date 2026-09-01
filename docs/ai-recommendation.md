# AI / Recommendation Methodology

This document is the authoritative reference for exactly how scores and recommendations are
computed. Every formula below is implemented verbatim in the referenced source file — nothing
here is aspirational.

## 1. What is deterministic vs. ML

| Component | Type | File |
|---|---|---|
| Savings rate, debt-to-income ratio, emergency-fund coverage, goal progress | Deterministic | `app/services/calculations.py` |
| Financial Health Score (0-100) | Deterministic (weighted formula) | `app/services/financial_health.py` |
| Behavioral feature engineering (9 features) | Deterministic (pandas/numpy) | `app/analytics/behavior.py` |
| Behavioral archetype classification | **ML — K-Means clustering** | `app/analytics/behavior.py` |
| Risk tolerance level | Deterministic (weighted questionnaire average) | `app/api/risk.py` |
| Financial literacy level | Deterministic (percentage correct) | `app/api/literacy.py` |
| Recommendation selection & wording | Deterministic rule engine, **consuming the ML-derived behavioral label as one input** | `app/ml/recommendation_engine.py` |

The recommendation engine is a **hybrid rule-based system**: the rules themselves are fixed
condition→template logic (not learned), but one of their inputs (the behavioral archetype) comes
from an unsupervised ML model. Recommendations are tagged `explanation_type: "hybrid"` when a
behavioral label was available, `"rule_based"` otherwise — the frontend surfaces this on every
recommendation's detail page so it's never misrepresented as a black-box prediction.

We do not use a supervised model to decide *whether* to fire a recommendation, because there is
no labeled outcome data (e.g., "did the user's finances improve after this recommendation?") to
train one against. Pretending otherwise would be dishonest about what the system does.

## 2. Financial Health Score (0-100)

`compute_financial_health()` in `app/services/financial_health.py`. Seven components, each scored
0-100 independently via a simple linear rule, then combined by fixed weights:

| Component | Weight | Rule |
|---|---|---|
| Savings | 25% | `savings_rate% / 20 * 100`, clamped to [0,100]. A 20%+ savings rate scores 100. |
| Debt | 20% | `100 - (DTI% / 40 * 100)`, clamped. 0% DTI scores 100; 40%+ DTI scores 0. |
| Emergency fund | 15% | `months_covered / 6 * 100`, clamped. 6+ months scores 100. |
| Goals | 15% | Average goal progress percentage across all active goals (100 if no goals exist — nothing to be behind on). |
| Spending | 10% | 100 if discretionary ratio ≤ 30%; 0 if ≥ 70%; linear in between. |
| Investment | 10% | `investment_consistency * 100` (monthly investment contribution as a fraction of income, capped at 100%). |
| Insurance | 5% | 100 if both health and life insurance on file; 50 if one; 0 if neither. |

Final score = Σ(component_score × weight), rounded to 1 decimal.

Category label: **Strong** (80-100), **Good** (60-79), **Fair** (40-59), **Needs Attention** (0-39).

The API response (`GET /api/financial-health`) returns every component score alongside a
human-readable `explanation` string citing the user's actual numbers, e.g. *"Debt-to-income ratio
of 13.9% (weight 20%)."*

## 3. Behavioral Analytics (K-Means clustering)

### Feature engineering (`compute_features()`)

Nine features are computed per user from their transaction history, loans, and profile:

1. `savings_rate` — (income − expenses) / income, clamped to [-1, 1]
2. `discretionary_ratio` / `essential_ratio` — share of expenses in discretionary vs. essential
   categories (essential = rent, utilities, healthcare, transport, education)
3. `spending_volatility` — std. dev. of monthly expenses / mean monthly expenses, capped at 1.0
4. `savings_consistency` — fraction of tracked months where income > expenses
5. `debt_burden` — total monthly EMI / monthly income, capped at 1.0
6. `investment_consistency` — months with recorded investment activity / months tracked
7. `recurring_expense_ratio` — spend in recurring categories (rent, utilities, subscriptions,
   insurance) / total expenses
8. `category_concentration` — Herfindahl index (Σ share²) of expense categories; higher means
   spending is concentrated in fewer categories

### Clustering (`classify_behavior()`)

Five reference archetypes are hand-defined as points in this 9-dimensional feature space, based
on domain knowledge of what each archetype looks like:

- **Disciplined Saver** — high savings rate, low discretionary ratio, high consistency
- **High Discretionary Spender** — low savings rate, high discretionary ratio
- **Inconsistent Saver** — high spending volatility, low savings consistency
- **Debt-Heavy** — high debt burden, low savings rate
- **Balanced Planner** — moderate values across the board

`sklearn.cluster.KMeans` (n_clusters=5, random_state=42) is fit over the 5 reference points plus
the current user's feature vector; the user is assigned to whichever cluster its nearest
reference archetype also falls into. This lets a single user be classified meaningfully without
needing a large training population — appropriate for an academic project where each user's data
is analyzed independently, while still using genuine unsupervised clustering rather than a
lookup table.

The `/api/behavior-analysis` endpoint returns the archetype label plus 3+ plain-language insights
generated from the underlying feature values (e.g. *"Discretionary spending represents 43% of
your monthly expenses."*).

## 4. Recommendation Engine

`generate_recommendations(context)` in `app/ml/recommendation_engine.py` evaluates a fixed set of
condition → template rules across four categories, using the full computed context (financial
health inputs, behavioral label, risk level, literacy level, goals):

- **Savings**: low savings rate (<10%), insufficient emergency fund (<6 months), high
  discretionary spending (>40%)
- **Credit/Debt**: high EMI burden (DTI >40% high priority, >20% medium), high-interest loans
  (≥12% p.a.) flagged for priority repayment
- **Investment**: emergency-fund-first guidance when coverage <3 months; risk-profile-appropriate
  allocation guidance (low/moderate/high risk wording); low contribution-rate nudge
- **Insurance**: missing health insurance (high priority), missing life insurance (medium)
- **Goals**: any goal <50% progress gets a contribution-rate recommendation

Wording is adjusted by literacy level: `beginner`/`basic` users get simpler, more directive
language; `intermediate`/`advanced` users get more technical phrasing (e.g. "diversified
equity/index funds" vs. "may consider a higher allocation toward equity").

Every recommendation object carries:

```
title, category, recommendation, priority, reason,
supporting_metrics (the exact numbers that triggered the rule),
expected_benefit, action, explanation_type
```

No recommendation ever fabricates a number — `supporting_metrics` is always built directly from
the same `context` dict used to evaluate the rule condition, so the "why" shown to the user is
provably the same data that fired the rule.

## 5. Explainability ("Why am I seeing this?")

Each recommendation's detail page (`GET /api/recommendations/{id}`, rendered at
`/recommendations/:id` in the frontend) shows:
- The `reason` string (plain-language explanation)
- `supporting_metrics` as a labeled data table (the user's own numbers)
- `expected_benefit` and the concrete `action` to take
- The `explanation_type` (`rule_based` or `hybrid`), so users know whether an ML-derived signal
  (behavioral archetype) contributed

We do not use SHAP/LIME because there is no trained supervised model whose feature attributions
would need explaining — the K-Means cluster assignment is inherently interpretable (nearest
reference archetype in a named, documented feature space), and the recommendation rules are
already fully transparent condition→action logic. Applying SHAP/LIME here would be decorative,
not explanatory, so we don't claim to use it.

## 6. Responsible-guidance constraints

The recommendation engine never:
- Guarantees investment returns (all investment guidance is phrased as "may consider" /
  "educational guidance", never a promise)
- Recommends specific securities, funds, or insurance products/providers
- Encourages new borrowing when DTI is already elevated
- Fabricates a number not present in `supporting_metrics`

Every recommendation-related page in the frontend carries the disclaimer: *"This system provides
educational and personalized financial guidance based on the information provided by the user. It
does not constitute professional financial, investment, insurance, tax, or legal advice."*
