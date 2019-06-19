import json
from unittest import mock

import pytest

import search


def test_search_number_not_found(monkeypatch, search_number_event):
    """Test searching for an instrument number"""
    found = []
    at_mock = mock.MagicMock()
    at_mock.get_all.return_value = found
    monkeypatch.setattr("search.setup_airtable", lambda: at_mock)

    response = search.number(search_number_event, {})

    at_mock.get_all.assert_called_with(formula="{Number}='1-201'")

    assert response["statusCode"] == 404


def test_search_number_bad_request():
    """Test request missing data returns bad request"""
    response = search.number({"body": "{}"}, {})

    assert response["statusCode"] == 400


@pytest.mark.xfail
def test_search_assigned(monkeypatch, search_assigned_event, records):
    """Test searching for a student name"""
    found = [records[1], records[2], records[8]]
    at_mock = mock.MagicMock()
    at_mock.get_all.return_value = found
    monkeypatch.setattr("search.setup_airtable", lambda: at_mock)

    response = search.assigned(search_assigned_event, {})

    at_mock.get_all.assert_called_with(
        formula="SEARCH('test name', LOWER({Assigned To}))"
    )
    assert response["statusCode"] == 200
    assert response["body"] == json.dumps(found)


def test_search_assigned_bad_request():
    """Test searching for a name missing data returns bad request"""
    response = search.assigned({"body": "{}"}, {})

    assert response["statusCode"] == 400
