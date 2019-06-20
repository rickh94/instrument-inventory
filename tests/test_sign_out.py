from unittest import mock

from app import sign_out


def test_sign_out_successful(monkeypatch, sign_out_event, fake_instrument):
    """Test signing out an instrument"""
    instrument_mock = mock.MagicMock()
    instrument_item = fake_instrument(
        "fakeid", number="1-201", size="4/4", type="violin", location="office"
    )
    instrument_mock.scan.return_value = [instrument_item]
    monkeypatch.setattr("app.sign_out.InstrumentModel", instrument_mock)

    response = sign_out.main(sign_out_event, {})

    instrument_item.update.assert_called()
    instrument_item.save.assert_called()
    instrument_mock.assignedTo.set.assert_called_with("Test Student")
    instrument_mock.location.set.assert_called_with("Grant Elementary School")

    assert response["statusCode"] == 200


def test_sign_out_updates_history(monkeypatch, sign_out_event, fake_instrument):
    """Test signing out and instrument updates the history"""
    instrument_mock = mock.MagicMock()
    instrument_item = fake_instrument(
        "fakeid",
        number="1-201",
        size="4/4",
        type="violin",
        location="office",
        assignedTo="Previous Owner",
    )
    instrument_mock.scan.return_value = [instrument_item]
    monkeypatch.setattr("app.sign_out.InstrumentModel", instrument_mock)

    response = sign_out.main(sign_out_event, {})

    instrument_item.update.assert_called()
    instrument_item.save.assert_called()
    instrument_mock.assignedTo.set.assert_called_with("Test Student")
    instrument_mock.location.set.assert_called_with("Grant Elementary School")
    instrument_mock.history.add.assert_called_with({"Previous Owner"})

    assert response["statusCode"] == 200


def test_dynamo_raises_error(monkeypatch, sign_out_event):
    """Test airtable raising an error"""

    def db_mock(*args, **kwargs):
        raise Exception

    monkeypatch.setattr("app.sign_out.InstrumentModel.scan", db_mock)

    response = sign_out.main(sign_out_event, {})

    assert response["statusCode"] == 500


def test_no_records_match(monkeypatch, sign_out_event):
    """Test error is returned when no records are found"""
    instrument_mock = mock.MagicMock()
    instrument_mock.scan.return_value = []

    monkeypatch.setattr("app.sign_out.InstrumentModel", instrument_mock)

    response = sign_out.main(sign_out_event, {})

    assert response["statusCode"] == 404
