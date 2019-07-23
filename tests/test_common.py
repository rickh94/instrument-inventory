from unittest import mock

from app.utils import common


def test_generate_photo_urls(monkeypatch):
    """Test generating download urls for photo objects"""
    fake_s3_client = mock.MagicMock()
    monkeypatch.setenv("PHOTOS_BUCKET_NAME", "fake_bucket")

    def fake_generate_presigned_url(_method, Params=None, *_):
        assert Params["Bucket"] == "fake_bucket"
        return f"http://fake/{Params['Key']}"

    fake_s3_client.generate_presigned_url = fake_generate_presigned_url
    monkeypatch.setattr("boto3.client", lambda *args: fake_s3_client)
    photo_urls = common.generate_photo_urls("test.jpg")

    assert photo_urls["thumbnail"] == "http://fake/thumbnail-test.jpg"
    assert photo_urls["full"] == "http://fake/test.jpg"


def test_delete_photos(monkeypatch):
    mock_s3_client = mock.MagicMock()
    monkeypatch.setenv("PHOTOS_BUCKET_NAME", "fake_bucket")
    monkeypatch.setattr("boto3.client", lambda *args: mock_s3_client)

    common.delete_photos("fake_photo.jpg")

    mock_s3_client.delete_object.assert_any_call(
        Bucket="fake_bucket", Key="fake_photo.jpg"
    )
    mock_s3_client.delete_object.assert_any_call(
        Bucket="fake_bucket", Key="thumbnail-fake_photo.jpg"
    )
