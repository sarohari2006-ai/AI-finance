"""
Hybrid Recommendation Engine.

Architecture (documented in docs/ai-recommendation.md):
  - Deterministic financial calculations (savings rate, DTI, emergency-fund
    gap, goal contribution requirements) feed rule conditions.
  - The behavioral archetype comes from the K-Means clustering step in
    app.analytics.behavior.
  - Risk profile and literacy level (from user-submitted assessments) gate
    which investment/insurance rules apply and how detailed the wording is.
  - A rule engine (this file) evaluates a fixed set of condition -> template
    rules across four categories: savings, investment, insurance, credit.
    Each firing rule is scored for priority and returned with the exact
    user metrics that triggered it (the "explanation").

There is no black-box model deciding *whether* to recommend something —
every recommendation here is traceable to a specific rule and the user's
own numbers. This is intentionally NOT dressed up as a deep-learning
system; the spec explicitly calls for transparency over false sophistication.
"""
from typing import Dict, Any, List


def _metric(**kwargs) -> Dict[str, Any]:
    return kwargs


def generate_recommendations(context: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    context keys expected:
      monthly_income, monthly_expenses, savings_rate_pct, emergency_fund,
      emergency_fund_months, discretionary_ratio, discretionary_amount,
      total_emi, debt_to_income_pct, loans (list), investments (list),
      investment_total, risk_level, literacy_level, goals (list of dict),
      behavior_label, has_health_insurance, has_life_insurance,
      financial_health_score
    """
    recs: List[Dict[str, Any]] = []
    literacy = context.get("literacy_level") or "basic"
    simple_wording = literacy in ("beginner", "basic")

    # ---------------- SAVINGS ----------------
    savings_rate = context["savings_rate_pct"]
    if savings_rate < 10:
        recs.append({
            "title": "Increase Your Monthly Savings",
            "category": "savings",
            "priority": "high" if savings_rate < 0 else "medium",
            "recommendation": (
                "Try to save at least 10-20% of your monthly income."
                if simple_wording else
                "Target a savings rate of 10-20% of net income by reallocating discretionary spend."
            ),
            "reason": (
                f"Your current savings rate is {savings_rate:.1f}%, which is below the commonly "
                f"recommended 10-20% range."
            ),
            "supporting_metrics": _metric(
                monthly_income=context["monthly_income"],
                monthly_expenses=context["monthly_expenses"],
                savings_rate_pct=savings_rate,
            ),
            "expected_benefit": "Builds a financial cushion and accelerates progress toward your goals.",
            "action": f"Aim to set aside ₹{max(context['monthly_income'] * 0.1, 0):,.0f} per month automatically.",
        })

    if context["emergency_fund_months"] < 6:
        target_fund = context["monthly_expenses"] * 6
        gap = max(target_fund - context["emergency_fund"], 0)
        monthly_alloc = round(gap / 12, 2) if gap > 0 else 0
        recs.append({
            "title": "Build Your Emergency Fund",
            "category": "savings",
            "priority": "high" if context["emergency_fund_months"] < 3 else "medium",
            "recommendation": "Increase your monthly emergency-fund contribution.",
            "reason": (
                f"Your emergency savings currently cover {context['emergency_fund_months']:.1f} months of "
                f"expenses, below the recommended 6-month target."
            ),
            "supporting_metrics": _metric(
                monthly_expenses=context["monthly_expenses"],
                emergency_fund=context["emergency_fund"],
                target_fund=round(target_fund, 2),
            ),
            "expected_benefit": "Protects you from debt during income disruptions or emergencies.",
            "action": f"Allocate approximately ₹{monthly_alloc:,.0f}/month toward the emergency fund for the next year.",
        })

    if context["discretionary_ratio"] > 0.4:
        recs.append({
            "title": "Reduce Discretionary Spending",
            "category": "savings",
            "priority": "medium",
            "recommendation": "Review and reduce non-essential spending categories.",
            "reason": (
                f"Discretionary spending is {context['discretionary_ratio'] * 100:.0f}% of your monthly "
                f"expenses, which is high relative to essential spending."
            ),
            "supporting_metrics": _metric(
                discretionary_ratio=context["discretionary_ratio"],
                discretionary_amount=context["discretionary_amount"],
            ),
            "expected_benefit": "Frees up cash flow for savings and goal contributions.",
            "action": "Set a monthly budget cap for shopping, entertainment, and subscription categories.",
        })

    # ---------------- CREDIT / DEBT ----------------
    dti = context["debt_to_income_pct"]
    if dti > 0:
        high_interest_loans = [l for l in context["loans"] if l.get("interest_rate", 0) >= 12]
        if dti > 40:
            recs.append({
                "title": "High EMI Burden Detected",
                "category": "credit",
                "priority": "high",
                "recommendation": "Prioritize reducing your debt load before taking on new obligations.",
                "reason": f"Your EMI payments represent {dti:.1f}% of your monthly income, above the safe threshold of 40%.",
                "supporting_metrics": _metric(total_emi=context["total_emi"], monthly_income=context["monthly_income"], debt_to_income_pct=dti),
                "expected_benefit": "Reduces financial stress and improves loan eligibility in the future.",
                "action": "Avoid new loans and consider consolidating or renegotiating high-interest debt.",
            })
        elif dti > 20:
            recs.append({
                "title": "Monitor Your Debt Load",
                "category": "credit",
                "priority": "medium",
                "recommendation": "Keep EMI payments in check relative to income.",
                "reason": f"Your EMI payments represent {dti:.1f}% of your monthly income.",
                "supporting_metrics": _metric(total_emi=context["total_emi"], debt_to_income_pct=dti),
                "expected_benefit": "Maintains healthy borrowing capacity and reduces repayment risk.",
                "action": "Avoid increasing EMI obligations until your debt-to-income ratio falls below 20%.",
            })

        if high_interest_loans:
            names = ", ".join(l.get("loan_type", "loan") for l in high_interest_loans)
            recs.append({
                "title": "Prioritize High-Interest Debt",
                "category": "credit",
                "priority": "high",
                "recommendation": f"Focus extra repayments on your high-interest loan(s): {names}.",
                "reason": "Paying down high-interest debt first reduces total interest paid over time.",
                "supporting_metrics": _metric(high_interest_loans=high_interest_loans),
                "expected_benefit": "Minimizes total interest cost and shortens repayment timelines.",
                "action": "Direct any surplus cash flow toward the loan with the highest interest rate first.",
            })

    # ---------------- INVESTMENTS ----------------
    risk_level = context.get("risk_level") or "moderate"
    if context["emergency_fund_months"] < 3:
        recs.append({
            "title": "Build Safety Net Before Investing Further",
            "category": "investment",
            "priority": "medium",
            "recommendation": "Prioritize your emergency fund before increasing investment contributions.",
            "reason": "Investing while lacking a basic emergency fund increases the risk of having to sell investments at a loss during a crisis.",
            "supporting_metrics": _metric(emergency_fund_months=context["emergency_fund_months"]),
            "expected_benefit": "Reduces the chance of forced, poorly-timed withdrawals.",
            "action": "Split any surplus between emergency savings and investments until you reach 3+ months of coverage.",
        })
    else:
        if risk_level == "low":
            text = (
                "Consider low-volatility options such as fixed deposits, PPF, or debt mutual funds for your goals."
                if simple_wording else
                "Your risk profile suggests weighting a larger share of contributions toward fixed-income instruments (FDs, PPF, debt funds) with a smaller equity allocation for long-horizon goals."
            )
        elif risk_level == "high":
            text = (
                "You may consider a higher allocation toward equity or equity mutual funds for long-term goals, alongside your existing safety net."
                if simple_wording else
                "Your risk tolerance and time horizon may support a higher equity allocation (diversified equity/index funds) for long-term goals, while maintaining fixed-income exposure for near-term goals."
            )
        else:
            text = (
                "A balanced mix of equity and debt instruments may suit your moderate risk profile."
                if simple_wording else
                "A diversified allocation across equity and debt instruments, rebalanced periodically, aligns with a moderate risk profile."
            )
        recs.append({
            "title": "Investment Allocation Guidance",
            "category": "investment",
            "priority": "low",
            "recommendation": text,
            "reason": f"This guidance is based on your {risk_level} risk profile and current emergency-fund coverage.",
            "supporting_metrics": _metric(risk_level=risk_level, investment_total=context["investment_total"]),
            "expected_benefit": "Aligns your investment mix with your comfort level for market fluctuations.",
            "action": "Review your asset allocation against your risk profile and goal horizons; this is educational guidance, not a guaranteed strategy.",
        })

    if context["monthly_income"] > 0:
        contribution_rate = context.get("investment_contribution", 0) / context["monthly_income"]
        if contribution_rate < 0.1 and context["emergency_fund_months"] >= 3:
            recs.append({
                "title": "Increase Investment Contributions",
                "category": "investment",
                "priority": "medium",
                "recommendation": "Consider increasing your regular investment contributions.",
                "reason": f"You currently invest about {contribution_rate * 100:.1f}% of your income, below a common 10-15% guideline.",
                "supporting_metrics": _metric(contribution_rate=round(contribution_rate * 100, 1)),
                "expected_benefit": "Supports long-term goal achievement through consistent contributions.",
                "action": "Set up an automatic monthly transfer toward your investment account.",
            })

    # ---------------- INSURANCE ----------------
    if not context.get("has_health_insurance"):
        recs.append({
            "title": "Consider Health Insurance Coverage",
            "category": "insurance",
            "priority": "high",
            "recommendation": "You do not currently have a health insurance policy on file.",
            "reason": "Health insurance protects your savings and emergency fund from being depleted by unexpected medical expenses.",
            "supporting_metrics": _metric(has_health_insurance=False),
            "expected_benefit": "Reduces financial risk from medical emergencies.",
            "action": "Research health insurance plans appropriate for your family size and needs. This is educational guidance, not professional insurance advice.",
        })
    if not context.get("has_life_insurance") and context.get("has_dependents_hint", True):
        recs.append({
            "title": "Consider Life Insurance Coverage",
            "category": "insurance",
            "priority": "medium",
            "recommendation": "You do not currently have a life insurance policy on file.",
            "reason": "Life insurance can protect dependents from financial hardship in case of unforeseen events.",
            "supporting_metrics": _metric(has_life_insurance=False),
            "expected_benefit": "Provides financial protection for dependents.",
            "action": "Evaluate term life insurance options appropriate for your income and dependents. This is educational guidance, not professional insurance advice.",
        })

    # ---------------- GOALS ----------------
    for goal in context.get("goals", []):
        if goal["progress_percentage"] < 50 and goal.get("status") != "achieved":
            recs.append({
                "title": f"Stay on Track: {goal['name']}",
                "category": "goal",
                "priority": "medium" if goal.get("priority") == "high" else "low",
                "recommendation": f"To reach your '{goal['name']}' goal by {goal['target_date']}, increase your contributions.",
                "reason": f"You are {goal['progress_percentage']:.0f}% toward this goal with {goal['remaining_amount']:,.0f} remaining.",
                "supporting_metrics": _metric(**goal),
                "expected_benefit": "Keeps you on pace to reach your target date.",
                "action": f"Contribute approximately ₹{goal['recommended_monthly_contribution']:,.0f}/month toward this goal.",
            })

    # Assign explanation_type: all rule-based here (behavior label is ML-derived input but rule selection is deterministic)
    for r in recs:
        r["explanation_type"] = "hybrid" if context.get("behavior_label") else "rule_based"

    # Sort by priority
    priority_rank = {"high": 0, "medium": 1, "low": 2}
    recs.sort(key=lambda r: priority_rank.get(r["priority"], 3))

    return recs
