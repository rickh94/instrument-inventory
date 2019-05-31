import json
from unittest import mock

import pytest

import todos
from models import TodoModel
import pynamodb.exceptions


@pytest.fixture
def fake_uuid():
    def _uuid():
        return "fakeuuid"

    return _uuid


def test_create_todo_full(monkeypatch, fake_uuid):
    """Test creating a to do item"""
    todo_mock = mock.MagicMock()
    created_item = mock.MagicMock()
    created_item.todoId = ("fakeuuid",)
    created_item.content = "test content"
    created_item.relevantInstrument = "1-610"
    created_item.completed = False
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
    created_item.todoId = ("fakeuuid",)
    created_item.content = "test content"
    created_item.relevantInstrument = None
    created_item.completed = False
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


@pytest.fixture
def fake_todo():
    class FakeTodo:
        def __init__(self, content, relevant_instrument=None, completed=False):
            self.userId = "USER-SUB-1234"
            self.todoId = "testuuid"
            self.content = content
            self.relevantInstrument = relevant_instrument
            self.completed = completed

    return FakeTodo


def test_read_single(monkeypatch, fake_todo):
    """Test getting a single to do item"""
    todo_mock = mock.MagicMock()
    todo_mock.get.return_value = fake_todo("test read")

    monkeypatch.setattr("todos.TodoModel", todo_mock)

    response = todos.read_single(
        {
            "pathParameters": {"id": "testuuid"},
            "requestContext": {"identity": {"cognitoIdentityId": "USER-SUB-1234"}},
        },
        {},
    )

    todo_mock.get.assert_called_with("USER-SUB-1234", "testuuid")

    assert response["statusCode"] == 200
    assert response["body"] == json.dumps(
        {
            "todoId": "testuuid",
            "content": "test read",
            "relevantInstrument": None,
            "completed": False,
        }
    )


def test_read_single_no_item(monkeypatch):
    """Test failure to get item"""

    def bad_get(*args):
        raise TodoModel.DoesNotExist

    monkeypatch.setattr("todos.TodoModel.get", bad_get)

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


def test_read_active(monkeypatch):
    """Test getting all uncompleted to do items"""

    class FakeTodoItem:
        def __init__(self, userId, todoId, content):
            self.userId = userId
            self.todoId = todoId
            self.content = content

        @property
        def attribute_values(self):
            return {
                "userId": self.userId,
                "todoId": self.todoId,
                "content": self.content,
            }

    fake_todo = mock.MagicMock()
    fake_todo.query.return_value = [
        FakeTodoItem("USER-SUB-1234", "id1", content="test todo 1"),
        FakeTodoItem("USER-SUB-1234", "id2", content="test todo 2"),
        FakeTodoItem("USER-SUB-1234", "id3", content="test todo 3"),
    ]

    monkeypatch.setattr("todos.TodoModel", fake_todo)

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


def test_read_active_fails(monkeypatch):
    """Test reading active todos fails"""

    def explode(*args):
        raise Exception

    monkeypatch.setattr("todos.TodoModel.query", explode)

    response = todos.read_active(
        {"requestContext": {"identity": {"cognitoIdentityId": "USER-SUB-1234"}}}, {}
    )

    assert response["statusCode"] == 500


@pytest.fixture
def make_fake_todo_item():
    class FakeTodoItem:
        def __init__(self, userId, todoId, content, completed=False):
            self.userId = userId
            self.todoId = todoId
            self.content = content
            self.completed = completed
            self.update = mock.MagicMock()
            self.refresh = mock.MagicMock()
            self.save = mock.MagicMock()

        @property
        def attribute_values(self):
            return {
                "userId": self.userId,
                "todoId": self.todoId,
                "content": self.content,
                "completed": self.completed,
            }

    return FakeTodoItem


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

    monkeypatch.setattr("todos.TodoModel", fake_todo)

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


def test_read_complete_fails(monkeypatch):
    """Test reading complete todos fails"""

    def explode(*args):
        raise Exception

    monkeypatch.setattr("todos.TodoModel.query", explode)

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

    monkeypatch.setattr("todos.TodoModel", fake_todo)

    response = todos.mark_completed(
        {
            "requestContext": {"identity": {"cognitoIdentityId": "USER-SUB-1234"}},
            "pathParameters": {"id": "id1"},
        },
        {},
    )

    fake_todo.get.assert_called_with("USER-SUB-1234", "id1")
    fake_todo.completed.set.assert_called_with(True)
    todo_item.update.assert_called()
    todo_item.save.assert_called()
    todo_item.refresh.assert_called()

    assert response["statusCode"] == 200


def test_mark_item_completed_bad_request():
    """Test no id in path"""
    response = todos.mark_completed({}, {})

    assert response["statusCode"] == 400


def test_mark_item_completed_does_not_exist(monkeypatch):
    """Test id does not exist"""

    def get_explode(*args):
        raise pynamodb.exceptions.DoesNotExist

    monkeypatch.setattr("todos.TodoModel.get", get_explode)

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

    monkeypatch.setattr("todos.TodoModel", fake_todo)

    response = todos.unmark_completed(
        {
            "requestContext": {"identity": {"cognitoIdentityId": "USER-SUB-1234"}},
            "pathParameters": {"id": "id1"},
        },
        {},
    )

    fake_todo.get.assert_called_with("USER-SUB-1234", "id1")
    fake_todo.completed.set.assert_called_with(False)
    todo_item.update.assert_called()
    todo_item.save.assert_called()
    todo_item.refresh.assert_called()

    assert response["statusCode"] == 200


def test_unmark_item_completed_bad_request():
    """Test no id in path"""
    response = todos.unmark_completed({}, {})

    assert response["statusCode"] == 400


def test_unmark_item_completed_does_not_exist(monkeypatch):
    """Test id does not exist"""

    def get_explode(*args):
        raise pynamodb.exceptions.DoesNotExist

    monkeypatch.setattr("todos.TodoModel.get", get_explode)

    response = todos.unmark_completed(
        {
            "requestContext": {"identity": {"cognitoIdentityId": "USER-SUB-1234"}},
            "pathParameters": {"id": "id1"},
        },
        {},
    )

    assert response["statusCode"] == 404
