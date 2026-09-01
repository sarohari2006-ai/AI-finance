from app.services.financial_health import compute_financial_health, score_savings, score_debt, category_label


def test_score_savings_at_target_is_100():
    assert score_savings(20) == 100.0


def test_score_savings_negative_is_zero():
    assert score_savings(-10) == 0.0


def test_score_debt_zero_dti_is_100():
    assert score_debt(0) == 100.0


def test_score_debt_high_dti_is_zero():
    assert score_debt(50) == 0.0


def test_category_labels():
    assert category_label(85) == "Strong"
    assert category_label(65) == "Good"
    assert category_label(45) == "Fair"
    assert category_label(20) == "Needs Attention"


def test_compute_financial_health_new_user_with_no_data():
    """A brand new user with zero income/expenses/goals shouldn't crash the scorer."""
    result = compute_financial_health(
        savings_rate_pct=0, debt_to_income_pct=0, emergency_fund_months=0,
        avg_goal_progress_pct=100.0, discretionary_ratio=0.0, investment_consistency=0.0,
        has_health_insurance=False, has_life_insurance=False,
    )
    assert 0 <= result["score"] <= 100
    assert result["category"] in ("Needs Attention", "Fair", "Good", "Strong")
    assert set(result["components"].keys()) == {
        "savings", "debt", "emergency_fund", "goals", "spending", "investment", "insurance"
    }


def test_compute_financial_health_ideal_user_scores_high():
    result = compute_financial_health(
        savings_rate_pct=25, debt_to_income_pct=0, emergency_fund_months=6,
        avg_goal_progress_pct=100.0, discretionary_ratio=0.2, investment_consistency=1.0,
        has_health_insurance=True, has_life_insurance=True,
    )
    assert result["score"] >= 95
    assert result["category"] == "Strong"
