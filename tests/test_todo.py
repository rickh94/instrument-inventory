import json
from unittest import mock

import pynamodb.exceptions
import pytest

from app import todos
from app.utils.models import TodoModel


@pytest.fixture
def make_fake_todo_item():
    class FakeTodoItem:
        def __init__(
            self, userId, todoId, content, relevantInstrument="", completed=False
        ):
            self.userId = userId
            self.todoId = todoId
            self.content = content
            self.completed = completed
            self.relevantInstrument = relevantInstrument
            self.update = mock.MagicMock()
            self.refresh = mock.MagicMock()
            self.save = mock.MagicMock()
            self.delete = mock.MagicMock()

        @property
        def attribute_values(self):
            return {
                "userId": self.userId,
                "todoId": self.todoId,
                "content": self.content,
                "completed": self.completed,
            }

    return FakeTodoItem


def test_create_todo_full(monkeypatch, make_fake_todo_item):
    """Test creating a to do item"""
    todo_mock = mock.MagicMock()
    created_item = make_fake_todo_item(
        "USER-SUB-1234",
        "fakeuuid",
        content="test content",
        relevantInstrument="1-610",
        completed=False,
    )

    todo_mock.return_value = created_item

    monkeypatch.setattr("app.todos.TodoModel", todo_mock)
    event = {
        "body": json.dumps({"content": "test content", "relevantInstrument": "1-610"}),
        "requestContext": {"identity": {"cognitoIdentityId": "USER-SUB-1234"}},
    }

    # noinspection PyTypeChecker
    response = todos.create(event, {})

    assert response["statusCode"] == 201

    todo_mock.assert_called_with(
        "USER-SUB-1234",
        content="test content",
        relevantInstrument="1-610",
        completed=False,
    )

    created_item.save.assert_called()


def test_create_todo_partial(monkeypatch, make_fake_todo_item):
    """Test creating a partial to do item"""
    todo_mock = mock.MagicMock()
    created_item = make_fake_todo_item(
        "USER-SUB-1234", "fakeuuid", content="test content"
    )
    todo_mock.return_value = created_item

    monkeypatch.setattr("app.todos.TodoModel", todo_mock)
    event = {
        "body": json.dumps({"content": "test content"}),
        "requestContext": {"identity": {"cognitoIdentityId": "USER-SUB-1234"}},
    }

    # noinspection PyTypeChecker
    response = todos.create(event, {})
    assert response["statusCode"] == 201

    todo_mock.assert_called_with(
        "USER-SUB-1234",
        content="test content",
        relevantInstrument=None,
        completed=False,
    )

    created_item.save.assert_called()


def test_create_todo_incomplete_invalid():
    """Test missing data returns validation error"""
    # noinspection PyTypeChecker
    response = todos.create({"body": json.dumps({})}, {})

    assert response["statusCode"] == 422


def test_read_single(monkeypatch, make_fake_todo_item):
    """Test getting a single to do item"""
    todo_mock = mock.MagicMock()
    todo_mock.get.return_value = make_fake_todo_item(
        "USER-SUB-1234", "testuuid", content="test read"
    )

    monkeypatch.setattr("app.todos.TodoModel", todo_mock)

    response = todos.read_single(
        {
            "pathParameters": {"id": "testuuid"},
            "requestContext": {"identity": {"cognitoIdentityId": "USER-SUB-1234"}},
        },
        {},
    )

    todo_mock.get.assert_called_with("USER-SUB-1234", "testuuid")

    assert response["statusCode"] == 200
    expected = {
        "todoId": "testuuid",
        "content": "test read",
        "relevantInstrument": None,
        "completed": False,
    }
    actual = json.loads(response["body"])
    for k, v in expected.items():
        assert actual[k] == v


def test_read_single_no_item(monkeypatch):
    """Test failure to get item"""

    def bad_get(*_):
        raise TodoModel.DoesNotExist

    monkeypatch.setattr("app.todos.TodoModel.get", bad_get)

    response = todos.read_single(
        {
            "pathParameters": {"id": "fail"},
            "requestContext": {"identity": {"cognitoIdentityId": "USER-SUB-1234"}},
        },
        {},
    )

    assert response["statusCode"] == 404


def test_read_single_bad_request():
    """Test that missing parameters creates bad request"""

    response = todos.read_single({}, {})

    assert response["statusCode"] == 400


