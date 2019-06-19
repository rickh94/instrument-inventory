import json
from unittest import mock

import common
import retrieve


def test_retrieve_successful(monkeypatch, retrieve_event, fake_instrument):
    """Test retrieving an instrument"""
    instrument_mock = mock.MagicMock()
    instrument_item = fake_instrument(
        "fakeid",
        number="1-201",
        type="violin",
        size="4/4",
        location="Grant Elementary School",
        assignedTo="Test Student",
    )
    instrument_mock.scan.return_value = [instrument_item]

    monkeypatch.setattr("retrieve.InstrumentModel", instrument_mock)

    response = retrieve.single(retrieve_event, {})

    instrument_item.update.assert_called()
    instrument_item.save.assert_called()
    instrument_mock.assignedTo.set.assert_called_with(None)
    instrument_mock.location.set.assert_called_with("Storage")
    instrument_mock.history.add.assert_called_with({"Test Student"})

    assert response["statusCode"] == 200
    assert json.loads(response["body"])["id"] == "fakeid"


def test_retrieve_successful_without_assigned_to(
    monkeypatch, retrieve_event, fake_instrument
):
    """Test retrieving an instrument"""
    instrument_mock = mock.MagicMock()
    instrument_item = fake_instrument(
        "fakeid",
        number="1-201",
        type="violin",
        size="4/4",
        location="Grant Elementary School",
    )
    instrument_mock.scan.return_value = [instrument_item]

    monkeypatch.setattr("retrieve.InstrumentModel", instrument_mock)

    response = retrieve.single(retrieve_event, {})

    instrument_item.update.assert_called()
    instrument_item.save.assert_called()
    instrument_mock.assignedTo.set.assert_called_with(None)
    instrument_mock.location.set.assert_called_with("Storage")
    instrument_mock.history.add.assert_not_called()

    assert response["statusCode"] == 200
    assert json.loads(response["body"])["id"] == "fakeid"


def test_dynamo_raises_error(monkeypatch, retrieve_event):
    """Test airtable raising an error"""

    def db_mock(*args, **kwargs):
        raise Exception

    monkeypatch.setattr("retrieve.setup_airtable", db_mock)

    response = retrieve.single(retrieve_event, {})

    assert response["statusCode"] == 500


def test_no_records_found(monkeypatch, retrieve_event):
    """Test error is returned when no records are found"""
    instrument_mock = mock.MagicMock()
    instrument_mock.scan.return_value = []

    monkeypatch.setattr("retrieve.InstrumentModel", instrument_mock)

    response = retrieve.single(retrieve_event, {})

    assert response["statusCode"] == 404


def test_retrieve_instrument_helper():
    """Test the helper function"""
    at = mock.MagicMock()
    at.search = mock.MagicMock()
    at.search.return_value = [
        {
            "id": "recid",
            "fields": {
                "Number": "1-201",
                "Instrument Type": "violin",
                "Size": "4/4",
                "Location": "somewhere",
                "Assigned To": "Some Student",
                "History": "Previous Student",
            },
        }
    ]
    at.update = mock.MagicMock()
    common.move_instrument("1-201", at)
    at.search.assert_called_once_with("Number", "1-201")
    at.update.assert_called_once_with(
        "recid",
        {
            "Location": "Storage",
            "Assigned To": "",
            "History": "Previous Student, Some Student",
        },
    )


