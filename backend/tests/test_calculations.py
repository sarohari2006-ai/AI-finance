from datetime import date

from app.services import calculations as calc
from app.models.models import Transaction, TransactionType, FinancialGoal, GoalPriority, GoalStatus, Loan


def _txn(amount, type_, category="food", d=None):
    return Transaction(date=d or date.today(), category=category, amount=amount, type=type_)


def test_savings_rate_normal():
    assert calc.savings_rate(10000, 8000) == 20.0


def test_savings_rate_zero_income():
    assert calc.savings_rate(0, 5000) == 0.0


def test_savings_rate_negative_when_overspending():
    assert calc.savings_rate(10000, 15000) == -50.0


def test_savings_rate_capped_at_negative_100():
    # Even if expenses are 10x income, ratio shouldn't go below -100%
    assert calc.savings_rate(1000, 50000) == -100.0


def test_total_income_and_expenses():
    txns = [
        _txn(1000, TransactionType.income),
        _txn(500, TransactionType.expense),
        _txn(300, TransactionType.expense),
    ]
    assert calc.total_income(txns) == 1000
    assert calc.total_expenses(txns) == 800


def test_total_income_expenses_empty_list():
    assert calc.total_income([]) == 0
    assert calc.total_expenses([]) == 0


def test_emergency_fund_months_zero_expenses():
    assert calc.emergency_fund_months(5000, 0) == 0.0


def test_emergency_fund_months_normal():
    assert calc.emergency_fund_months(30000, 10000) == 3.0


def test_debt_to_income_ratio_zero_income():
    assert calc.debt_to_income_ratio(5000, 0) == 0.0


def test_debt_to_income_ratio_normal():
    assert calc.debt_to_income_ratio(10000, 50000) == 20.0


def test_goal_progress_partial():
    goal = FinancialGoal(
        name="Test Goal", target_amount=100000, current_amount=25000,
        target_date=date(date.today().year + 1, date.today().month, 1),
        priority=GoalPriority.medium, status=GoalStatus.in_progress,
    )
    result = calc.goal_progress(goal)
    assert result["progress_percentage"] == 25.0
    assert result["remaining_amount"] == 75000


def test_goal_progress_already_achieved_caps_at_100():
    goal = FinancialGoal(
        name="Done Goal", target_amount=1000, current_amount=1500,
        target_date=date(date.today().year + 1, date.today().month, 1),
        priority=GoalPriority.low, status=GoalStatus.in_progress,
    )
    result = calc.goal_progress(goal)
    assert result["progress_percentage"] == 100.0
    assert result["remaining_amount"] == 0.0


def test_essential_vs_discretionary_no_transactions():
    result = calc.essential_vs_discretionary([])
    assert result["essential_ratio"] == 0.0
    assert result["discretionary_ratio"] == 0.0


def test_total_monthly_emi_multiple_loans():
    loans = [
        Loan(loan_type="home_loan", principal_amount=100000, outstanding_amount=80000, interest_rate=8, emi=2000),
        Loan(loan_type="car_loan", principal_amount=50000, outstanding_amount=30000, interest_rate=9, emi=1500),
    ]
    assert calc.total_monthly_emi(loans) == 3500
