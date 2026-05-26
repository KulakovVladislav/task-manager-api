import uuid

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


@pytest.fixture(scope="function", autouse=True)
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def override_dependencies(db_session):
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_client(client):
    unique_id = uuid.uuid4().hex[:6]
    test_user = {
        "username": f"user_{unique_id}",
        "email": f"auth_{unique_id}@example.com",
        "password": "Strong_password_123@"
    }

    reg_resp = client.post("/users/register", json=test_user)
    assert reg_resp.status_code in [200, 201]

    login_response = client.post(
        "/users/login",
        json={
            "email": test_user["email"],
            "password": test_user["password"]
        }
    )

    response_data = login_response.json()
    token = response_data.get("access_token")

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


@pytest.fixture
def setup_test_tasks(auth_client):
    tasks_to_create = [
        {"title": "Task A", "description": "Desc A", "priority": 3, "completed": False},
        {"title": "Task B", "description": "Desc B", "priority": 1, "completed": True},
        {"title": "Task C", "description": "Desc C", "priority": 5, "completed": False},
        {"title": "Task D", "description": "Desc D", "priority": 2, "completed": True},
        {"title": "Task E", "description": "Desc E", "priority": 4, "completed": False},
    ]
    for task in tasks_to_create:

        response = auth_client.post("/tasks", json=task)
        assert response.status_code in [200, 201]

        if task["completed"]:
            task_id = response.json()["id"]
            auth_client.patch(f"/tasks/{task_id}", json={"completed": True})  # или /tasks/{task_id}/полный_апдейт

    return auth_client
