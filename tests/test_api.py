from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_status_endpoint():
    response = client.get("/system")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello Backend"}


def test_create_task_invalid_priority_high(auth_client):  # Используем новую фикстуру
    response = auth_client.post(
        "/tasks",
        json={
            "title": "New Task",
            "description": "Task description",
            "priority": 6
        }
    )
    print("\nResponse JSON:", response.json())
    assert response.status_code == 422