def test_read_active(monkeypatch, make_fake_todo_item):
    """Test getting all uncompleted to do items"""

    fake_todo = mock.MagicMock()
    fake_todo.query.return_value = [
        make_fake_todo_item("USER-SUB-1234", "id1", content="test todo 1"),
        make_fake_todo_item("USER-SUB-1234", "id2", content="test todo 2"),
        make_fake_todo_item("USER-SUB-1234", "id3", content="test todo 3"),
    ]

    monkeypatch.setattr("app.todos.TodoModel", fake_todo)

    response = todos.read_active(
        {"requestContext": {"identity": {"cognitoIdentityId": "USER-SUB-1234"}}}, {}
    )

    fake_todo.query.assert_called_with("USER-SUB-1234", mock.ANY)

    assert response["statusCode"] == 200
    assert {item["todoId"] for item in json.loads(response["body"])} == {
        "id1",
        "id2",
        "id3",
    }


def test_read_active_fails(monkeypatch, explode):
    """Test reading active todos fails"""
    monkeypatch.setattr("app.todos.TodoModel.query", explode)

    response = todos.read_active(
        {"requestContext": {"identity": {"cognitoIdentityId": "USER-SUB-1234"}}}, {}
    )

    assert response["statusCode"] == 500


def test_read_complete(monkeypatch, make_fake_todo_item):
    """Test getting all completed to do items"""

    fake_todo = mock.MagicMock()
    fake_todo.query.return_value = [
        make_fake_todo_item(
            "USER-SUB-1234", "id1", content="test todo 1", completed=True
        ),
        make_fake_todo_item(
            "USER-SUB-1234", "id2", content="test todo 2", completed=True
        ),
        make_fake_todo_item(
            "USER-SUB-1234", "id3", content="test todo 3", completed=True
        ),
    ]

    monkeypatch.setattr("app.todos.TodoModel", fake_todo)

    response = todos.read_completed(
        {"requestContext": {"identity": {"cognitoIdentityId": "USER-SUB-1234"}}}, {}
    )

    fake_todo.query.assert_called_with("USER-SUB-1234", mock.ANY)

    assert response["statusCode"] == 200
    assert {item["todoId"] for item in json.loads(response["body"])} == {
        "id1",
        "id2",
        "id3",
    }


def test_read_complete_fails(monkeypatch, explode):
    """Test reading complete todos fails"""
    monkeypatch.setattr("app.todos.TodoModel.query", explode)

    response = todos.read_completed(
        {"requestContext": {"identity": {"cognitoIdentityId": "USER-SUB-1234"}}}, {}
    )

    assert response["statusCode"] == 500


def test_mark_item_completed(monkeypatch, make_fake_todo_item):
    """Test marking an item complete"""
    fake_todo = mock.MagicMock()
    todo_item = make_fake_todo_item(
        "USER-SUB-1234", "id1", content="test todo1", completed=False
    )
    fake_todo.get.return_value = todo_item

    monkeypatch.setattr("app.todos.TodoModel", fake_todo)

    response = todos.mark_completed(
        {
            "requestContext": {"identity": {"cognitoIdentityId": "USER-SUB-1234"}},
            "pathParameters": {"id": "id1"},
        },
        {},
    )

    fake_todo.get.assert_called_with("USER-SUB-1234", "id1")
    assert todo_item.completed is True
    todo_item.save.assert_called()
    todo_item.refresh.assert_called()

    assert response["statusCode"] == 200


def test_mark_item_completed_bad_request():
    """Test no id in path"""
    response = todos.mark_completed({}, {})

    assert response["statusCode"] == 400


def test_mark_item_completed_does_not_exist(monkeypatch, db_not_found):
    """Test id does not exist"""
    monkeypatch.setattr("app.todos.TodoModel.get", db_not_found)

    response = todos.mark_completed(
        {
            "requestContext": {"identity": {"cognitoIdentityId": "USER-SUB-1234"}},
            "pathParameters": {"id": "id1"},
        },
        {},
    )

    assert response["statusCode"] == 404


def test_unmark_item_completed(monkeypatch, make_fake_todo_item):
    """Test unmarking an item complete"""
    fake_todo = mock.MagicMock()
    todo_item = make_fake_todo_item(
        "USER-SUB-1234", "id1", content="test todo1", completed=True
    )
    fake_todo.get.return_value = todo_item

    monkeypatch.setattr("app.todos.TodoModel", fake_todo)

    response = todos.unmark_completed(
        {
            "requestContext": {"identity": {"cognitoIdentityId": "USER-SUB-1234"}},
            "pathParameters": {"id": "id1"},
        },
        {},
    )

    fake_todo.get.assert_called_with("USER-SUB-1234", "id1")

    assert todo_item.completed is False
    todo_item.save.assert_called()
    todo_item.refresh.assert_called()

    assert response["statusCode"] == 200


