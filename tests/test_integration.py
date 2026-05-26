from fastapi.testclient import TestClient

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
