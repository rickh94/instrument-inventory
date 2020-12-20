from unittest import mock

import pytest
import ujson

import app.strings.create
import app.strings.get
import app.strings.update


@pytest.fixture
def fake_string():
    class FakeString:
        def __init__(self, id_, type, size, string, count=0):
            self.id = id_
            self.type = type
            self.size = size
            self.string = string
            self.count = count

        @property
        def attribute_values(self):
            return {
                "id": self.id,
                "type": self.type,
                "size": self.size,
                "string": self.string,
                "count": self.count,
            }

        def refresh(self):
            pass

        def save(self):
            pass

    return FakeString


@pytest.fixture
def fake_strings(fake_string):
    return [
        fake_string(id_="id0", type="Violin", size="4/4", string="E", count=10),
        fake_string(id_="id1", type="Viola", size='15"', string="C", count=1),
        fake_string(id_="id2", type="Cello", size="1/4", string="D", count=5),
    ]


def test_string_create_successful(monkeypatch, string_create_event):
    """Test string creation event"""
    string_mock = mock.MagicMock()
    created_item = mock.MagicMock()
    created_item.attribute_values = {
        "id": "fakeuuid",
        "type": "Violin",
        "size": "4/4",
        "string": "A",
        "count": 0,
    }
    created_item.type = "Violin"
    created_item.size = "4/4"
    created_item.string = "A"
    created_item.count = 0
    string_mock.scan.return_value = []
    string_mock.return_value = created_item

    monkeypatch.setattr("app.strings.create.StringModel", string_mock)

    response = app.strings.create.main(string_create_event, {})

    string_mock.assert_called_with(type="Violin", size="4/4", count=0, string="A")

    created_item.save.assert_called()

    assert response["statusCode"] == 201


def test_get_successful(monkeypatch, fake_strings):
    db_mock = mock.MagicMock()
    db_mock.scan.return_value = fake_strings
    monkeypatch.setattr("app.strings.get.StringModel", db_mock)

    response = app.strings.get.main({}, {})

    assert response["statusCode"] == 200


def test_use_strings(monkeypatch, fake_strings):
    db_mock = mock.MagicMock()

    def mock_query(id_):
        for item in fake_strings:
            if item.id == id_:
                item.save = mock.MagicMock()
                return [item]

    db_mock.query = mock_query

    monkeypatch.setattr("app.strings.update.StringModel", db_mock)

    data = {
        "string_updates": [
            {"id": "id0", "amount": 4},
            {"id": "id1", "amount": 1},
            {"id": "id2", "amount": 2},
        ]
    }

    response = app.strings.update.use_strings({"body": ujson.dumps(data)}, {})

    assert response["statusCode"] == 200
    body = ujson.loads(response["body"])

    assert len(body["updated"]) == 3
    assert len(body["failed"]) == 0

    assert fake_strings[0].count == 6
    fake_strings[0].save.assert_called()

    assert fake_strings[1].count == 0
    fake_strings[1].save.assert_called()

    assert fake_strings[2].count == 3
    fake_strings[2].save.assert_called()


def test_add_strings(monkeypatch, fake_strings):
    db_mock = mock.MagicMock()

    def mock_query(id_):
        for item in fake_strings:
            if item.id == id_:
                item.save = mock.MagicMock()
                return [item]

    db_mock.query = mock_query

    monkeypatch.setattr("app.strings.update.StringModel", db_mock)

    data = {
        "string_updates": [
            {"id": "id0", "amount": 2},
            {"id": "id1", "amount": 6},
            {"id": "id2", "amount": 1},
        ]
    }

    response = app.strings.update.add_strings({"body": ujson.dumps(data)}, {})

    assert response["statusCode"] == 200
    body = ujson.loads(response["body"])
    assert len(body["updated"]) == 3
    assert len(body["failed"]) == 0

    assert fake_strings[0].count == 12
    fake_strings[0].save.assert_called()

    assert fake_strings[1].count == 7
    fake_strings[1].save.assert_called()

    assert fake_strings[2].count == 6
    fake_strings[2].save.assert_called()
