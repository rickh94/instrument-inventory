from unittest import mock

import ujson

from app import search


def _result_id_set(records):
    if isinstance(records, str):
        records = ujson.loads(records)

    def record_id(rec):
        if isinstance(rec, dict):
            return rec["id"]
        return rec.id

    return {record_id(rec) for rec in records}


def test_search_number(monkeypatch, records):
    """Test searching for an instrument number"""
    instrument_mock = mock.MagicMock()
    instrument_item = records[0]
    instrument_mock.scan.return_value = [instrument_item]
    monkeypatch.setattr("app.search.InstrumentModel", instrument_mock)

    response = search.number({"body": ujson.dumps({"term": "1-605"})}, {})

    instrument_mock.scan.assert_called()
    instrument_mock.number.__eq__.assert_called_with("1-605")

    assert response["statusCode"] == 200
    assert _result_id_set(response["body"]) == {instrument_item.id}


def test_search_number_not_found(monkeypatch, search_number_event):
    """Test searching for an instrument number"""
    instrument_mock = mock.MagicMock()
    instrument_mock.scan.return_value = []
    monkeypatch.setattr("app.search.InstrumentModel", instrument_mock)

    response = search.number(search_number_event, {})

    instrument_mock.scan.assert_called()

    assert response["statusCode"] == 404


def test_search_number_invalid():
    """Test request missing data returns bad request"""
    response = search.number({"body": "{}"}, {})

    assert response["statusCode"] == 422


def test_search_assigned(monkeypatch, search_assigned_event, records):
    """Test searching for a student name"""
    found = [records[1], records[2], records[8]]
    instrument_mock = mock.MagicMock()
    instrument_mock.scan.return_value = found
    monkeypatch.setattr("app.search.InstrumentModel", instrument_mock)

    response = search.assigned(search_assigned_event, {})

    instrument_mock.scan.assert_called()
    instrument_mock.assignedTo.contains.assert_called_with("Test Name")

    assert response["statusCode"] == 200
    assert _result_id_set(response["body"]) == _result_id_set(found)


def test_search_assigned_bad_request():
    """Test searching for a name missing data returns bad request"""
    response = search.assigned({"body": "{}"}, {})

    assert response["statusCode"] == 422


def test_search_history(monkeypatch, records):
    """Test searching for a name in an instrument's history"""
    found = [records[1], records[2], records[7]]
    instrument_mock = mock.MagicMock()
    instrument_mock.scan.return_value = found
    monkeypatch.setattr("app.search.InstrumentModel", instrument_mock)

    response = search.history({"body": ujson.dumps({"term": "Test Name"})}, {})
    instrument_mock.history.contains.assert_called_with("Test Name")

    assert response["statusCode"] == 200
    assert _result_id_set(response["body"]) == _result_id_set(found)


def test_search_history_invalid():
    """Test missing data is validation error"""
    response = search.history({"body": "{}"}, {})

    assert response["statusCode"] == 422


def test_search_history_and_assigned(monkeypatch, records):
    found = [records[1], records[2], records[4]]
    instrument_mock = mock.MagicMock()
    instrument_mock.scan.return_value = found
    monkeypatch.setattr("app.search.InstrumentModel", instrument_mock)

    response = search.history_and_assigned(
        {"body": ujson.dumps({"term": "Test Name"})}, {}
    )

    instrument_mock.history.contains.assert_called_with("Test Name")

    assert response["statusCode"] == 200
    assert _result_id_set(response["body"]) == _result_id_set(found)


def test_search_history_and_assigned_invalid():
    """Test missing data is validation error"""
    response = search.history({"body": "{}"}, {})

    assert response["statusCode"] == 422
