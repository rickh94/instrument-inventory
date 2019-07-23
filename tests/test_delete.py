from unittest import mock

from app import delete
from app.utils.models import InstrumentModel


def test_delete(monkeypatch, fake_instrument):
    """Test deleting and instrument"""
    instrument_mock = mock.MagicMock()
    instrument_item = fake_instrument(
        "fakeid", number="1234", size="4/4", type="violin", location="office"
    )
    instrument_mock.get.return_value = instrument_item

    monkeypatch.setattr("app.delete.InstrumentModel", instrument_mock)

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

    monkeypatch.setattr("app.delete.InstrumentModel", instrument_mock)
    monkeypatch.setattr("app.delete.delete_photos", delete_photos_mock)

    response = delete.main({"pathParameters": {"id": "fakeid"}}, {})

    instrument_mock.get.assert_called_with("fakeid")
    instrument_item.delete.assert_called()
    delete_photos_mock.assert_called_with("test_photo.jpg")

    assert response["statusCode"] == 204


def test_delete_no_id():
    """Test no id returns bad request"""
    response = delete.main({}, {})

    assert response["statusCode"] == 400


def test_delete_not_found(monkeypatch, db_not_found):
    """Test item is not found"""
    monkeypatch.setattr("app.delete.InstrumentModel.get", db_not_found)

    response = delete.main({"pathParameters": {"id": "fakeid"}}, {})

    assert response["statusCode"] == 404
