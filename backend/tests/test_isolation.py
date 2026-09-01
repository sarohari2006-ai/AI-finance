def test_users_cannot_access_each_others_transactions(client, auth_headers):
    headers_a = auth_headers(email="usera@example.com")
    headers_b = auth_headers(email="userb@example.com")

    resp = client.post("/api/transactions", json={
        "date": "2026-01-01", "category": "food", "amount": 500, "type": "expense",
    }, headers=headers_a)
    assert resp.status_code == 201
    txn_id = resp.json()["id"]

    # User B should not see it in their list
    listing = client.get("/api/transactions", headers=headers_b).json()
    assert all(t["id"] != txn_id for t in listing)

    # User B should not be able to delete it (404, not leaking existence via 403)
    delete_resp = client.delete(f"/api/transactions/{txn_id}", headers=headers_b)
    assert delete_resp.status_code == 404

    # User A can still delete their own
    own_delete = client.delete(f"/api/transactions/{txn_id}", headers=headers_a)
    assert own_delete.status_code == 204


def test_users_get_independent_financial_profiles(client, auth_headers):
    headers_a = auth_headers(email="profa@example.com")
    headers_b = auth_headers(email="profb@example.com")

    client.put("/api/profile", json={"monthly_income": 50000, "monthly_expenses": 20000}, headers=headers_a)
    client.put("/api/profile", json={"monthly_income": 100000, "monthly_expenses": 40000}, headers=headers_b)

    profile_a = client.get("/api/profile", headers=headers_a).json()
    profile_b = client.get("/api/profile", headers=headers_b).json()

    assert profile_a["monthly_income"] == 50000
    assert profile_b["monthly_income"] == 100000


def test_different_users_get_different_recommendations(client, auth_headers):
    headers_a = auth_headers(email="reca@example.com")
    headers_b = auth_headers(email="recb@example.com")

    client.put("/api/profile", json={
        "monthly_income": 20000, "monthly_expenses": 19000, "current_savings": 1000, "emergency_fund": 500,
    }, headers=headers_a)
    client.put("/api/profile", json={
        "monthly_income": 200000, "monthly_expenses": 60000, "current_savings": 500000, "emergency_fund": 400000,
    }, headers=headers_b)

    recs_a = client.get("/api/recommendations", headers=headers_a).json()
    recs_b = client.get("/api/recommendations", headers=headers_b).json()

    titles_a = {r["title"] for r in recs_a}
    titles_b = {r["title"] for r in recs_b}
    assert titles_a != titles_b
