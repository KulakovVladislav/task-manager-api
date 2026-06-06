import pytest
from fastapi import Depends
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.exceptions import AuthenticationFailedError
from app.database.db import get_db
from app.database.models import Task, User
from app.main import app
from app.services.user_service import authenticate_user
from tests.conftest import db_session


def test_e2e_user_lifecycle(any_client: TestClient):
    register_response = any_client.post("/users/register", json={
        "username": "user_a",
        "email": "usera@example.com",
        "password": "passwordA123@"
    })
    assert register_response.status_code == 201

    login_response = any_client.post("/users/login", json={
        "email": "usera@example.com",
        "password": "passwordA123@"
    })
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()


def test_data_isolation_audit(user_alpha_client: TestClient, user_beta_client: TestClient):
    create_response = user_alpha_client.post("/tasks", json={
        "title": "secret recept",
        "description": "show to nobody"
    })
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    assert user_beta_client.get(f"/tasks/{task_id}").status_code == 404
    assert user_beta_client.put(f"/tasks/{task_id}", json={"title": "Взломано", "description": "compromised",
                                                           "priority": 1}).status_code == 404
    assert user_beta_client.delete(f"/tasks/{task_id}").status_code == 404


def test_validation_task(auth_client: TestClient):
    response = auth_client.get("/tasks")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) <= 10

    for params in [{"limit": 105}, {"offset": -5}, {"sort_by": "invalid_value"}]:
        assert auth_client.get("/tasks", params=params).status_code == 422


def test_tasks_pagination(auth_client: TestClient, setup_test_tasks):
    data = auth_client.get("/tasks", params={"limit": 3}).json()
    assert len(data) == 3
    first_page_titles = [t["title"] for t in data]

    data_offset = auth_client.get("/tasks", params={"limit": 3, "offset": 3}).json()
    assert len(data_offset) == 2

    for task in data_offset:
        assert task["title"] not in first_page_titles


def test_tasks_filtering(auth_client: TestClient, setup_test_tasks):
    data = auth_client.get("/tasks?completed=true").json()
    assert len(data) == 2
    assert all(t["completed"] is True for t in data)

    data_priority = auth_client.get("/tasks?priority=5").json()
    assert len(data_priority) == 1
    assert data_priority[0]["title"] == "Task C"


def test_tasks_sorting(auth_client: TestClient, setup_test_tasks):
    priorities_asc = [t["priority"] for t in
                      auth_client.get("/tasks", params={"sort_by": "priority", "order": "asc"}).json()]
    assert priorities_asc == sorted(priorities_asc)

    priorities_desc = [t["priority"] for t in
                       auth_client.get("/tasks", params={"sort_by": "priority", "order": "desc"}).json()]
    assert priorities_desc == sorted(priorities_desc, reverse=True)





def test_soft_deleted_task_is_hidden_from_api_but_exists_in_db(auth_client: TestClient, db_session, created_task_id):
    assert auth_client.delete(f"/tasks/{created_task_id}").status_code == 200

    assert auth_client.get(f"/tasks/{created_task_id}").status_code == 404
    assert all(t["id"] != created_task_id for t in auth_client.get("/tasks").json())

    db_task = db_session.query(Task).filter(Task.id == created_task_id).first()
    assert db_task is not None
    assert db_task.is_deleted is True
    assert db_task.deleted_at is not None


def test_soft_deleted_task_cannot_be_updated(auth_client: TestClient, db_session, created_task_id):
    auth_client.delete(f"/tasks/{created_task_id}")

    response = auth_client.put(f"/tasks/{created_task_id}", json={
        "title": "Updated title", "description": "Updated description", "priority": 2
    })
    assert response.status_code == 404

    db_task = db_session.query(Task).filter(Task.id == created_task_id).first()
    assert db_task.title == "Task for soft delete"


def test_soft_deleted_task_cannot_be_deleted_twice(auth_client: TestClient, created_task_id):
    assert auth_client.delete(f"/tasks/{created_task_id}").status_code == 200
    assert auth_client.delete(f"/tasks/{created_task_id}").status_code == 404


def test_domain_exception_handler(auth_client: TestClient):
    response = auth_client.get(f"/tasks/9999999")
    assert response.status_code == 404
    assert response.json() == {"detail": "task not found"}


def test_middleware_adds_x_response_to_http(any_client: TestClient):
    response = any_client.get(f"/system/db-info")
    assert response.status_code == 200
    latency = response.headers.get("X-Response-Time")
    assert latency is not None
    assert latency.endswith("ms")
    number_part = latency[:-2]
    assert float(number_part) >= 0


def test_transaction_rolls_back_on_unexpected_exception(auth_client: TestClient, db_session):
    rollback_title = "rollback_marker_unique"

    @app.post("/test/rollback-transaction")
    def temporary_rollback_endpoint(db: Session = Depends(get_db)):
        user = db.query(User).first()
        assert user is not None
        task = Task(
            title=rollback_title,
            user_id=user.id,
            description="Should be rolled back",
            priority=1,
            is_deleted=False,
            completed=True,
            deleted_at=None
        )
        db.add(task)
        db.flush()
        raise RuntimeError("forced failure")

    client = TestClient(app, raise_server_exceptions=False)
    response = client.post("/test/rollback-transaction")
    assert response.status_code == 500
    task = db_session.query(Task).filter(Task.title == rollback_title).first()
    assert task is None


def test_authenticate_user_runs_dummy_verify_when_user_not_found(db_session, mocker):
    mock_verify = mocker.patch(
        "app.services.user_service.verify_password",
        return_value=False
    )
    with pytest.raises(AuthenticationFailedError):
        authenticate_user(
            email="non_existent_user_999@example.com",
            password="any_password",
            db=db_session
        )

    mock_verify.assert_called_once()
