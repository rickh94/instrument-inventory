import json
from unittest import mock

import pytest

import todos


@pytest.fixture
def fake_uuid():
    def _uuid():
        return "fakeuuid"

    return _uuid


def test_create_todo_full(monkeypatch, fake_uuid):
    """Test creating a to do item"""
    todo_mock = mock.MagicMock()
    created_item = mock.MagicMock()
    todo_mock.return_value = created_item

    monkeypatch.setattr("todos.TodoModel", todo_mock)
    monkeypatch.setattr("uuid.uuid1", fake_uuid)

    response = todos.create(
        {
            "body": json.dumps(
                {"content": "test content", "relevantInstrument": "1-610"}
            ),
            "requestContext": {"identity": {"cognitoIdentityId": "USER-SUB-1234"}},
        },
        {},
    )

    todo_mock.assert_called_with(
        "USER-SUB-1234", "fakeuuid", content="test content", relevantInstrument="1-610"
    )

    created_item.save.assert_called()

    assert response["statusCode"] == 201


def test_create_todo_partial(monkeypatch, fake_uuid):
    """Test creating a partial to do item"""
    todo_mock = mock.MagicMock()
    created_item = mock.MagicMock()
    todo_mock.return_value = created_item

    monkeypatch.setattr("todos.TodoModel", todo_mock)
    monkeypatch.setattr("uuid.uuid1", fake_uuid)

    response = todos.create(
        {
            "body": json.dumps({"content": "test content"}),
            "requestContext": {"identity": {"cognitoIdentityId": "USER-SUB-1234"}},
        },
        {},
    )

    todo_mock.assert_called_with(
        "USER-SUB-1234", "fakeuuid", content="test content", relevantInstrument=None
    )

    created_item.save.assert_called()

    assert response["statusCode"] == 201


def test_create_todo_incomplete_bad_request():
    """Test missing data returns bad request"""
    response = todos.create({"body": json.dumps({})}, {})

    assert response["statusCode"] == 400
