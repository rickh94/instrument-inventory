import ujson
from unittest import mock

from app import get


def _result_id_set(records):
    if isinstance(records, str):
        records = ujson.loads(records)

    def record_id(rec):
        if isinstance(rec, dict):
            return rec["id"]
        return rec.id

    return {record_id(rec) for rec in records}


def test_get_successful(monkeypatch, get_event, fake_instrument):
    """Test getting a single instrument"""
    instrument_mock = mock.MagicMock()
    fake_record = fake_instrument(
        "fakeid",
        number="123",
        size="4/4",
        type="Violin",
        location="Office",
        photo="test-photo.jpg",
        history=ujson.dumps(["Old Owner"]),
    )
    instrument_mock.get.return_value = fake_record

    def fake_photo_url(photo_name):
        return {
            "thumbnail": f"http://fake.com/thumbnail-{photo_name}",
            "full": f"http://fake.com/{photo_name}",
        }

    monkeypatch.setattr("app.get.InstrumentModel", instrument_mock)
    monkeypatch.setattr("app.get.generate_photo_urls", fake_photo_url)

    response = get.main(get_event, {})
    print(response["body"])

    assert response["statusCode"] == 200
    expected_result = {
        "id": "fakeid",
        "number": "123",
        "size": "4/4",
        "location": "Office",
        "photoUrls": {
            "thumbnail": "http://fake.com/thumbnail-test-photo.jpg",
            "full": "http://fake.com/test-photo.jpg",
        },
        "history": ["Old Owner"],
    }
    item = ujson.loads(response["body"])
    for k, v in expected_result.items():
        if isinstance(item[k], dict):
            assert item[k]["thumbnail"] == v["thumbnail"]
            assert item[k]["full"] == v["full"]
        else:
            assert item[k] == v


def test_get_no_photo_successful(monkeypatch, get_event, fake_instrument):
    """Test getting a single instrument"""
    instrument_mock = mock.MagicMock()
    fake_record = fake_instrument(
        "fakeid", number="123", size="4/4", type="Violin", location="Office"
    )
    instrument_mock.get.return_value = fake_record

    def fake_photo_url(photo_name):
        return {
            "thumbnail": f"http://fake/thumbnail-{photo_name}",
            "full": f"http://fake/{photo_name}",
        }

    monkeypatch.setattr("app.get.InstrumentModel", instrument_mock)
    monkeypatch.setattr("app.get.generate_photo_urls", fake_photo_url)

    response = get.main(get_event, {})

    print(response["body"])
    assert response["statusCode"] == 200
    expected_result = {
        "id": "fakeid",
        "photoUrls": None,
        "number": "123",
        "size": "4/4",
        "type": "Violin",
        "location": "Office",
    }
    item = ujson.loads(response["body"])
    for k, v in expected_result.items():
        assert item[k] == v


def test_get_missing_data():
    """Test missing data returns 400 bad request"""
    response = get.main({"pathParameters": {}}, {})

    assert response["statusCode"] == 400


def test_not_found(monkeypatch, get_event, db_not_found):
    """Test 404 return on not found"""
    monkeypatch.setattr("app.get.InstrumentModel.get", db_not_found)

    response = get.main(get_event, {})

    assert response["statusCode"] == 404


def test_dynamo_fail(monkeypatch, get_event, explode):
    """Test dynamodb error returns 500 server error"""
    monkeypatch.setattr("app.get.InstrumentModel", explode)

    response = get.main(get_event, {})

    assert response["statusCode"] == 500


def test_get_all(monkeypatch, records):
    """Test getting all instruments"""
    db_mock = mock.MagicMock()
    db_mock.scan.return_value = records
    monkeypatch.setattr("app.get.InstrumentModel", db_mock)

    response = get.all_({}, {})

    db_mock.scan.assert_called()
    instruments = ujson.loads(response["body"])["instruments"]

    assert _result_id_set(instruments) == _result_id_set(records)


def test_dynamo_error_all(monkeypatch, explode):
    """Test getting all instruments dynamodb error"""
    monkeypatch.setattr("app.get.InstrumentModel.scan", explode)

    response = get.all_({}, {})

    assert response["statusCode"] == 500
