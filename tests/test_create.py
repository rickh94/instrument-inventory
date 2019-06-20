import json
from unittest import mock

from app import create


def test_basic_create_successful(monkeypatch, basic_create_event, fake_uuid):
    """Test a minimal create"""
    instrument_mock = mock.MagicMock()
    created_item = mock.MagicMock()
    created_item.attribute_values = {"id": "fakeuuid"}
    created_item.number = "1-601"
    created_item.id = "fakeuuid"
    instrument_mock.return_value = created_item

    monkeypatch.setattr("app.create.InstrumentModel", instrument_mock)
    monkeypatch.setattr("uuid.uuid4", fake_uuid)

    response = create.main(basic_create_event, {})

    instrument_mock.assert_called_with(
        "fakeuuid",
        number="1-601",
        type="violin",
        size="4/4",
        location="office",
        assignedTo=None,
        maintenanceNotes=None,
        conditionNotes=None,
        ready=False,
        condition=None,
        quality=None,
        rosin=False,
        bow=False,
        shoulderRestEndpinRest=False,
        gifted=False,
        photo=None,
    )

    created_item.save.assert_called()

    assert response["statusCode"] == 201


def test_full_create_successful(monkeypatch, full_create_event, fake_uuid):
    """Test full create full"""
    instrument_mock = mock.MagicMock()
    created_item = mock.MagicMock()
    created_item.attribute_values = {"id": "fakeuuid"}
    created_item.number = "1-602"
    created_item.id = "fakeuuid"
    instrument_mock.return_value = created_item
    handle_photo_mock = mock.MagicMock()
    handle_photo_mock.return_value = "fake_photo.jpg"

    monkeypatch.setattr("app.create.InstrumentModel", instrument_mock)
    monkeypatch.setattr("uuid.uuid4", fake_uuid)
    monkeypatch.setattr("app.create.handle_photo", handle_photo_mock)

    response = create.main(full_create_event, {})

    handle_photo_mock.assert_called_with(
        "https://unsplash.com/photos/uqKyeMaaAOQ/download?force=true"
    )
    instrument_mock.assert_called_with(
        "fakeuuid",
        number="1-602",
        type="violin",
        size="4/4",
        location="Grant Elementary School",
        assignedTo="Test Name",
        maintenanceNotes="test notes",
        conditionNotes="test condition",
        ready=True,
        condition=5,
        quality=3,
        rosin=True,
        bow=True,
        shoulderRestEndpinRest=True,
        gifted=True,
        photo="fake_photo.jpg",
    )

    created_item.save.assert_called()

    assert response["statusCode"] == 201


def test_dynamodb_raises_error(monkeypatch, basic_create_event):
    """Airtable raising an error returns server error"""

    def db_mock():
        raise Exception

    monkeypatch.setattr("app.create.InstrumentModel", db_mock)

    response = create.main(basic_create_event, {})

    assert response["statusCode"] == 500


def test_incomplete_create(monkeypatch):
    """Error is returned if incomplete create"""
    incomplete_event = {"body": json.dumps({"instrumentNumber": "1-603"})}

    response = create.main(incomplete_event, {})

    assert response["statusCode"] == 400
