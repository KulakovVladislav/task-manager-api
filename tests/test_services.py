from unittest.mock import patch

from app.core.cache import cache_key
from app.database.models import User
from app.schemas import SortByFields, OrderOptions, TaskCreate
from app.services.task_service import create_task as create_task_service
from app.services.user_service import get_user_by_username


def test_get_user_by_username_returns_user(mocker):
    mock_session = mocker.MagicMock()
    fake_user = "FAKE_USER_OBJ"
    mock_session.query.return_value.filter.return_value.first.return_value = fake_user

    result = get_user_by_username("some_username", mock_session)

    assert result == fake_user


def test_get_user_by_username_returns_none_when_not_found(mocker):
    mock_session = mocker.MagicMock()
    mock_session.query.return_value.filter.return_value.first.return_value = None

    result = get_user_by_username("not_exists", mock_session)

    assert result is None


def test_get_tasks_uses_cache_on_second_request(auth_client, db_session, redis_client):
    me_response = auth_client.get("/users/me")
    if me_response.status_code == 200:
        user_id = me_response.json()["id"]
    else:
        user_id = 1

    from app.database.models import User
    db_user = db_session.query(User).filter(User.id == user_id).first()

    item = TaskCreate(title="Test Task", description="Test Description", priority=1)
    create_task_service(item, db_session, db_user)
    response_1 = auth_client.get("/tasks")
    assert response_1.status_code == 200

    expected_key = cache_key(
        user_id=user_id,
        completed=None,
        priority=None,
        limit=10,
        offset=0,
        sort_by=SortByFields.id.value,
        order=OrderOptions.asc.value
    )
    assert redis_client.exists(expected_key) == 1

    with patch("app.api.tasks.get_tasks_service") as mock_service:
        response_2 = auth_client.get("/tasks")
        assert response_2.status_code == 200
        assert response_2.json() == response_1.json()
        mock_service.assert_not_called()


def test_create_task_invalidates_tasks_cache(auth_client, db_session, redis_client):
    user_id = 1
    me_response = auth_client.get("/users/me")
    if me_response.status_code == 200:
        user_id = me_response.json()["id"]

    db_user = db_session.query(User).filter(User.id == user_id).first()

    item_1 = TaskCreate(title="First Task", description="First Desc", priority=1)
    create_task_service(item_1, db_session, db_user)

    response_get_1 = auth_client.get("/tasks")
    assert response_get_1.status_code == 200

    expected_key = cache_key(
        user_id=user_id,
        completed=None,
        priority=None,
        limit=10,
        offset=0,
        sort_by=SortByFields.id.value,
        order=OrderOptions.asc.value
    )
    assert redis_client.exists(expected_key) == 1

    item_2 = {"title": "Second Task", "description": "Second Desc", "priority": 2}
    response_post = auth_client.post("/tasks", json=item_2)
    assert response_post.status_code == 201

    assert redis_client.exists(expected_key) == 0
