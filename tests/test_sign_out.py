from unittest import mock

from app import sign_out


def test_sign_out_successful(monkeypatch, sign_out_event, fake_instrument):
    """Test signing out an instrument"""
    instrument_mock = mock.MagicMock()
    instrument_item = fake_instrument(
        "fakeid", number="1-201", size="4/4", type="Violin", location="Office"
    )
    instrument_mock.scan.return_value = [instrument_item]
    monkeypatch.setattr("app.sign_out.InstrumentModel", instrument_mock)

    response = sign_out.main(sign_out_event, {})

    assert response["statusCode"] == 200

    instrument_mock.number.__eq__.assert_called_with("1-201")

    assert instrument_item.assignedTo == "Test Student"
    assert instrument_item.location == "Grant Elementary School"

    instrument_item.save.assert_called()
    instrument_item.refresh.assert_called()


def test_sign_out_updates_history(monkeypatch, sign_out_event, fake_instrument):
    """Test signing out and instrument updates the history"""
    instrument_mock = mock.MagicMock()
    instrument_item = fake_instrument(
        "fakeid",
        number="1-201",
        size="4/4",
        type="Violin",
        location="Office",
        assignedTo="Previous Owner",
    )
    instrument_mock.scan.return_value = [instrument_item]
    monkeypatch.setattr("app.sign_out.InstrumentModel", instrument_mock)

    response = sign_out.main(sign_out_event, {})

    instrument_mock.number.__eq__.assert_called_with("1-201")

    assert instrument_item.assignedTo == "Test Student"
    assert instrument_item.location == "Grant Elementary School"
    assert "Previous Owner" in instrument_item.history

    instrument_item.save.assert_called()
    instrument_item.refresh.assert_called()

    assert response["statusCode"] == 200


def test_sign_out_multiple_successful(
    monkeypatch, sign_out_multiple_event, fake_instrument
):
    """Test signing out multiple instruments"""
    instrument_mock = mock.MagicMock()
    ins1 = fake_instrument(
        "fakeid",
        number="1-201",
        size="4/4",
        type="violin",
        location="office",
        assignedTo="Previous Owner",
    )
    ins2 = fake_instrument(
        "fakeid2",
        number="1-204",
        size="4/4",
        type="violin",
        location="office",
        assignedTo="Previous Owner",
    )

    def _fake_equal(_self, number):
        return number

    def _fake_scan(number):
        if number == "1-201":
            return [ins1]
        if number == "1-204":
            return [ins2]

    instrument_mock.number.__eq__ = _fake_equal
    instrument_mock.scan = _fake_scan
    monkeypatch.setattr("app.sign_out.InstrumentModel", instrument_mock)

    response = sign_out.multiple(sign_out_multiple_event, {})

    assert response["statusCode"] == 200

    assert ins1.assignedTo == "Test Student"
    assert ins1.location == "Grant Elementary School"

    assert ins2.assignedTo == "Test Student2"
    assert ins2.location == "SproutU"


def test_dynamo_raises_error(monkeypatch, sign_out_event):
    """Test airtable raising an error"""

    def db_mock(*_a, **_k):
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

    instrument_mock.number.__eq__.assert_called_with("1-201")

    assert response["statusCode"] == 404
