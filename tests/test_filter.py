import json
from unittest import mock

import pytest

import filter


def _result_id_set(records):
    if isinstance(records, str):
        records = json.loads(records)
    return {rec["id"] for rec in records}


@pytest.mark.xfail
def test_filter_by_instrument(monkeypatch, records):
    """Test filtering by instrument type"""
    at_mock = mock.MagicMock()
    at_mock.get_all.return_value = records[0:2]

    monkeypatch.setattr("filter.setup_airtable", lambda: at_mock)

    event = {"body": json.dumps({"instrumentType": "violin"})}

    response = filter.main(event, {})

    at_mock.get_all.assert_called_with(formula="AND({Instrument Type}='violin')")

    assert _result_id_set(response["body"]) == _result_id_set(records[0:2])


@pytest.mark.xfail
def test_filter_by_size(monkeypatch, records):
    """Test filtering by instrument size"""
    at_mock = mock.MagicMock()
    at_mock.get_all.return_value = records[4:6]

    monkeypatch.setattr("filter.setup_airtable", lambda: at_mock)

    event = {"body": json.dumps({"size": "4/4"})}

    response = filter.main(event, {})

    at_mock.get_all.assert_called_with(formula="AND({Size}='4/4')")

    assert _result_id_set(response["body"]) == _result_id_set(records[4:6])


@pytest.mark.xfail
def test_filter_by_location(monkeypatch, records):
    """Test filtering by location"""
    at_mock = mock.MagicMock()
    at_mock.get_all.return_value = records[6:8]

    monkeypatch.setattr("filter.setup_airtable", lambda: at_mock)

    event = {"body": json.dumps({"location": "office"})}

    response = filter.main(event, {})

    at_mock.get_all.assert_called_with(formula="AND({Location}='office')")

    assert _result_id_set(response["body"]) == _result_id_set(records[6:8])


@pytest.mark.xfail
def test_filter_not_assigned(monkeypatch, records):
    """Test filtering by unassigned instruments"""
    at_mock = mock.MagicMock()
    at_mock.get_all.return_value = [records[9]]

    event = {"body": json.dumps({"notAssigned": True})}

    monkeypatch.setattr("filter.setup_airtable", lambda: at_mock)

    response = filter.main(event, {})

    at_mock.get_all.assert_called_with(formula="AND({Assigned To}='')")

    assert _result_id_set(response["body"]) == _result_id_set([records[9]])


@pytest.mark.xfail
def test_filter_multiple(monkeypatch, records):
    """Test filtering by multiple attributes"""
    at_mock = mock.MagicMock()
    at_mock.get_all.return_value = [records[7]]

    monkeypatch.setattr("filter.setup_airtable", lambda: at_mock)

    event = {
        "body": json.dumps(
            {"location": "office", "instrumentType": "violin", "size": "4/4"}
        )
    }

    response = filter.main(event, {})

    at_mock.get_all.assert_called_with(
        formula="AND({Instrument Type}='violin',{Size}='4/4',{Location}='office')"
    )

    assert _result_id_set(response["body"]) == _result_id_set([records[7]])


def test_filter_nothing_bad_request():
    """Test sending nothing is a bad request"""

    response = filter.main({"body": json.dumps({})}, {})

    assert response["statusCode"] == 400
