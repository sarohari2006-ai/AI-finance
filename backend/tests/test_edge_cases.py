"""Edge cases explicitly called out in the project spec."""


def test_new_user_with_no_transactions_gets_dashboard(client, auth_headers):
    headers = auth_headers(email="newuser@example.com")
    resp = client.get("/api/dashboard", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["monthly_income"] == 0
    assert data["goals"] == []
    assert isinstance(data["top_recommendations"], list)


def test_user_with_no_goals_has_full_goal_score(client, auth_headers):
    headers = auth_headers(email="nogoals@example.com")
    resp = client.get("/api/financial-health", headers=headers)
    assert resp.status_code == 200
    # avg_goal_progress_pct defaults to 100 when there are no goals (nothing to fall behind on)
    assert resp.json()["components"]["goals"] == 100.0


def test_user_with_no_investments(client, auth_headers):
    headers = auth_headers(email="noinvest@example.com")
    resp = client.get("/api/investments", headers=headers)
    assert resp.status_code == 200
    assert resp.json() == []


def test_user_with_multiple_loans_sums_emi_correctly(client, auth_headers):
    headers = auth_headers(email="multiloan@example.com")
    client.put("/api/profile", json={"monthly_income": 100000}, headers=headers)
    client.post("/api/loans", json={
        "loan_type": "home_loan", "principal_amount": 500000, "outstanding_amount": 400000,
        "interest_rate": 8, "emi": 10000,
    }, headers=headers)
    client.post("/api/loans", json={
        "loan_type": "car_loan", "principal_amount": 200000, "outstanding_amount": 150000,
        "interest_rate": 9, "emi": 5000,
    }, headers=headers)
    health = client.get("/api/financial-health", headers=headers).json()
    # DTI = 15000/100000 = 15%
    assert "15.0" in health["explanation"]["debt"]


def test_zero_income_does_not_crash_savings_rate(client, auth_headers):
    headers = auth_headers(email="zeroincome@example.com")
    client.put("/api/profile", json={"monthly_income": 0, "monthly_expenses": 5000}, headers=headers)
    resp = client.get("/api/dashboard", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["savings_rate"] == 0.0


def test_negative_transaction_amount_rejected(client, auth_headers):
    headers = auth_headers(email="negamount@example.com")
    resp = client.post("/api/transactions", json={
        "date": "2026-01-01", "category": "food", "amount": -50, "type": "expense",
    }, headers=headers)
    assert resp.status_code == 422


def test_missing_required_registration_fields_rejected(client):
    resp = client.post("/api/auth/register", json={"name": "Incomplete"})
    assert resp.status_code == 422


def test_invalid_transaction_type_rejected(client, auth_headers):
    headers = auth_headers(email="badtype@example.com")
    resp = client.post("/api/transactions", json={
        "date": "2026-01-01", "category": "food", "amount": 100, "type": "not_a_real_type",
    }, headers=headers)
    assert resp.status_code == 400


def test_literacy_submit_with_no_answers_rejected(client, auth_headers):
    headers = auth_headers(email="noanswers@example.com")
    resp = client.post("/api/literacy/submit", json={"answers": {}}, headers=headers)
    assert resp.status_code == 400


def test_goal_with_current_amount_exceeding_target_marks_achieved(client, auth_headers):
    headers = auth_headers(email="overachiever@example.com")
    create_resp = client.post("/api/goals", json={
        "name": "Small Goal", "goal_type": "custom", "target_amount": 1000, "current_amount": 500,
        "target_date": "2027-01-01", "priority": "low",
    }, headers=headers)
    goal_id = create_resp.json()["id"]
    update_resp = client.put(f"/api/goals/{goal_id}", json={"current_amount": 1200}, headers=headers)
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "achieved"
