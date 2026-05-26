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
