from unittest import mock

import pytest

import app.bows.create


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
