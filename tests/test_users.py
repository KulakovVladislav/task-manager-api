from starlette.testclient import TestClient


def test_users(client):
    response = client.post(
        "/users/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "Testpassword123@"
        }
    )
    assert response.status_code == 201
    assert response.json()["username"] == "testuser"


def test_register_duplicate_user(client):
    response = client.post(
        "/users/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "Testpassword123@"
        }
    )
    assert response.status_code == 201

    response = client.post(
        "/users/register",
        json={
            "username": "testuser",
            "email": "test2@example.com",
            "password": "Testpassword123@"
        }
    )
    assert response.status_code == 400


def test_bad_email(client):
    response = client.post(
        "/users/register",
        json={
            "username": "testuser",
            "email": "not-an-email",
            "password": "Testpassword123@"
        }
    )
    assert response.status_code == 422


def test_bad_password(client):
    response = client.post(
        "/users/register",
        json={
            "username": "testuser",
            "email": "test2@example.com",
            "password": "very_bad_password"
        }
    )
    assert response.status_code == 422


def test_login_with_valid_password_returns_access_token(client):
    register_response = client.post(
        "/users/register",
        json={
            "username": "testuser",
            "email": "test2@example.com",
            "password": "Testpassword123@"
        }
    )
    assert register_response.status_code == 201
    login_response = client.post(
        "/users/login",
        json={
            "email": "test2@example.com",
            "password": "Testpassword123@"
        }
    )
    assert login_response.status_code == 200
    data = login_response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_with_invalid_password_returns_401(client):
    register_response = client.post(
        "/users/register",
        json={
            "username": "testuser",
            "email": "test2@example.com",
            "password": "Testpassword123@"
        }
    )
    assert register_response.status_code == 201
    login_response = client.post(
        "/users/login",
        json={
            "email": "test2@example.com",
            "password": "Testpassword123"
        }
    )
    assert login_response.status_code == 401
    data = login_response.json()
    assert data["detail"] == "Incorrect email or password"


def test_logout_revokes_token(client: TestClient):
    user_data = {
        "email": "logout_test@example.com",
        "password": "Strong_password_123@",
        "username": "logout_test_user"
    }

    register_res = client.post("/users/register", json=user_data)
    assert register_res.status_code in [200, 201]

    login_payload = {
        "email": user_data["email"],
        "password": user_data["password"]
    }

    login_res = client.post("/users/login", json=login_payload)
    assert login_res.status_code == 200

    token_data = login_res.json()
    access_token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    me_before = client.get("/users/me", headers=headers)
    assert me_before.status_code == 200

    logout_res = client.post("/users/logout", headers=headers)
    assert logout_res.status_code == 200

    me_after = client.get("/users/me", headers=headers)
    assert me_after.status_code == 401


def test_logout_with_wrong_token(client:TestClient):
    headers = {"Authorization": f"Bearer absolutely_fake_and_invalid_token"}
    response = client.post("/users/logout", headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "invalid token"