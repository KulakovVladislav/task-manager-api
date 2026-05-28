from fastapi.testclient import TestClient
from app.database.models import Task
from tests.conftest import auth_client


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
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    task_data = {
        "title": "Buy something",
        "description": "Buy something for the house"
    }
    task_response = any_client.post("/tasks", json=task_data, headers=headers)
    assert task_response.status_code == 201
    response_json = task_response.json()
    assert "id" in response_json
    assert "user_id" in response_json
    assert response_json["priority"] == 1


def test_data_isolation_audit(user_alpha_client: TestClient, user_beta_client: TestClient):
    create_response = user_alpha_client.post("/tasks", json={
        "title": "secret recept",
        "description": "show to nobody"
    })
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]
    get_response = user_beta_client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 404, "Уязвимость! Бета смог увидеть или узнать о существовании чужой задачи."
    put_response = user_beta_client.put(f"/tasks/{task_id}",
                                        json={"title": "Взломано", "description": "compromised", "priority": 1})
    assert put_response.status_code == 404, "Уязвимость! Бета смог изменить чужую задачу."
    delete_response = user_beta_client.delete(f"/tasks/{task_id}")
    assert delete_response.status_code == 404, "Уязвимость! Бета смог удалить чужую задачу."


def test_validation_task(client, auth_client):
    response = auth_client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 10
    response_max_limit = auth_client.get("/tasks", params={"limit": 105})
    assert response_max_limit.status_code in [400, 422]
    response_negative_offset = auth_client.get("/tasks", params={"offset": -5})
    assert response_negative_offset.status_code in [400, 422]
    invalid_sort = auth_client.get("/tasks", params={"sort_by": "invalid_value"})
    assert invalid_sort.status_code in [400, 422]


def test_tasks_pagination(auth_client, setup_test_tasks):
    response = auth_client.get("/tasks", params={"limit": 3})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    first_page_titles = [task["title"] for task in data]

    response_offset = auth_client.get("/tasks", params={"limit": 3, "offset": 3})
    assert response_offset.status_code == 200
    data_offset = response_offset.json()
    assert len(data_offset) == 2
    second_page_titles = [task["title"] for task in data_offset]

    for title in second_page_titles:
        assert title not in first_page_titles


def test_tasks_filtering(auth_client, setup_test_tasks):
    client = setup_test_tasks

    response = client.get("/tasks?completed=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(task["completed"] is True for task in data)

    response_priority = auth_client.get("/tasks?priority=5")
    assert response_priority.status_code == 200
    data_priority = response_priority.json()
    assert len(data_priority) == 1
    assert data_priority[0]["title"] == "Task C"


def test_tasks_sorting(auth_client, setup_test_tasks):
    response_asc = auth_client.get("/tasks", params={"sort_by": "priority", "order": "asc"})
    assert response_asc.status_code == 200
    data_asc = response_asc.json()

    priorities_asc = [task["priority"] for task in data_asc]

    assert priorities_asc == sorted(priorities_asc)

    response_desc = auth_client.get("/tasks", params={"sort_by": "priority", "order": "desc"})
    assert response_desc.status_code == 200
    data_desc = response_desc.json()

    priorities_desc = [task["priority"] for task in data_desc]

    assert priorities_desc == sorted(priorities_desc, reverse=True)


def test_soft_deleted_task_is_hidden_from_api_but_exists_in_db(client, db_session):
    user_data = {
        "username": "soft_user",
        "email": "soft_user@example.com",
        "password": "StrongPassword123!",
    }

    response = client.post("/users/register", json=user_data)
    assert response.status_code in (200, 201)

    response = client.post(
        "/users/login",
        json={
            "email": user_data["email"],
            "password": user_data["password"],
        },
    )
    assert response.status_code == 200

    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        "/tasks",
        json={
            "title": "Task for soft delete",
            "description": "Should be hidden after delete",
            "priority": 1,
        },
        headers=headers,
    )
    assert response.status_code in (200, 201)

    task_id = response.json()["id"]

    response = client.delete(f"/tasks/{task_id}", headers=headers)
    assert response.status_code in (200, 204)

    response = client.get(f"/tasks/{task_id}", headers=headers)
    assert response.status_code == 404

    response = client.get("/tasks", headers=headers)
    assert response.status_code == 200
    assert all(task["id"] != task_id for task in response.json())

    db_task = db_session.query(Task).filter(Task.id == task_id).first()

    assert db_task is not None
    assert db_task.is_deleted is True
    assert db_task.deleted_at is not None


