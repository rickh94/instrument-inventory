from unittest import mock

import ujson

from app import update


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
            "body": ujson.dumps({"photoUrl": "http://example.com/image.jpg"}),
            "pathParameters": {"id": "fakeid"},
        },
        {},
    )

    handle_photo_mock.assert_called_with("http://example.com/image.jpg")

    instrument_mock.get.assert_called_with("fakeid")
    assert instrument_item.photo == "fake_photo.jpg"

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
            "body": ujson.dumps({"photoUrl": "http://example.com/image.jpg"}),
            "pathParameters": {"id": "fakeid"},
        },
        {},
    )

    handle_photo_mock.assert_called_with("http://example.com/image.jpg")
    delete_photo_mock.assert_called_with("old_photo.jpg")

    instrument_mock.get.assert_called_with("fakeid")
    assert instrument_item.photo == "fake_photo.jpg"

    instrument_item.save.assert_called()

    assert response["statusCode"] == 200


def test_item_not_found(monkeypatch, db_not_found):
    """Test item not found error causes 404 not found"""
    monkeypatch.setattr("app.update.InstrumentModel.get", db_not_found)

    response = update.photo(
        {
            "body": ujson.dumps({"photoUrl": "http://example.com/image.jpg"}),
            "pathParameters": {"id": "fakeid"},
        },
        {},
    )

    assert response["statusCode"] == 404


def test_add_photo_no_id():
    """Test adding a photo with no record id fails"""
    response = update.photo(
        {"body": ujson.dumps({"photoUrl": "http://example.com/image.jpg"})}, {}
    )

    assert response["statusCode"] == 400


def test_add_photo_no_photo():
    """Test adding a photo with no photo url"""
    response = update.photo(
        {"body": ujson.dumps({}), "pathParameters": {"id": "fakeid"}}, {}
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

    # noinspection PyTypeChecker
    response = update.full(
        {
            "pathParameters": {"id": "fakeid"},
            "body": ujson.dumps(
                {
                    "type": "Cello",
                    "number": "C1-502",
                    "size": "4/4",
                    "location": "Office",
                    "assignedTo": "Test Name",
                    "condition": 4,
                    "quality": "2",
                    "conditionNotes": "test condition notes",
                    "maintenanceNotes": "test maintenance notes",
                    "gifted": True,
                }
            ),
        },
        {},
    )

    assert response["statusCode"] == 200

    instrument_item.save.assert_called()

    assert instrument_item.type == "Cello"
    assert instrument_item.number == "C1-502"
    assert instrument_item.size == "4/4"
    assert instrument_item.location == "Office"
    assert instrument_item.assignedTo == "Test Name"
    assert instrument_item.condition == 4
    assert instrument_item.quality == 2
    assert instrument_item.conditionNotes == "test condition notes"
    assert instrument_item.maintenanceNotes == "test maintenance notes"
    assert instrument_item.gifted is True


def test_unknown_key():
    """Test unknown key in request returns 400 bad request"""
    # noinspection PyTypeChecker
    response = update.full(
        {"pathParameters": {"id": "fakeid"}, "body": ujson.dumps({"unknown": "fail"})},
        {},
    )

    assert response["statusCode"] == 422


def test_all_item_not_found(monkeypatch, db_not_found):
    """Test item not found error causes 404 not found"""

    monkeypatch.setattr("app.update.InstrumentModel.get", db_not_found)

    # noinspection PyTypeChecker
    response = update.full(
        {
            "body": ujson.dumps(
                {
                    "type": "Cello",
                    "number": "C1-502",
                    "size": "4/4",
                    "location": "Office",
                    "assignedTo": "Test Name",
                    "condition": 4,
                    "quality": "2",
                    "conditionNotes": "test condition notes",
                    "maintenanceNotes": "test maintenance notes",
                    "gifted": True,
                }
            ),
            "pathParameters": {"id": "fakeid"},
        },
        {},
    )

    assert response["statusCode"] == 404


def test_update_full_no_id():
    """test that not having an id in the path returns a bad request error"""
    # noinspection PyTypeChecker
    response = update.full(
        {
            "body": ujson.dumps(
                {
                    "type": "Cello",
                    "number": "C1-502",
                    "size": "4/4",
                    "location": "Office",
                    "assignedTo": "Test Name",
                    "condition": 4,
                    "quality": "2",
                    "conditionNotes": "test condition notes",
                    "maintenanceNotes": "test maintenance notes",
                    "gifted": True,
                }
            )
        },
        {},
    )

    assert response["statusCode"] == 400
