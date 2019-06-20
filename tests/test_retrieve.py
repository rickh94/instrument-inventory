import json
from unittest import mock

from app import retrieve


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

    monkeypatch.setattr("app.retrieve.InstrumentModel", instrument_mock)

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

    monkeypatch.setattr("app.retrieve.InstrumentModel", instrument_mock)

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

    monkeypatch.setattr("app.retrieve.InstrumentModel.scan", db_mock)

    response = retrieve.single(retrieve_event, {})

    assert response["statusCode"] == 500


def test_no_records_found(monkeypatch, retrieve_event):
    """Test error is returned when no records are found"""
    instrument_mock = mock.MagicMock()
    instrument_mock.scan.return_value = []

    monkeypatch.setattr("app.retrieve.InstrumentModel", instrument_mock)

    response = retrieve.single(retrieve_event, {})

    assert response["statusCode"] == 404


def test_retrieve_multiple_successful(monkeypatch, retrieve_multiple_event, records):
    """Test basic retrieve multiple instruments"""
    instrument_mock = mock.MagicMock()
    instrument_mock.scan.return_value = records
    monkeypatch.setattr("app.retrieve.InstrumentModel", instrument_mock)

    response = retrieve.multiple(
        {
            "body": json.dumps(
                {
                    "instrumentNumbers": [
                        "1-605",
                        "1-601",
                        "1-602",
                        "2-603",
                        "C1-505",
                        "V15-502",
                        "V15-503",
                        "B1-502",
                        "C2-508",
                        "2-606",
                    ]
                }
            )
        },
        {},
    )

    for record in records:
        record.update.assert_called()
        record.save.assert_called()
        if record.assignedTo:
            instrument_mock.history.add.assert_any_call({record.assignedTo})

    instrument_mock.number.is_in.assert_called_with(
        "1-605",
        "1-601",
        "1-602",
        "2-603",
        "C1-505",
        "V15-502",
        "V15-503",
        "B1-502",
        "C2-508",
        "2-606",
    )
    instrument_mock.assignedTo.set.assert_called_with(None)
    instrument_mock.location.set.assert_called_with("Storage")

    assert response["statusCode"] == 200
    assert response["body"] == json.dumps(
        {
            "instrumentsUpdated": [
                "1-605",
                "1-601",
                "1-602",
                "2-603",
                "C1-505",
                "V15-502",
                "V15-503",
                "B1-502",
                "C2-508",
                "2-606",
            ],
            "instrumentsFailed": [],
        }
    )


def test_retrieve_multiple_some_fail(monkeypatch, records):
    """Test retrieving multiple with some failures"""
    instrument_mock = mock.MagicMock()
    instrument_mock.scan.return_value = records
    monkeypatch.setattr("app.retrieve.InstrumentModel", instrument_mock)

    response = retrieve.multiple(
        {
            "body": json.dumps(
                {
                    "instrumentNumbers": [
                        "1-605",
                        "1-601",
                        "1-602",
                        "2-603",
                        "C1-505",
                        "V15-502",
                        "V15-503",
                        "B1-502",
                        "C2-508",
                        "2-606",
                        "1-003",
                    ]
                }
            )
        },
        {},
    )

    assert response["statusCode"] == 200
    assert response["body"] == json.dumps(
        {
            "instrumentsUpdated": [
                "1-605",
                "1-601",
                "1-602",
                "2-603",
                "C1-505",
                "V15-502",
                "V15-503",
                "B1-502",
                "C2-508",
                "2-606",
            ],
            "instrumentsFailed": ["1-003"],
        }
    )


def test_bad_request_single():
    """Test missing data returns bad request"""
    response = retrieve.single({"body": "{}"}, {})

    assert response["statusCode"] == 400


def test_bad_request_multiple():
    """Test missing data returns bad request"""
    response = retrieve.multiple({"body": "{}"}, {})

    assert response["statusCode"] == 400
