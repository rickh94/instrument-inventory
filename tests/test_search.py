import json
from unittest import mock

import pytest

import search


def test_search_number(monkeypatch, records):
    """Test searching for an instrument number"""
    instrument_mock = mock.MagicMock()
    instrument_item = records[0]
    instrument_mock.scan.return_value = [instrument_item]
    monkeypatch.setattr("search.InstrumentModel", instrument_mock)

    response = search.number({"body": json.dumps({"instrumentNumber": "1-605"})}, {})

    instrument_mock.scan.assert_called()

    assert response["statusCode"] == 200
    assert response["body"] == json.dumps([instrument_item.attribute_values])


def test_search_number_not_found(monkeypatch, search_number_event):
    """Test searching for an instrument number"""
    instrument_mock = mock.MagicMock()
    instrument_mock.scan.return_value = []
    monkeypatch.setattr("search.InstrumentModel", instrument_mock)

    response = search.number(search_number_event, {})

    instrument_mock.scan.assert_called()

    assert response["statusCode"] == 404


def test_search_number_bad_request():
    """Test request missing data returns bad request"""
    response = search.number({"body": "{}"}, {})

    assert response["statusCode"] == 400


def test_search_assigned(monkeypatch, search_assigned_event, records):
    """Test searching for a student name"""
    found = [records[1], records[2], records[8]]
    instrument_mock = mock.MagicMock()
    instrument_mock.scan.return_value = found
    monkeypatch.setattr("search.InstrumentModel", instrument_mock)

    response = search.assigned(search_assigned_event, {})

    instrument_mock.scan.assert_called()

    assert response["statusCode"] == 200
    assert response["body"] == json.dumps([item.attribute_values for item in found])


def test_search_assigned_bad_request():
    """Test searching for a name missing data returns bad request"""
    response = search.assigned({"body": "{}"}, {})

    assert response["statusCode"] == 400
