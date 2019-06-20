import json
from unittest import mock

from app import update
from lib.models import InstrumentModel


def test_add_photo(monkeypatch, fake_instrument):
    """Test adding a photo"""
    instrument_mock = mock.MagicMock()
    instrument_item = fake_instrument(
        "fakeid", number="123", size="4/4", type="violin", location="office"
    )
    instrument_mock.get.return_value = instrument_item
    handle_photo_mock = mock.MagicMock()
    handle_photo_mock.return_value = "fake_photo.jpg"

    monkeypatch.setattr("app.update.InstrumentModel", instrument_mock)
    monkeypatch.setattr("app.update.handle_photo", handle_photo_mock)

    response = update.photo(
        {
            "body": json.dumps({"photoUrl": "http://example.com/image.jpg"}),
            "pathParameters": {"id": "fakeid"},
        },
        {},
    )

    handle_photo_mock.assert_called_with("http://example.com/image.jpg")

    instrument_mock.get.assert_called_with("fakeid")
    instrument_mock.photo.set.assert_called_with("fake_photo.jpg")
    instrument_item.update.assert_called()
    instrument_item.save.assert_called()

    assert response["statusCode"] == 200


def test_add_photo_deletes_old_photo(monkeypatch, fake_instrument):
    instrument_mock = mock.MagicMock()
    instrument_item = fake_instrument(
        "fakeid",
        number="123",
        size="4/4",
        type="violin",
        location="office",
        photo="old_photo.jpg",
    )

    instrument_mock.get.return_value = instrument_item
    delete_photo_mock = mock.MagicMock()
    handle_photo_mock = mock.MagicMock()
    handle_photo_mock.return_value = "fake_photo.jpg"

    monkeypatch.setattr("app.update.InstrumentModel", instrument_mock)
    monkeypatch.setattr("app.update.handle_photo", handle_photo_mock)
    monkeypatch.setattr("app.update.delete_photos", delete_photo_mock)

    response = update.photo(
        {
            "body": json.dumps({"photoUrl": "http://example.com/image.jpg"}),
            "pathParameters": {"id": "fakeid"},
        },
        {},
    )

    handle_photo_mock.assert_called_with("http://example.com/image.jpg")
    delete_photo_mock.assert_called_with("old_photo.jpg")

    instrument_mock.get.assert_called_with("fakeid")
    instrument_mock.photo.set.assert_called_with("fake_photo.jpg")
    instrument_item.update.assert_called()
    instrument_item.save.assert_called()

    assert response["statusCode"] == 200


def test_item_not_found(monkeypatch):
    """Test item not found error causes 404 not found"""

    def db_not_found(*args):
        raise InstrumentModel.DoesNotExist

    monkeypatch.setattr("app.update.InstrumentModel.get", db_not_found)

    response = update.photo(
        {
            "body": json.dumps({"photoUrl": "http://example.com/image.jpg"}),
            "pathParameters": {"id": "fakeid"},
        },
        {},
    )

    assert response["statusCode"] == 404


def test_add_photo_no_id():
    """Test adding a photo with no record id fails"""
    response = update.photo(
        {"body": json.dumps({"photoUrl": "http://example.com/image.jpg"})}, {}
    )

    assert response["statusCode"] == 400


def test_add_photo_no_photo():
    """Test adding a photo with no photo url"""
    response = update.photo(
        {"body": json.dumps({}), "pathParameters": {"id": "fakeid"}}, {}
    )

    assert response["statusCode"] == 400


def test_update_full_record(monkeypatch, fake_instrument):
    """Test updating a record in full"""
    instrument_mock = mock.MagicMock()
    instrument_item = fake_instrument(
        "fakeid", number="V14-502", size='14"', type="viola", location="Storage"
    )
    instrument_mock.get.return_value = instrument_item
    monkeypatch.setattr("app.update.InstrumentModel", instrument_mock)

    response = update.full(
        {
            "pathParameters": {"id": "fakeid"},
            "body": json.dumps(
                {
                    "type": "cello",
                    "number": "C1-502",
                    "size": "4/4",
                    "location": "office",
                    "assignedTo": "Test Name",
                    "condition": 4,
                    "quality": "2",
                    "conditionNotes": "test condition notes",
                    "maintenanceNotes": "test maintenance notes",
                    "rosin": True,
                    "bow": False,
                    "ready": True,
                    "shoulderRestEndpinRest": False,
                    "gifted": True,
                }
            ),
        },
        {},
    )

    instrument_mock.get.assert_called_with("fakeid")
    instrument_mock.type.set.assert_called_with("cello")
    instrument_mock.number.set.assert_called_with("C1-502")
    instrument_mock.size.set.assert_called_with("4/4")
    instrument_mock.location.set.assert_called_with("office")
    instrument_mock.assignedTo.set.assert_called_with("Test Name")
    instrument_mock.condition.set.assert_called_with(4)
    instrument_mock.quality.set.assert_called_with(2)
    instrument_mock.conditionNotes.set.assert_called_with("test condition notes")
    instrument_mock.maintenanceNotes.set.assert_called_with("test maintenance notes")
    instrument_mock.rosin.set.assert_called_with(True)
    instrument_mock.bow.set.assert_called_with(False)
    instrument_mock.ready.set.assert_called_with(True)
    instrument_mock.shoulderRestEndpinRest.set.assert_called_with(False)
    instrument_mock.gifted.set.assert_called_with(True)

    instrument_item.update.assert_called()
    instrument_item.save.assert_called()

    assert response["statusCode"] == 200


def test_unknown_key():
    """Test unknown key in request returns 400 bad request"""
    response = update.full(
        {"pathParameters": {"id": "fakeid"}, "body": json.dumps({"unknown": "fail"})},
        {},
    )

    assert response["statusCode"] == 400


def test_all_item_not_found(monkeypatch):
    """Test item not found error causes 404 not found"""

    def db_not_found(*args):
        raise InstrumentModel.DoesNotExist

    monkeypatch.setattr("app.update.InstrumentModel.get", db_not_found)

    response = update.full(
        {"body": json.dumps({"number": "1234"}), "pathParameters": {"id": "fakeid"}}, {}
    )

    assert response["statusCode"] == 404


def test_update_full_no_id():
    """test that not having an id in the path returns a bad request error"""
    response = update.full({"body": json.dumps({"instrumenttype": "violin"})}, {})

    assert response["statusCode"] == 400
