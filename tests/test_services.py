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
