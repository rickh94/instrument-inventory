from unittest import mock

import ujson

from app import move


def test_move_multiple_successful(monkeypatch, records):
    """Test basic move multiple instruments"""
    instrument_mock = mock.MagicMock()
    instrument_mock.scan.return_value = records
    monkeypatch.setattr("app.move.InstrumentModel", instrument_mock)

    response = move.multiple(
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
                    ],
                    "location": "Westminster Presbyterian Church",
                }
            )
        },
        {},
    )

    for record in records:
        assert record.location == "Westminster Presbyterian Church"
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


def test_move_multiple_successful_different_location(monkeypatch, records):
    """Test basic move multiple instruments"""
    instrument_mock = mock.MagicMock()
    instrument_mock.scan.return_value = records
    monkeypatch.setattr("app.move.InstrumentModel", instrument_mock)

    response = move.multiple(
        {
            "body": ujson.dumps(
                {
                    "numbers": [
                        "1-605",
                        "1-601",
                        "V15-502",
                        "V15-503",
                        "B1-502",
                        "C2-508",
                        "2-606",
                    ],
                    "location": "Office",
                }
            )
        },
        {},
    )

    for record in records:
        assert record.location == "Office"
        record.save.assert_called()

    instrument_mock.number.is_in.assert_called_with(
        "1-605",
        "1-601",
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


def test_move_multiple_some_fail(monkeypatch, records):
    """Test moving multiple with some failures"""
    instrument_mock = mock.MagicMock()
    instrument_mock.scan.return_value = records
    monkeypatch.setattr("app.move.InstrumentModel", instrument_mock)

    response = move.multiple(
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
                    ],
                    "location": "Westminster Presbyterian Church",
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


def test_bad_request_multiple():
    """Test missing data returns validation error"""
    response = move.multiple({"body": "{}"}, {})

    assert response["statusCode"] == 422
