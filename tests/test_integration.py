from fastapi.testclient import TestClient


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
    put_response = user_beta_client.put(f"/tasks/{task_id}", json={"title": "Взломано", "description": "compromised", "priority": 1})
    assert put_response.status_code == 404, "Уязвимость! Бета смог изменить чужую задачу."
    delete_response = user_beta_client.delete(f"/tasks/{task_id}")
    assert delete_response.status_code == 404, "Уязвимость! Бета смог удалить чужую задачу."
