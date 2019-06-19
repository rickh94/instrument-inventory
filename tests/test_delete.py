from unittest import mock

import delete
from models import InstrumentModel


def test_delete(monkeypatch, fake_instrument):
    """Test deleting and instrument"""
    instrument_mock = mock.MagicMock()
    instrument_item = fake_instrument(
        "fakeid", number="1234", size="4/4", type="violin", location="office"
    )
    instrument_mock.get.return_value = instrument_item

    monkeypatch.setattr("delete.InstrumentModel", instrument_mock)

    response = delete.main({"pathParameters": {"id": "fakeid"}}, {})

    instrument_mock.get.assert_called_with("fakeid")
    instrument_item.delete.assert_called()

    assert response["statusCode"] == 204


def test_delete_associated_photo(monkeypatch, fake_instrument):
    """Test deleting instrument deletes associated photo"""
    instrument_mock = mock.MagicMock()
    instrument_item = fake_instrument(
        "fakeid",
        number="1234",
        size="4/4",
        type="violin",
        location="office",
        photo="test_photo.jpg",
    )
    instrument_mock.get.return_value = instrument_item
    delete_photos_mock = mock.MagicMock()

    monkeypatch.setattr("delete.InstrumentModel", instrument_mock)
    monkeypatch.setattr("delete.delete_photos", delete_photos_mock)

    response = delete.main({"pathParameters": {"id": "fakeid"}}, {})

    instrument_mock.get.assert_called_with("fakeid")
    instrument_item.delete.assert_called()
    delete_photos_mock.assert_called_with("test_photo.jpg")

    assert response["statusCode"] == 204


def test_delete_no_id():
    """Test no id returns bad request"""
    response = delete.main({}, {})

    assert response["statusCode"] == 400


def test_delete_not_found(monkeypatch):
    """Test item is not found"""

    def explode(*args):
        raise InstrumentModel.DoesNotExist

    monkeypatch.setattr("delete.InstrumentModel.get", explode)

    response = delete.main({"pathParameters": {"id": "fakeid"}}, {})

    assert response["statusCode"] == 404
