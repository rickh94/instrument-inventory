import json
from unittest import mock

import update


def test_add_photo(monkeypatch):
    """Test adding a photo"""
    at_mock = mock.MagicMock()
    monkeypatch.setattr("update.setup_airtable", lambda: at_mock)

    response = update.photo(
        {
            "body": json.dumps({"photoUrl": "http://example.com/image.jpg"}),
            "pathParameters": {"id": "recid"},
        },
        {},
    )

    at_mock.update.assert_called_with(
        "recid", {"Photo": [{"url": "http://example.com/image.jpg"}]}
    )

    assert response["statusCode"] == 200


def test_add_photo_no_id():
    """Test adding a photo with no record id fails"""
    response = update.photo(
        {"body": json.dumps({"photoUrl": "http://example.com/image.jpg"})}, {}
    )

    assert response["statusCode"] == 400


def test_add_photo_no_photo():
    """Test adding a photo with no photo url"""
    response = update.photo(
        {"body": json.dumps({}), "pathParameters": {"id": "recid"}}, {}
    )

    assert response["statusCode"] == 400


def test_update_full_record(monkeypatch):
    """Test updating a record in full"""
    fields = {
        "Number": "1-610",
        "Instrument Type": "violin",
        "Maintenance Notes": "some new notes",
        "Location": "office",
    }
    at_mock = mock.MagicMock()
    at_mock.update.return_value = {"id": "recid", "fields": fields}
    monkeypatch.setattr("update.setup_airtable", lambda: at_mock)

    event = {
        "body": json.dumps(
            {
                "number": fields["Number"],
                "instrumentType": fields["Instrument Type"],
                "maintenanceNotes": fields["Maintenance Notes"],
            }
        ),
        "pathParameters": {"id": "recid"},
    }

    response = update.full(event, {})

    at_mock.update.assert_called_with(
        "recid",
        {
            "Number": fields["Number"],
            "Instrument Type": fields["Instrument Type"],
            "Maintenance Notes": fields["Maintenance Notes"],
        },
    )

    assert response["statusCode"] == 200
    assert response["body"] == json.dumps(
        {"message": "Update Successful", "item": {"id": "recid", "fields": fields}}
    )


def test_update_full_no_id():
    """Test that not having an id in the path returns a bad request error"""
    response = update.full({"body": json.dumps({"instrumentType": "violin"})}, {})

    assert response["statusCode"] == 400
