from unittest import mock

import ujson

from app import retrieve


def test_retrieve_successful(monkeypatch, retrieve_event, fake_instrument):
    """Test retrieving an instrument"""
    instrument_mock = mock.MagicMock()
    instrument_item = fake_instrument(
        "fakeid",
        number="1-201",
        type="Violin",
        size="4/4",
        location="Grant Elementary School",
        assignedTo="Test Student",
    )
    instrument_mock.scan.return_value = [instrument_item]

    monkeypatch.setattr("app.retrieve.InstrumentModel", instrument_mock)

    response = retrieve.single(retrieve_event, {})
    print(response)

    assert response["statusCode"] == 200

    assert instrument_item.assignedTo is None
    assert instrument_item.location == "Storage"
    assert instrument_item.history == ujson.dumps(["Test Student"])
    instrument_item.save.assert_called()

    assert ujson.loads(response["body"])["id"] == "fakeid"


def test_retrieve_successful_gifted(monkeypatch, retrieve_event, fake_instrument):
    """Test retrieving an instrument"""
    instrument_mock = mock.MagicMock()
    instrument_item = fake_instrument(
        "fakeid",
        number="1-201",
        type="Violin",
        size="4/4",
        location="Grant Elementary School",
        assignedTo="Test Student",
        gifted=True,
    )
    instrument_mock.scan.return_value = [instrument_item]

    monkeypatch.setattr("app.retrieve.InstrumentModel", instrument_mock)

    response = retrieve.single(retrieve_event, {})
    print(response)

    assert response["statusCode"] == 200

    assert instrument_item.assignedTo is None
    assert instrument_item.location == "Storage"
    assert instrument_item.gifted is False
    assert instrument_item.history == ujson.dumps(["Test Student"])
    instrument_item.save.assert_called()

    assert ujson.loads(response["body"])["id"] == "fakeid"


def test_retrieve_successful_without_assigned_to(
    monkeypatch, retrieve_event, fake_instrument
):
    """Test retrieving an instrument"""
    instrument_mock = mock.MagicMock()
    instrument_item = fake_instrument(
        "fakeid",
        number="1-201",
        type="Violin",
        size="4/4",
        location="Grant Elementary School",
    )
    instrument_mock.scan.return_value = [instrument_item]

    monkeypatch.setattr("app.retrieve.InstrumentModel", instrument_mock)

    response = retrieve.single(retrieve_event, {})

    assert instrument_item.assignedTo is None
    assert instrument_item.location == "Storage"
    assert instrument_item.history is None
    instrument_item.save.assert_called()
    print(response)

    assert response["statusCode"] == 200
    assert ujson.loads(response["body"])["id"] == "fakeid"


def test_dynamo_raises_error(monkeypatch, retrieve_event, explode):
    """Test dynamodb raising an error"""
    monkeypatch.setattr("app.retrieve.InstrumentModel.scan", explode)

    response = retrieve.single(retrieve_event, {})

    assert response["statusCode"] == 500


def test_no_records_found(monkeypatch, retrieve_event):
    """Test error is returned when no records are found"""
    instrument_mock = mock.MagicMock()
    instrument_mock.scan.return_value = []

    monkeypatch.setattr("app.retrieve.InstrumentModel", instrument_mock)

    response = retrieve.single(retrieve_event, {})

    assert response["statusCode"] == 404


def test_retrieve_multiple_successful(monkeypatch, records):
    """Test basic retrieve multiple instruments"""
    instrument_mock = mock.MagicMock()
    instrument_mock.scan.return_value = records
    monkeypatch.setattr("app.retrieve.InstrumentModel", instrument_mock)

    response = retrieve.multiple(
        {
            "body": ujson.dumps(
                {
                    "numbers": [
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
        assert record.assignedTo is None
        assert record.location == "Storage"
        record.save.assert_called()

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

    assert response["statusCode"] == 200
    assert response["body"] == ujson.dumps(
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
            "body": ujson.dumps(
                {
                    "numbers": [
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
    assert response["body"] == ujson.dumps(
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
    """Test missing data returns validation error"""
    response = retrieve.single({"body": "{}"}, {})

    assert response["statusCode"] == 422


def test_bad_request_multiple():
    """Test missing data returns validation error"""
    response = retrieve.multiple({"body": "{}"}, {})

    assert response["statusCode"] == 422
