import json
from unittest import mock

import update


def test_add_photo(monkeypatch):
    """Test adding a photo"""
    at_mock = mock.MagicMock()
    monkeypatch.setattr("update.setup_airtable", lambda: at_mock)

    response = update.photo(
        {
            "body": json.dumps({"photoUrl": "http://example.com/image.jpg"}),
            "pathParameters": {"id": "recid"},
        },
        {},
    )

    at_mock.update.assert_called_with(
        "recid", {"Photo": [{"url": "http://example.com/image.jpg"}]}
    )

    assert response["statusCode"] == 200


def test_add_photo_no_id():
    """Test adding a photo with no record id fails"""
    response = update.photo(
        {"body": json.dumps({"photoUrl": "http://example.com/image.jpg"})}, {}
    )

    assert response["statusCode"] == 404


def test_add_photo_no_photo():
    """Test adding a photo with no photo url"""
    response = update.photo(
        {"body": json.dumps({}), "pathParameters": {"id": "recid"}}, {}
    )

    assert response["statusCode"] == 400