def test_soft_deleted_task_cannot_be_updated(client, db_session):
    user_data = {
        "username": "soft_update_user",
        "email": "soft_update_user@example.com",
        "password": "StrongPassword123!",
    }

    response = client.post("/users/register", json=user_data)
    assert response.status_code == 201

    response = client.post(
        "/users/login",
        json={
            "email": user_data["email"],
            "password": user_data["password"],
        },
    )
    assert response.status_code == 200

    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        "/tasks",
        json={
            "title": "Task to update after delete",
            "description": "Original description",
            "priority": 1,
        },
        headers=headers,
    )
    assert response.status_code == 201

    task_id = response.json()["id"]

    response = client.delete(f"/tasks/{task_id}", headers=headers)
    assert response.status_code in (200, 204)

    response = client.put(
        f"/tasks/{task_id}",
        json={
            "title": "Updated title",
            "description": "Updated description",
            "priority": 2,
        },
        headers=headers,
    )
    assert response.status_code == 404

    db_task = db_session.query(Task).filter(Task.id == task_id).first()

    assert db_task is not None
    assert db_task.is_deleted is True
    assert db_task.title == "Task to update after delete"


def test_soft_deleted_task_cannot_be_deleted_twice(client, db_session):
    user_data = {
        "username": "soft_double_delete_user",
        "email": "soft_double_delete_user@example.com",
        "password": "StrongPassword123!",
    }

    response = client.post("/users/register", json=user_data)
    assert response.status_code == 201

    response = client.post(
        "/users/login",
        json={
            "email": user_data["email"],
            "password": user_data["password"],
        },
    )
    assert response.status_code == 200

    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        "/tasks",
        json={
            "title": "Task to delete twice",
            "description": "Double delete check",
            "priority": 1,
        },
        headers=headers,
    )
    assert response.status_code == 201

    task_id = response.json()["id"]

    response = client.delete(f"/tasks/{task_id}", headers=headers)
    assert response.status_code in (200, 204)

    response = client.delete(f"/tasks/{task_id}", headers=headers)
    assert response.status_code == 404

    db_task = db_session.query(Task).filter(Task.id == task_id).first()

    assert db_task is not None
    assert db_task.is_deleted is True
    assert db_task.deleted_at is not None


def test_delete_all_tasks_soft_deletes_active_tasks(client, db_session):
    user_data = {
        "username": "soft_delete_all_user",
        "email": "soft_delete_all_user@example.com",
        "password": "StrongPassword123!",
    }

    response = client.post("/users/register", json=user_data)
    assert response.status_code == 201

    response = client.post(
        "/users/login",
        json={
            "email": user_data["email"],
            "password": user_data["password"],
        },
    )
    assert response.status_code == 200

    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    task_ids = []

    for index in range(3):
        response = client.post(
            "/tasks",
            json={
                "title": f"Task {index}",
                "description": f"Description {index}",
                "priority": 1,
            },
            headers=headers,
        )
        assert response.status_code == 201
        task_ids.append(response.json()["id"])

    response = client.delete("/tasks", headers=headers)
    assert response.status_code in (200, 204)

    response = client.get("/tasks", headers=headers)
    assert response.status_code == 200
    assert response.json() == []

    db_tasks = db_session.query(Task).filter(Task.id.in_(task_ids)).all()

    assert len(db_tasks) == 3

    for db_task in db_tasks:
        assert db_task.is_deleted is True
        assert db_task.deleted_at is not None


def test_delete_all_tasks_returns_success_when_no_active_tasks(client):
    user_data = {
        "username": "empty_bulk_delete_user",
        "email": "empty_bulk_delete_user@example.com",
        "password": "StrongPassword123!",
    }

    response = client.post("/users/register", json=user_data)
    assert response.status_code == 201

    response = client.post(
        "/users/login",
        json={
            "email": user_data["email"],
            "password": user_data["password"],
        },
    )
    assert response.status_code == 200

    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.delete("/tasks", headers=headers)

    assert response.status_code == 200
    assert response.json() == {"deleted_count": 0}
