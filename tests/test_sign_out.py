import json
from unittest import mock

import sign_out


def test_sign_out_successful(monkeypatch, sign_out_event):
    """Test signing out an instrument"""
    at_object_mock = mock.MagicMock()
    at_object_mock.search.return_value = [
        {
            "id": "recid",
            "fields": {
                "Number": "1-201",
                "Location": "Storage",
                "Assigned To": "Test Previous",
                "Size": "4/4",
                "History": "Person from History",
            },
        }
    ]
    at_object_mock.update.return_value = {
        "id": "recid",
        "fields": {
            "Number": "1-201",
            "Location": "Grant Elementary School",
            "Assigned To": "Test Student",
            "History": "Person from History, Test Previous",
        },
    }

    def setup_airtable_mock():
        return at_object_mock

    monkeypatch.setattr("sign_out.setup_airtable", setup_airtable_mock)

    response = sign_out.main(sign_out_event, {})
    at_object_mock.update.assert_called_with(
        "recid",
        {
            "Location": "Grant Elementary School",
            "Assigned To": "Test Student",
            "History": "Person from History, Test Previous",
        },
    )
    # at_object_mock.update_by_field.assert_called_with(
    #     "Number",
    #     "1-201",
    #     {"Assigned To": "Test Student", "Location": "Grant Elementary School"},
    # )

    assert response["statusCode"] == 200
    assert json.loads(response["body"])["id"] == "recid"


def test_airtable_raises_error(monkeypatch, sign_out_event):
    """Test airtable raising an error"""

    def at_mock(*args, **kwargs):
        raise Exception

    monkeypatch.setattr("sign_out.setup_airtable", at_mock)

    response = sign_out.main(sign_out_event, {})

    assert response["statusCode"] == 500


def test_no_records_match(monkeypatch, sign_out_event):
    """Test error is returned when no records are found"""
    at_object_mock = mock.MagicMock()
    at_object_mock.update.return_value = {}

    def at_mock(*args, **kwargs):
        return at_object_mock

    monkeypatch.setattr("sign_out.setup_airtable", at_mock)

    response = sign_out.main(sign_out_event, {})

    assert response["statusCode"] == 400