def test_retrieve_multiple_successful(monkeypatch, retrieve_multiple_event):
    """Test basic retrieve multiple instruments"""
    at_object_mock = mock.MagicMock()
    at_object_mock.update_by_field = mock.MagicMock()
    at_object_mock.search = mock.MagicMock()
    at_object_mock.search.side_effect = [
        [
            {
                "id": "recid1",
                "fields": {
                    "Number": "1-001",
                    "Instrument Type": "violin",
                    "Size": "4/4",
                    "Location": "somewhere",
                    "Assigned To": "Test Student",
                },
            }
        ],
        [
            {
                "id": "recid2",
                "fields": {
                    "Number": "1-002",
                    "Instrument Type": "violin",
                    "Size": "4/4",
                    "Location": "somewhere",
                    "History": "Previous Student",
                },
            }
        ],
        [
            {
                "id": "recid3",
                "fields": {
                    "Number": "1-003",
                    "Instrument Type": "violin",
                    "Size": "4/4",
                    "Location": "somewhere",
                    "Assigned To": "Test Student2",
                    "History": "Previous Student",
                },
            }
        ],
        [
            {
                "id": "recid4",
                "fields": {
                    "Number": "1-004",
                    "Instrument Type": "violin",
                    "Size": "4/4",
                    "Location": "somewhere",
                    "Assigned To": "Test Student",
                    "History": "Previous Student4",
                },
            }
        ],
    ]

    monkeypatch.setattr("retrieve.setup_airtable", lambda: at_object_mock)

    response = retrieve.multiple(retrieve_multiple_event, {})
    at_object_mock.search.assert_any_call("Number", "1-001")
    at_object_mock.search.assert_any_call("Number", "1-002")
    at_object_mock.search.assert_any_call("Number", "1-003")
    at_object_mock.search.assert_any_call("Number", "1-004")
    at_object_mock.update.assert_any_call(
        "recid1", {"Location": "Storage", "History": "Test Student", "Assigned To": ""}
    )
    at_object_mock.update.assert_any_call(
        "recid2", {"Location": "Storage", "Assigned To": ""}
    )
    at_object_mock.update.assert_any_call(
        "recid3",
        {
            "Location": "Storage",
            "History": "Previous Student, Test Student2",
            "Assigned To": "",
        },
    )
    at_object_mock.update.assert_any_call(
        "recid4",
        {
            "Location": "Storage",
            "History": "Previous Student4, Test Student",
            "Assigned To": "",
        },
    )

    assert response["statusCode"] == 200
    assert response["body"] == (
        "{"
        '"instrumentsUpdated": '
        '["1-001", "1-002", "1-003", "1-004"], '
        '"instrumentsFailed": []'
        "}"
    )


def test_retrieve_multiple_some_fail(monkeypatch, retrieve_multiple_event):
    """Test retrieving multiple with some failures"""
    at_object_mock = mock.MagicMock()
    at_object_mock.update_by_field = mock.MagicMock()
    at_object_mock.search = mock.MagicMock()
    at_object_mock.search.side_effect = [
        [
            {
                "id": "recid1",
                "fields": {
                    "Number": "1-001",
                    "Instrument Type": "violin",
                    "Size": "4/4",
                    "Location": "somewhere",
                    "Assigned To": "Test Student",
                },
            }
        ],
        [
            {
                "id": "recid2",
                "fields": {
                    "Number": "1-002",
                    "Instrument Type": "violin",
                    "Size": "4/4",
                    "Location": "somewhere",
                    "History": "Previous Student",
                },
            }
        ],
        [],
        [
            {
                "id": "recid4",
                "fields": {
                    "Number": "1-004",
                    "Instrument Type": "violin",
                    "Size": "4/4",
                    "Location": "somewhere",
                    "Assigned To": "Test Student",
                    "History": "Previous Student4",
                },
            }
        ],
    ]

    monkeypatch.setattr("retrieve.setup_airtable", lambda: at_object_mock)

    response = retrieve.multiple(retrieve_multiple_event, {})
    at_object_mock.search.assert_any_call("Number", "1-001")
    at_object_mock.search.assert_any_call("Number", "1-002")
    at_object_mock.search.assert_any_call("Number", "1-003")
    at_object_mock.search.assert_any_call("Number", "1-004")
    at_object_mock.update.assert_any_call(
        "recid1", {"Location": "Storage", "History": "Test Student", "Assigned To": ""}
    )
    at_object_mock.update.assert_any_call(
        "recid2", {"Location": "Storage", "Assigned To": ""}
    )
    at_object_mock.update.assert_any_call(
        "recid4",
        {
            "Location": "Storage",
            "History": "Previous Student4, Test Student",
            "Assigned To": "",
        },
    )

    assert response["statusCode"] == 200
    assert response["body"] == (
        "{"
        '"instrumentsUpdated": ["1-001", "1-002", "1-004"], '
        '"instrumentsFailed": ['
        '{"number": "1-003", "error": "Could not find instrument"}'
        "]"
        "}"
    )


def test_bad_request_single():
    """Test missing data returns bad request"""
    response = retrieve.single({"body": "{}"}, {})

    assert response["statusCode"] == 400


def test_bad_request_multiple():
    """Test missing data returns bad request"""
    response = retrieve.multiple({"body": "{}"}, {})

    assert response["statusCode"] == 400