def test_unmark_item_completed_bad_request():
    """Test no id in path"""
    response = todos.unmark_completed({}, {})

    assert response["statusCode"] == 400


def test_unmark_item_completed_does_not_exist(monkeypatch, db_not_found):
    """Test id does not exist"""

    monkeypatch.setattr("app.todos.TodoModel.get", db_not_found)

    response = todos.unmark_completed(
        {
            "requestContext": {"identity": {"cognitoIdentityId": "USER-SUB-1234"}},
            "pathParameters": {"id": "id1"},
        },
        {},
    )

    assert response["statusCode"] == 404


def test_update_todo_full(monkeypatch, make_fake_todo_item):
    """Test update a to do item"""
    fake_todo = mock.MagicMock()
    todo_item = make_fake_todo_item(
        "USER-SUB-1234",
        "id1",
        content="test todo1",
        relevantInstrument="1-610",
        completed=False,
    )
    fake_todo.get.return_value = todo_item

    monkeypatch.setattr("app.todos.TodoModel", fake_todo)

    response = todos.update(
        {
            "requestContext": {"identity": {"cognitoIdentityId": "USER-SUB-1234"}},
            "pathParameters": {"id": "id1"},
            "body": json.dumps(
                {"content": "some different content", "relevantInstrument": "1-611"}
            ),
        },
        {},
    )
    print(response)

    fake_todo.get.assert_called_with("USER-SUB-1234", "id1")

    assert todo_item.content == "some different content"
    assert todo_item.relevantInstrument == "1-611"
    todo_item.save.assert_called()
    todo_item.refresh.assert_called()

    assert response["statusCode"] == 200


def test_update_todo_partial(monkeypatch, make_fake_todo_item):
    """Test partially update a to do item"""
    fake_todo = mock.MagicMock()
    todo_item = make_fake_todo_item(
        "USER-SUB-1234",
        "id1",
        content="test todo1",
        relevantInstrument="1-610",
        completed=False,
    )
    fake_todo.get.return_value = todo_item

    monkeypatch.setattr("app.todos.TodoModel", fake_todo)

    response = todos.update(
        {
            "requestContext": {"identity": {"cognitoIdentityId": "USER-SUB-1234"}},
            "pathParameters": {"id": "id1"},
            "body": json.dumps({"relevantInstrument": "1-611"}),
        },
        {},
    )

    fake_todo.get.assert_called_with("USER-SUB-1234", "id1")

    assert todo_item.content == "test todo1"
    assert todo_item.relevantInstrument == "1-611"
    todo_item.save.assert_called()
    todo_item.refresh.assert_called()

    assert response["statusCode"] == 200


def test_update_no_id_bad_request():
    """Test missing id returns not found"""
    response = todos.update({"body": json.dumps({})}, {})

    assert response["statusCode"] == 400


def test_update_does_not_exist_not_found(monkeypatch, db_not_found):
    """Test returns 404 error if to do item is not found"""
    monkeypatch.setattr("app.todos.TodoModel.get", db_not_found)

    response = todos.update(
        {
            "requestContext": {"identity": {"cognitoIdentityId": "USER-SUB-1234"}},
            "pathParameters": {"id": "id1"},
            "body": json.dumps({}),
        },
        {},
    )

    assert response["statusCode"] == 404


def test_delete_todo(monkeypatch, make_fake_todo_item):
    """Test deleting a to do item"""
    fake_todo = mock.MagicMock()
    todo_item = make_fake_todo_item(
        "USER-SUB-1234",
        "id1",
        content="test todo1",
        relevantInstrument="1-610",
        completed=False,
    )
    fake_todo.get.return_value = todo_item

    monkeypatch.setattr("app.todos.TodoModel", fake_todo)

    response = todos.delete(
        {
            "requestContext": {"identity": {"cognitoIdentityId": "USER-SUB-1234"}},
            "pathParameters": {"id": "id1"},
        },
        {},
    )

    fake_todo.get.assert_called_with("USER-SUB-1234", "id1")
    todo_item.delete.assert_called()

    assert response["statusCode"] == 204


def test_delete_todo_bad_request():
    """Test no id returns bad request"""
    response = todos.delete({"body": json.dumps({})}, {})

    assert response["statusCode"] == 400


def test_delete_todo_not_found(monkeypatch, db_not_found):
    """Test delete to do not found returns 404"""
    monkeypatch.setattr("app.todos.TodoModel.get", db_not_found)

    response = todos.delete(
        {
            "requestContext": {"identity": {"cognitoIdentityId": "USER-SUB-1234"}},
            "pathParameters": {"id": "id1"},
            "body": json.dumps({}),
        },
        {},
    )

    assert response["statusCode"] == 404
