import ujson
from unittest import mock

import app.filter
from app import filter


def _result_id_set(records):
    if isinstance(records, str):
        records = ujson.loads(records)

    def record_id(rec):
        if isinstance(rec, dict):
            return rec["id"]
        return rec.id

    return {record_id(rec) for rec in records}


def test_filter_by_instrument(monkeypatch, records):
    """Test filtering by instrument type"""
    instrument_mock = mock.MagicMock()
    instrument_mock.scan.return_value = records[0:2]

    monkeypatch.setattr("app.filter.InstrumentModel", instrument_mock)

    event = {"body": ujson.dumps({"type": "Violin"})}

    response = filter.main(event, {})
    print(response["body"])
    assert response["statusCode"] == 200

    instrument_mock.scan.assert_called()

    assert _result_id_set(response["body"]) == _result_id_set(records[0:2])


def test_filter_by_size(monkeypatch, records):
    """Test filtering by instrument size"""
    instrument_mock = mock.MagicMock()
    instrument_mock.scan.return_value = records[4:6]

    monkeypatch.setattr("app.filter.InstrumentModel", instrument_mock)

    event = {"body": ujson.dumps({"size": "4/4"})}

    response = filter.main(event, {})

    instrument_mock.scan.assert_called()

    assert _result_id_set(response["body"]) == _result_id_set(records[4:6])


def test_filter_by_location(monkeypatch, records):
    """Test filtering by location"""
    instrument_mock = mock.MagicMock()
    instrument_mock.scan.return_value = records[6:8]

    monkeypatch.setattr("app.filter.InstrumentModel", instrument_mock)

    event = {"body": ujson.dumps({"location": "Office"})}

    response = filter.main(event, {})
    print(response["body"])
    assert response["statusCode"] == 200

    instrument_mock.scan.assert_called()

    assert _result_id_set(response["body"]) == _result_id_set(records[6:8])


def test_filter_not_assigned(monkeypatch, records):
    """Test filtering by unassigned instruments"""
    instrument_mock = mock.MagicMock()
    instrument_mock.scan.return_value = [records[9]]

    event = {"body": ujson.dumps({"notAssigned": True})}

    monkeypatch.setattr("app.filter.InstrumentModel", instrument_mock)

    response = filter.main(event, {})
    print(response["body"])
    assert response["statusCode"] == 200

    instrument_mock.assignedTo.does_not_exist.assert_called()
    instrument_mock.scan.assert_called()

    assert _result_id_set(response["body"]) == _result_id_set([records[9]])


def test_filter_multiple(monkeypatch, records):
    """Test filtering by multiple attributes"""
    instrument_mock = mock.MagicMock()
    instrument_mock.scan.return_value = [records[7]]

    monkeypatch.setattr("app.filter.InstrumentModel", instrument_mock)

    event = {
        "body": ujson.dumps({"location": "Office", "type": "Violin", "size": "4/4"})
    }

    response = filter.main(event, {})

    instrument_mock.scan.assert_called()

    assert _result_id_set(response["body"]) == _result_id_set([records[7]])


def test_filter_nothing_bad_request():
    """Test sending nothing is a validation error"""

    response = filter.main({"body": ujson.dumps({})}, {})

    assert response["statusCode"] == 422


def test_filter_signed_out_instruments(monkeypatch, records):
    """Test searching for instruments that haven't been returned"""
    found = records[2:8]
    instrument_mock = mock.MagicMock()
    instrument_mock.scan.return_value = found
    monkeypatch.setattr("app.filter.InstrumentModel", instrument_mock)

    response = app.filter.signed_out({}, {})

    instrument_mock.assignedTo.exists.assert_called()
    # instrument_mock.gifted.__eq__.assert_called_with(False)

    assert response["statusCode"] == 200
    assert _result_id_set(response["body"]) == _result_id_set(found)


def test_filter_signed_out_dynamo_error(monkeypatch, explode):
    """Test search signed_out encounters dynamodb error"""
    monkeypatch.setattr("app.filter.InstrumentModel.scan", explode)

    response = app.filter.signed_out({}, {})

    assert response["statusCode"] == 500


def test_filter_gifted_instruments(monkeypatch, records):
    """Test searching for instruments that haven't been returned"""
    found = records[4:9]
    instrument_mock = mock.MagicMock()
    instrument_mock.scan.return_value = found
    monkeypatch.setattr("app.filter.InstrumentModel", instrument_mock)

    response = app.filter.gifted({}, {})

    instrument_mock.gifted.__eq__.assert_called_with(True)

    assert response["statusCode"] == 200
    assert _result_id_set(response["body"]) == _result_id_set(found)


def test_filter_gifted_dynamo_error(monkeypatch, explode):
    """Test search signed_out encounters dynamodb error"""
    monkeypatch.setattr("app.filter.InstrumentModel.scan", explode)

    response = app.filter.gifted({}, {})

    assert response["statusCode"] == 500
