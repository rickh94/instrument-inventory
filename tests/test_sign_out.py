from unittest import mock

import sign_out


def test_sign_out_successful(monkeypatch, sign_out_event):
    """Test signing out an instrument"""
    at_object_mock = mock.MagicMock()

    def setup_airtable_mock():
        return at_object_mock

    monkeypatch.setattr("sign_out.setup_airtable", setup_airtable_mock)

    response = sign_out.main(sign_out_event, {})
    at_object_mock.update_by_field.assert_called_with(
        "Number",
        "1-201",
        {"Assigned To": "Test Student", "Location": "Grant Elementary School"},
    )

    assert response["statusCode"] == 200


def test_airtable_raises_error(monkeypatch, sign_out_event):
    """Test airtable raising an error"""

    def at_mock(*args, **kwargs):
        raise Exception

    monkeypatch.setattr("sign_out.setup_airtable", at_mock)

    response = sign_out.main(sign_out_event, {})

    assert response["statusCode"] == 500


def test_no_records_match(monkeypatch, sign_out_event):
    """Test error is returned when no records are found"""
    at_object_mock = mock.MagicMock()
    at_object_mock.update_by_field.return_value = {}

    def at_mock(*args, **kwargs):
        return at_object_mock

    monkeypatch.setattr("sign_out.setup_airtable", at_mock)

    response = sign_out.main(sign_out_event, {})

    assert response["statusCode"] == 500
