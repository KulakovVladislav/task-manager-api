import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.mark.parametrize("payload, expected_field", [
    ({"title": "Test", "priority": 0}, "priority"),
    ({"title": "Test", "priority": 6}, "priority"),
    ({"title": "", "priority": 3}, "title"),
    ({"title": "A" * 201, "priority": 3}, "title"),
])
def test_create_task_validation_boundaries(auth_client, payload, expected_field):
    data = {"title": "Valid Title", "description": "Valid Desc", "priority": 3}
    data.update(payload)
    response = auth_client.post("/tasks", json=data)
    assert response.status_code == 422
    errors = response.json().get("detail", [])
    assert any(err.get("loc")[-1] == expected_field for err in errors)
