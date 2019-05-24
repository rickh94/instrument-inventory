import json
from unittest import mock

import pytest

import get


@pytest.fixture
def rec():
    return {
        "id": "reciMq9N5Ry5uNQgf",
        "fields": {
            "Number": "1-602",
            "Maintenance Notes": "test notes",
            "Photo": [
                {
                    "id": "att9fOcsfNqxUarbz",
                    "url": "https://dl.airtable.com/.attachments/4799cebc7824dd76dad75fb58726fdfd/47f73802/uqKyeMaaAOQ",
                    "filename": "uqKyeMaaAOQ",
                    "size": 155408,
                    "type": "text/html",
                }
            ],
            "Instrument Type": "violin",
            "Size": "4/4",
            "Location": "Grant Elementary School",
            "Ready To Go": True,
            "Condition": 5,
            "Assigned To": "Test Name",
            "Quality": 3,
            "Condition Notes": "test condition",
            "Rosin": True,
            "Bow": True,
            "Shoulder Rest/Endpin Rest": True,
            "Gifted to student": True,
        },
        "createdTime": "2019-05-24T02:34:47.000Z",
    }


def test_get_successful(monkeypatch, get_event, rec):
    """Test getting a single instrument"""
    at_mock = mock.MagicMock()
    at_mock.get.return_value = rec

    monkeypatch.setattr("get.setup_airtable", lambda: at_mock)

    response = get.main(get_event, {})

    assert response["statusCode"] == 200
    assert response["body"] == json.dumps(rec)


def test_get_missing_data():
    """Test missing data returns 400 bad request"""
    response = get.main({"pathParameters": {}}, {})

    assert response["statusCode"] == 404


def test_airtable_error(monkeypatch, get_event):
    """Test airtable error returns 500 server error"""

    def at_fail():
        raise Exception

    monkeypatch.setattr("get.setup_airtable", at_fail)

    response = get.main(get_event, {})

    assert response["statusCode"] == 500
