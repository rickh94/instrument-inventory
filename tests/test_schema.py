import json

from app import schema


def test_get_schema():
    """Test that schema returns valid json."""
    response = schema.main()

    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert "info" in body
    assert "components" in body
    assert "schemas" in body["components"]
    assert "Instrument" in body["components"]["schemas"]
