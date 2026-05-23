import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.database.base import Base
from app.database.db import get_db
from app.main import app

engine = create_engine(settings.test_database_url)
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def prepare_test_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_client(client):
    test_user = {
        "username": "unique_auth_user",
        "email": "unique_auth@example.com",
        "password": "Strong_password_123@"
    }

    client.post("/users/register", json=test_user)

    login_response = client.post(
        "/users/login",
        json={
            "email": test_user["email"],
            "password": test_user["password"]
        }
    )

    response_data = login_response.json()
    token = response_data.get("access_token") or response_data.get("token") or response_data.get("jwt")

    if not token:
        raise ValueError(f"Не удалось найти токен в ответе сервера. Ответ: {response_data}")

    client.headers.update({"Authorization": f"Bearer {token}"})
    return client


@pytest.fixture(scope="session")
def any_client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def user_alpha_client(any_client):
    any_client.post("/users/register", json={
        "username": "alpha_user",
        "email": "alpha@example.com",
        "password": "Superpassword123@"
    })

    login_response = any_client.post("/users/login", json={
        "email": "alpha@example.com",
        "password": "Superpassword123@"
    })
    token = login_response.json()["access_token"]

    alpha_client = TestClient(app)
    alpha_client.headers.update({"Authorization": f"Bearer {token}"})
    return alpha_client


@pytest.fixture
def user_beta_client(any_client):
    any_client.post("/users/register", json={
        "username": "beta_user",
        "email": "beta@example.com",
        "password": "Superpassword123@"
    })

    login_response = any_client.post("/users/login", json={
        "email": "beta@example.com",
        "password": "Superpassword123@"
    })
    token = login_response.json()["access_token"]

    beta_client = TestClient(app)
    beta_client.headers.update({"Authorization": f"Bearer {token}"})
    return beta_client
