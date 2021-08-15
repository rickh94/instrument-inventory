from unittest import mock

import pytest
import ujson

import app.other.create
import app.other.get
import app.other.update
from app.utils.api_models import Location


@pytest.fixture
def fake_other():
    class FakeOther:
        def __init__(
            self,
            id_,
            name,
            count,
            signed_out_to=None,
            notes=None,
            location_counts=None,
        ):
            self.id = id_
            self.name = name
            self.count = count
            self.signed_out_to = signed_out_to
            self.notes = notes
            self.location_counts = location_counts

        @property
        def attribute_values(self):
            return self.__dict__

        def refresh(self):
            pass

    return FakeOther


@pytest.fixture
def fake_items(fake_other):
    return [
        fake_other(
            id_="id0",
            name="Metronome",
            count=5,
            signed_out_to=["Person1", "Person2", "Person3"],
            notes="Some Metronomes",
        ),
        fake_other(id_="id1", name="Shoulder Rest", count=3),
        fake_other(
            id_="id2",
            name="Rosin",
            count=4,
            notes="Ugh",
            location_counts={Location.westminster: 3, Location.storage: 2},
        ),
    ]


def test_item_create_minimal(monkeypatch):
    item_create_event = {
        "body": ujson.dumps({"name": "Metronome", "count": 0}),
        "requestContext": {"identity": {"cognitoIdentityId": "USER-SUB-1234"}},
    }
    created_item = mock.MagicMock()
    created_item.name = "Metronome"
    created_item.count = 0
    created_item.signed_out_to = []
    created_item.notes = None

    created_item.attribute_values = {
        "name": "Metronome",
        "count": 0,
        "signed_out_to": [],
        "notes": None,
        "id": "id0",
    }

    other_mock = mock.MagicMock()
    other_mock.scan.return_value = []
    other_mock.return_value = created_item

    monkeypatch.setattr("app.other.create.OtherModel", other_mock)

    response = app.other.create.main(item_create_event, {})
    print(response)

    assert response["statusCode"] == 201

    other_mock.assert_called_once_with(
        name="Metronome", count=0, location_counts=None, signed_out_to=None, notes=None
    )
    created_item.save.assert_called()


def test_item_create_complete(monkeypatch):
    attributes = {
        "name": "Shoulder Rest",
        "count": 6,
        "signed_out_to": ["Person1", "person2", "3person"],
        "notes": "Some things about these things",
        "location_counts": {"Storage": 2, "Office": 1},
    }
    item_create_event = {
        "body": ujson.dumps(attributes),
        "requestContext": {"identity": {"cognitoIdentityId": "USER-SUB-1234"}},
    }
    created_item = mock.MagicMock()
    for k, v in attributes.items():
        setattr(created_item, k, v)
    created_item.attribute_values = {**attributes, "id": "id0"}

    other_mock = mock.MagicMock()
    other_mock.scan.return_value = []
    other_mock.return_value = created_item

    monkeypatch.setattr("app.other.create.OtherModel", other_mock)

    response = app.other.create.main(item_create_event, {})

    other_mock.assert_called_once_with(
        name="Shoulder Rest",
        count=6,
        signed_out_to=["Person1", "person2", "3person"],
        notes="Some things about these things",
        location_counts={"Storage": 2, "Office": 1},
    )
    created_item.save.assert_called()

    assert response["statusCode"] == 201


def test_get_successful(monkeypatch, fake_items):
    db_mock = mock.MagicMock()
    db_mock.scan.return_value = fake_items

    monkeypatch.setattr("app.other.get.OtherModel", db_mock)

    response = app.other.get.main({}, {})

    assert response["statusCode"] == 200


def test_use_other(monkeypatch, fake_items):
    """Test using other items"""
    db_mock = mock.MagicMock()

    def mock_query(id_):
        for item in fake_items:
            if item.id == id_:
                item.save = mock.MagicMock()
                return [item]

    db_mock.query = mock_query

    monkeypatch.setattr("app.other.update.OtherModel", db_mock)

    data = {
        "item_updates": [
            {"id": "id0", "amount": 3},
            {"id": "id1", "amount": 2},
            {"id": "id2", "amount": 1},
        ]
    }

    response = app.other.update.use_items({"body": ujson.dumps(data)}, {})

    assert response["statusCode"] == 200

    body = ujson.loads(response["body"])
    assert len(body["updated"]) == 3
    assert len(body["failed"]) == 0

    assert fake_items[0].count == 2
    assert fake_items[0].location_counts["Storage"] == 0
    fake_items[0].save.assert_called()

    assert fake_items[1].count == 1
    assert fake_items[1].location_counts["Storage"] == 0
    fake_items[2].save.assert_called()

    assert fake_items[2].count == 3
    assert fake_items[2].location_counts["Storage"] == 1
    fake_items[2].save.assert_called()


