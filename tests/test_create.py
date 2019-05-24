import json
from unittest import mock

import create


def test_basic_create_successful(monkeypatch, basic_create_event):
    """Test a minimal create"""
    at_object_mock = mock.MagicMock()
    at_object_mock.insert.return_value = {
        "fields": {"test": "test", "Number": "1234"},
        "id": "newrecid",
    }

    def at_mock():
        return at_object_mock

    monkeypatch.setattr("create.setup_airtable", at_mock)

    response = create.main(basic_create_event, {})

    at_object_mock.insert.assert_called_with(
        {
            "Number": "1-601",
            "Instrument Type": "violin",
            "Size": "4/4",
            "Location": "office",
            "Maintenance Notes": "",
            "Assigned To": "",
            "Condition Notes": "",
            "Ready To Go": False,
            "Condition": None,
            "Quality": None,
            "Rosin": False,
            "Bow": False,
            "Shoulder Rest/Endpin Rest": False,
            "Gifted to student": False,
            "Photo": [],
        }
    )

    assert response["statusCode"] == 201


def test_full_create_successful(monkeypatch, full_create_event):
    """Test full create full"""
    at_object_mock = mock.MagicMock()
    at_object_mock.insert.return_value = {
        "fields": {"test": "test", "Number": "1234"},
        "id": "newrecid2",
    }

    def at_mock():
        return at_object_mock

    monkeypatch.setattr("create.setup_airtable", at_mock)

    response = create.main(full_create_event, {})

    at_object_mock.insert.assert_called_with(
        {
            "Number": "1-602",
            "Instrument Type": "violin",
            "Size": "4/4",
            "Location": "Grant Elementary School",
            "Maintenance Notes": "test notes",
            "Assigned To": "Test Name",
            "Condition Notes": "test condition",
            "Ready To Go": True,
            "Condition": 5,
            "Quality": 3,
            "Rosin": True,
            "Bow": True,
            "Shoulder Rest/Endpin Rest": True,
            "Gifted to student": True,
            "Photo": [
                {"url": "https://unsplash.com/photos/uqKyeMaaAOQ/download?force=true"}
            ],
        }
    )

    assert response["statusCode"] == 201


def test_airtable_raises_error(monkeypatch, basic_create_event):
    """Airtable raising an error returns server error"""

    def at_mock():
        raise Exception

    monkeypatch.setattr("create.setup_airtable", at_mock)

    response = create.main(basic_create_event, {})

    assert response["statusCode"] == 500


def test_incomplete_create(monkeypatch):
    """Error is returned if incomplete create"""
    incomplete_event = {"body": json.dumps({"instrumentNumber": "1-603"})}
    at_object_mock = mock.MagicMock()

    def at_mock():
        return at_object_mock

    monkeypatch.setattr("create.setup_airtable", at_mock)

    response = create.main(incomplete_event, {})

    assert response["statusCode"] == 400
