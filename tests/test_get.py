import json
from unittest import mock

import pytest

from app import get
from lib.models import InstrumentModel


def _result_id_set(records):
    if isinstance(records, str):
        records = json.loads(records)

    def record_id(rec):
        if isinstance(rec, dict):
            return rec["id"]
        return rec.id

    return {record_id(rec) for rec in records}


def test_get_successful(monkeypatch, get_event, fake_instrument):
    """Test getting a single instrument"""
    instrument_mock = mock.MagicMock()
    fake_record = fake_instrument(
        "fakeid",
        number="123",
        size="4/4",
        type="violin",
        location="office",
        photo="test-photo.jpg",
        history=json.dumps(["Old Owner"]),
    )
    instrument_mock.get.return_value = fake_record

    def fake_photo_url(photo_name):
        return {
            "thumbnail": f"http://fake/thumbnail-{photo_name}",
            "full": f"http://fake/{photo_name}",
        }

    monkeypatch.setattr("app.get.InstrumentModel", instrument_mock)
    monkeypatch.setattr("app.get.generate_photo_urls", fake_photo_url)

    response = get.main(get_event, {})

    assert response["statusCode"] == 200
    expected_result = {
        field: value for field, value in fake_record.attribute_values.items()
    }
    expected_result["history"] = ["Old Owner"]
    expected_result["photoUrls"] = {
        "thumbnail": "http://fake/thumbnail-test-photo.jpg",
        "full": "http://fake/test-photo.jpg",
    }
    assert response["body"] == json.dumps(expected_result)


def test_get_no_photo_successful(monkeypatch, get_event, fake_instrument):
    """Test getting a single instrument"""
    instrument_mock = mock.MagicMock()
    fake_record = fake_instrument(
        "fakeid", number="123", size="4/4", type="violin", location="office"
    )
    instrument_mock.get.return_value = fake_record

    def fake_photo_url(photo_name):
        return {
            "thumbnail": f"http://fake/thumbnail-{photo_name}",
            "full": f"http://fake/{photo_name}",
        }

    monkeypatch.setattr("app.get.InstrumentModel", instrument_mock)
    monkeypatch.setattr("app.get.generate_photo_urls", fake_photo_url)

    response = get.main(get_event, {})

    assert response["statusCode"] == 200
    expected_result = {
        field: value for field, value in fake_record.attribute_values.items()
    }
    expected_result["photoUrls"] = None
    assert response["body"] == json.dumps(expected_result)


def test_get_missing_data():
    """Test missing data returns 400 bad request"""
    response = get.main({"pathParameters": {}}, {})

    assert response["statusCode"] == 404


def test_not_found(monkeypatch, get_event):
    """Test 404 return on not found"""

    def db_not_found(*args):
        raise InstrumentModel.DoesNotExist

    monkeypatch.setattr("app.get.InstrumentModel.get", db_not_found)

    response = get.main(get_event, {})

    assert response["statusCode"] == 404


def test_dynamo_fail(monkeypatch, get_event):
    """Test dynamodb error returns 500 server error"""

    def db_fail():
        raise Exception

    monkeypatch.setattr("app.get.InstrumentModel", db_fail)

    response = get.main(get_event, {})

    assert response["statusCode"] == 500


def test_get_all(monkeypatch, records):
    """Test getting all instruments"""
    db_mock = mock.MagicMock()
    db_mock.scan.return_value = records
    monkeypatch.setattr("app.get.InstrumentModel", db_mock)

    response = get.all_({}, {})

    db_mock.scan.assert_called()

    assert _result_id_set(response["body"]) == _result_id_set(records)


def test_dynamo_error_all(monkeypatch):
    """Test getting all instruments dyanmodb error"""

    def db_fail():
        raise Exception

    monkeypatch.setattr("app.get.InstrumentModel.scan", db_fail)

    response = get.all_({}, {})

    assert response["statusCode"] == 500
