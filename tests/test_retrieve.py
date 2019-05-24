from unittest import mock

import retrieve


def test_retrieve_successful_no_history(monkeypatch, retrieve_event):
    """Test retrieving an instrument"""
    at_object_mock = mock.MagicMock()
    at_object_mock.search.return_value = [
        {
            "id": "recid",
            "fields": {
                "Number": "1-201",
                "Instrument Type": "violin",
                "Size": "4/4",
                "Location": "somewhere",
                "Assigned To": "Test Student",
            },
        }
    ]

    monkeypatch.setattr("retrieve.setup_airtable", lambda: at_object_mock)

    response = retrieve.single(retrieve_event, {})
    at_object_mock.search.assert_called_with("Number", "1-201")
    at_object_mock.update.assert_called_with(
        "recid", {"Location": "transit", "History": "Test Student", "Assigned To": ""}
    )

    assert response["statusCode"] == 200


def test_retrieve_successful_with_history(monkeypatch, retrieve_event):
    """Test retrieving an instrument"""
    at_object_mock = mock.MagicMock()
    at_object_mock.search.return_value = [
        {
            "id": "recid",
            "fields": {
                "Number": "1-201",
                "Instrument Type": "violin",
                "Size": "4/4",
                "Location": "somewhere",
                "Assigned To": "Test Student",
                "History": "Previous Student",
            },
        }
    ]

    monkeypatch.setattr("retrieve.setup_airtable", lambda: at_object_mock)

    response = retrieve.single(retrieve_event, {})
    at_object_mock.search.assert_called_with("Number", "1-201")
    at_object_mock.update.assert_called_with(
        "recid",
        {
            "Location": "transit",
            "History": "Previous Student, Test Student",
            "Assigned To": "",
        },
    )
    assert response["statusCode"] == 200


def test_retrieve_successful_without_assigned_to(monkeypatch, retrieve_event):
    """Test retrieving an instrument"""
    at_object_mock = mock.MagicMock()
    at_object_mock.update_by_field = mock.MagicMock()
    at_object_mock.search = mock.MagicMock()
    at_object_mock.search.return_value = [
        {
            "id": "recid",
            "fields": {
                "Number": "1-201",
                "Instrument Type": "violin",
                "Size": "4/4",
                "Location": "somewhere",
                "History": "Previous Student",
            },
        }
    ]

    monkeypatch.setattr("retrieve.setup_airtable", lambda: at_object_mock)

    response = retrieve.single(retrieve_event, {})
    at_object_mock.search.assert_called_with("Number", "1-201")
    at_object_mock.update.assert_called_with(
        "recid", {"Location": "transit", "Assigned To": ""}
    )

    assert response["statusCode"] == 200


def test_airtable_raises_error(monkeypatch, retrieve_event):
    """Test airtable raising an error"""

    def at_mock(*args, **kwargs):
        raise Exception

    monkeypatch.setattr("retrieve.setup_airtable", at_mock)

    response = retrieve.single(retrieve_event, {})

    assert response["statusCode"] == 500


def test_no_records_found(monkeypatch, retrieve_event):
    """Test error is returned when no records are found"""
    at_object_mock = mock.MagicMock()
    at_object_mock.search.return_value = []

    monkeypatch.setattr("retrieve.setup_airtable", lambda: at_object_mock)

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
    retrieve._retrieve_instrument("1-201", at)
    at.search.assert_called_once_with("Number", "1-201")
    at.update.assert_called_once_with(
        "recid",
        {
            "Location": "transit",
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
        "recid1", {"Location": "transit", "History": "Test Student", "Assigned To": ""}
    )
    at_object_mock.update.assert_any_call(
        "recid2", {"Location": "transit", "Assigned To": ""}
    )
    at_object_mock.update.assert_any_call(
        "recid3",
        {
            "Location": "transit",
            "History": "Previous Student, Test Student2",
            "Assigned To": "",
        },
    )
    at_object_mock.update.assert_any_call(
        "recid4",
        {
            "Location": "transit",
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
        "recid1", {"Location": "transit", "History": "Test Student", "Assigned To": ""}
    )
    at_object_mock.update.assert_any_call(
        "recid2", {"Location": "transit", "Assigned To": ""}
    )
    at_object_mock.update.assert_any_call(
        "recid4",
        {
            "Location": "transit",
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
