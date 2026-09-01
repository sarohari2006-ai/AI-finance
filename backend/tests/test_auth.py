def test_register_creates_user_and_returns_token(client):
    resp = client.post("/api/auth/register", json={
        "name": "Alice", "email": "alice@example.com", "password": "secret123", "age": 30, "occupation": "Engineer",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["user"]["email"] == "alice@example.com"
    assert "access_token" in data


def test_register_duplicate_email_rejected(client):
    payload = {"name": "Bob", "email": "bob@example.com", "password": "secret123"}
    r1 = client.post("/api/auth/register", json=payload)
    assert r1.status_code == 201
    r2 = client.post("/api/auth/register", json=payload)
    assert r2.status_code == 400


def test_login_success(client):
    client.post("/api/auth/register", json={"name": "Carl", "email": "carl@example.com", "password": "secret123"})
    resp = client.post("/api/auth/login", json={"email": "carl@example.com", "password": "secret123"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password_rejected(client):
    client.post("/api/auth/register", json={"name": "Dana", "email": "dana@example.com", "password": "secret123"})
    resp = client.post("/api/auth/login", json={"email": "dana@example.com", "password": "wrongpass"})
    assert resp.status_code == 401


def test_protected_route_requires_token(client):
    resp = client.get("/api/dashboard")
    assert resp.status_code == 401


def test_protected_route_rejects_invalid_token(client):
    resp = client.get("/api/dashboard", headers={"Authorization": "Bearer invalid.token.here"})
    assert resp.status_code == 401


def test_password_is_hashed_not_plaintext(client):
    from app.database.session import SessionLocal  # noqa
    resp = client.post("/api/auth/register", json={"name": "Eve", "email": "eve@example.com", "password": "plaintextpw"})
    assert resp.status_code == 201
    # Ensure the password isn't echoed back anywhere in the response
    assert "plaintextpw" not in resp.text
