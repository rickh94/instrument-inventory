from unittest import mock

import pytest
import ujson

import app.bows.create
import app.bows.get
import app.bows.update


@pytest.fixture
def fake_bow():
    class FakeBow:
        def __init__(self, id_, type, size, count=0):
            self.id = id_
            self.type = type
            self.size = size
            self.count = count

        @property
        def attribute_values(self):
            return {
                "id": self.id,
                "size": self.size,
                "type": self.type,
                "count": self.count,
            }

        def refresh(self):
            pass

    return FakeBow


@pytest.fixture
def fake_bows(fake_bow):
    return [
        fake_bow(id_="id0", type="Violin", size="4/4", count=3),
        fake_bow(id_="id1", type="Cello", size="1/4", count=4),
        fake_bow(id_="id2", type="Viola", size='12"', count=2),
    ]


def test_bow_create_successful(monkeypatch, bow_create_event):
    """Test a bow creation event"""
    bow_mock = mock.MagicMock()
    created_item = mock.MagicMock()
    created_item.attribute_values = {
        "id": "fakeuuid",
        "type": "Violin",
        "size": "4/4",
        "count": 0,
    }
    created_item.type = "Violin"
    created_item.id = "fakeuuid"
    created_item.size = "4/4"
    created_item.count = 0
    bow_mock.scan.return_value = []
    bow_mock.return_value = created_item

    monkeypatch.setattr("app.bows.create.BowModel", bow_mock)

    response = app.bows.create.main(bow_create_event, {})

    bow_mock.assert_called_with(type="Violin", size="4/4", count=0)
    created_item.save.assert_called()

    assert response["statusCode"] == 201


def test_get_successful(monkeypatch, fake_bows):
    """Test getting all bows"""
    db_mock = mock.MagicMock()
    db_mock.scan.return_value = fake_bows
    monkeypatch.setattr("app.bows.get.BowModel", db_mock)

    response = app.bows.get.main({}, {})

    assert response["statusCode"] == 200


def test_use_bows(monkeypatch, fake_bows):
    """Test using bows"""
    db_mock = mock.MagicMock()

    def mock_query(id_):
        for item in fake_bows:
            if item.id == id_:
                item.save = mock.MagicMock()
                return [item]

    db_mock.query = mock_query

    monkeypatch.setattr("app.bows.update.BowModel", db_mock)

    data = {
        "bow_updates": [
            {"id": "id0", "amount": 1},
            {"id": "id1", "amount": 2},
            {"id": "id2", "amount": 1},
        ]
    }

    response = app.bows.update.use_bows({"body": ujson.dumps(data)}, {})

    assert response["statusCode"] == 200
    body = ujson.loads(response["body"])
    assert len(body["updated"]) == 3
    assert len(body["failed"]) == 0

    assert fake_bows[0].count == 2
    fake_bows[0].save.assert_called()

    assert fake_bows[1].count == 2
    fake_bows[1].save.assert_called()

    assert fake_bows[2].count == 1
    fake_bows[1].save.assert_called()


def test_add_bows(monkeypatch, fake_bows):
    """Test adding bows"""
    db_mock = mock.MagicMock()

    def mock_query(id_):
        for item in fake_bows:
            if item.id == id_:
                item.save = mock.MagicMock()
                return [item]

    db_mock.query = mock_query

    monkeypatch.setattr("app.bows.update.BowModel", db_mock)

    data = {
        "bow_updates": [
            {"id": "id0", "amount": 8},
            {"id": "id1", "amount": 3},
            {"id": "id2", "amount": 1},
        ]
    }

    response = app.bows.update.add_bows({"body": ujson.dumps(data)}, {})

    assert response["statusCode"] == 200
    body = ujson.loads(response["body"])
    assert len(body["updated"]) == 3
    assert len(body["failed"]) == 0

    assert fake_bows[0].count == 11
    fake_bows[0].save.assert_called()

    assert fake_bows[1].count == 7
    fake_bows[1].save.assert_called()

    assert fake_bows[2].count == 3
    fake_bows[1].save.assert_called()
