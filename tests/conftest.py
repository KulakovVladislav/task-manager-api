import uuid

import fakeredis
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.core.redis import get_redis_client
from app.database.base import Base
from app.database.db import get_db
from app.main import app

engine = create_engine(settings.test_database_url)
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@pytest.fixture(autouse=True, scope="session")
def fast_bcrypt():
    from unittest.mock import patch
    from passlib.context import CryptContext
    fast_ctx = CryptContext(schemes=["bcrypt"], bcrypt__rounds=4)
    with patch("app.security.pwd_context", fast_ctx):
        yield


@pytest.fixture(scope="function", autouse=True)
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def redis_client():
    fake_client = fakeredis.FakeRedis(decode_responses=True)
    fake_client.flushdb()
    yield fake_client
    fake_client.flushdb()


@pytest.fixture(autouse=True)
def mock_dependencies(db_session, redis_client):
    def _override_get_db():
        try:
            yield db_session
            db_session.commit()
        except Exception:
            db_session.rollback()
            raise

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_redis_client] = lambda: redis_client

    yield redis_client

    app.dependency_overrides.pop(get_db, None)
    app.dependency_overrides.pop(get_redis_client, None)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_client(client):
    unique_id = uuid.uuid4().hex[:6]
    test_user = {
        "username": f"user_{unique_id}",
        "email": f"auth_{unique_id}@example.com",
        "password": "Str0ng@Pwd!"
    }

    reg_resp = client.post("/users/register", json=test_user)
    assert reg_resp.status_code == 201

    login_response = client.post(
        "/users/login",
        json={
            "email": test_user["email"],
            "password": test_user["password"]
        }
    )

    token = login_response.json().get("access_token")
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client


@pytest.fixture
def user_alpha_client(client):
    client.post("/users/register", json={
        "username": "alpha_user",
        "email": "alpha@example.com",
        "password": "SuperPwd@123"
    })
    login_response = client.post("/users/login", json={
        "email": "alpha@example.com",
        "password": "SuperPwd@123"
    })
    token = login_response.json()["access_token"]

    alpha_client = TestClient(app)
    alpha_client.headers.update({"Authorization": f"Bearer {token}"})
    return alpha_client


@pytest.fixture
def user_beta_client(client):
    client.post("/users/register", json={
        "username": "beta_user",
        "email": "beta@example.com",
        "password": "SuperPwd@123"
    })
    login_response = client.post("/users/login", json={
        "email": "beta@example.com",
        "password": "SuperPwd@123"
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
        assert response.status_code == 201

        if task["completed"]:
            task_id = response.json()["id"]
            put_res = auth_client.put(f"/tasks/{task_id}/complete")
            assert put_res.status_code == 200
    return auth_client


@pytest.fixture
def created_task_id(auth_client) -> int:
    response = auth_client.post("/tasks", json={
        "title": "Task for soft delete",
        "description": "Original description",
        "priority": 1,
    })
    return response.json()["id"]