def test_add_other(monkeypatch, fake_items):
    """Test adding items"""
    db_mock = mock.MagicMock()

    def mock_query(id_):
        for item in fake_items:
            if item.id == id_:
                item.save = mock.MagicMock()
                return [item]

    db_mock.query = mock_query

    monkeypatch.setattr("app.other.update.OtherModel", db_mock)

    data = {
        "item_updates": [
            {"id": "id0", "amount": 8},
            {"id": "id1", "amount": 3},
            {"id": "id2", "amount": 1},
        ]
    }

    response = app.other.update.add_items({"body": ujson.dumps(data)}, {})

    assert response["statusCode"] == 200
    body = ujson.loads(response["body"])
    assert len(body["updated"]) == 3
    assert len(body["failed"]) == 0

    assert fake_items[0].count == 13
    assert fake_items[0].location_counts["Storage"] == 8
    fake_items[0].save.assert_called()

    assert fake_items[1].count == 6
    assert fake_items[1].location_counts["Storage"] == 3
    fake_items[1].save.assert_called()

    assert fake_items[2].count == 5
    assert fake_items[2].location_counts["Storage"] == 3
    fake_items[2].save.assert_called()


def test_sign_out_other(monkeypatch, fake_items):
    """Test signing out a random object"""
    db_mock = mock.MagicMock()
    fake_items[0].save = mock.MagicMock()
    db_mock.query.return_value = [fake_items[0]]

    monkeypatch.setattr("app.other.update.OtherModel", db_mock)

    to = "Test Person"
    id_ = "id0"

    response = app.other.update.sign_out(
        {"body": ujson.dumps({"to": to, "id": id_})}, {}
    )

    assert response["statusCode"] == 200
    assert fake_items[0].location_counts["Storage"] == 0
    assert to in fake_items[0].signed_out_to
    fake_items[0].save.assert_called()


def test_sign_out_other_from_storage(monkeypatch, fake_items):
    """Test signing out an item removes it from storage"""
    db_mock = mock.MagicMock()
    fake_items[2].save = mock.MagicMock()
    db_mock.query.return_value = [fake_items[2]]

    monkeypatch.setattr("app.other.update.OtherModel", db_mock)

    to = "Test Person"
    id_ = "id0"

    response = app.other.update.sign_out(
        {"body": ujson.dumps({"to": to, "id": id_})}, {}
    )

    assert response["statusCode"] == 200
    assert fake_items[2].location_counts["Storage"] == 1
    assert to in fake_items[2].signed_out_to
    fake_items[2].save.assert_called()


def test_retrieve_other(monkeypatch, fake_items):
    """Test retrieving a random object"""
    db_mock = mock.MagicMock()
    fake_items[0].save = mock.MagicMock()
    db_mock.query.return_value = [fake_items[0]]

    monkeypatch.setattr("app.other.update.OtherModel", db_mock)

    from_ = "Person1"
    id_ = "id0"

    response = app.other.update.retrieve(
        {"body": ujson.dumps({"from": from_, "id": id_})}, {}
    )

    assert response["statusCode"] == 200
    assert fake_items[0].count == 5
    assert fake_items[0].location_counts["Storage"] == 1
    assert from_ not in fake_items[0].signed_out_to
    fake_items[0].save.assert_called()


def test_lose_other(monkeypatch, fake_items):
    db_mock = mock.MagicMock()
    fake_items[0].save = mock.MagicMock()
    db_mock.query.return_value = [fake_items[0]]

    monkeypatch.setattr("app.other.update.OtherModel", db_mock)

    id_ = "id0"
    from_ = "Person1"

    response = app.other.update.lose(
        {"body": ujson.dumps({"from": from_, "id": id_})}, {}
    )

    assert response["statusCode"] == 200
    assert fake_items[0].count == 5
    assert from_ not in fake_items[0].signed_out_to
    fake_items[0].save.assert_called()


def test_move_too_many_items(monkeypatch, fake_items):
    db_mock = mock.MagicMock()
    fake_items[0].save = mock.MagicMock()
    db_mock.query.return_value = [fake_items[0]]

    monkeypatch.setattr("app.other.update.OtherModel", db_mock)

    response = app.other.update.move(
        {
            "body": ujson.dumps(
                {
                    "id": fake_items[0].id,
                    "count": 8,
                    "from_location": "Storage",
                    "to_location": "Westminster Presbyterian Church",
                }
            )
        },
        {},
    )

    assert response["statusCode"] == 400


def test_move_other_from_storage(monkeypatch, fake_items):
    db_mock = mock.MagicMock()
    fake_items[2].save = mock.MagicMock()
    db_mock.query.return_value = [fake_items[2]]

    monkeypatch.setattr("app.other.update.OtherModel", db_mock)

    response = app.other.update.move(
        {
            "body": ujson.dumps(
                {
                    "id": fake_items[2].id,
                    "count": 2,
                    "from_location": "Storage",
                    "to_location": "Westminster Presbyterian Church",
                }
            )
        },
        {},
    )

    assert response["statusCode"] == 200
    assert fake_items[2].location_counts["Storage"] == 0
    assert fake_items[2].location_counts["Westminster Presbyterian Church"] == 5


def test_move_other_to_storage(monkeypatch, fake_items):
    db_mock = mock.MagicMock()
    fake_items[2].save = mock.MagicMock()
    db_mock.query.return_value = [fake_items[2]]

    monkeypatch.setattr("app.other.update.OtherModel", db_mock)

    response = app.other.update.move(
        {
            "body": ujson.dumps(
                {
                    "id": fake_items[2].id,
                    "count": 2,
                    "to_location": "Storage",
                    "from_location": "Westminster Presbyterian Church",
                }
            )
        },
        {},
    )

    assert response["statusCode"] == 200
    assert fake_items[2].location_counts["Storage"] == 4
    assert fake_items[2].location_counts["Westminster Presbyterian Church"] == 1
