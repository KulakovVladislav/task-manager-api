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
    print(response.json())
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
