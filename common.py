import os
import uuid

import boto3
import requests
from PIL import Image

from airtable import Airtable

from responses import bad_request


def validate_request(body: dict, required_fields: dict):
    """Validate that a request has all required data"""
    for field_key, field_name in required_fields.items():
        if not body.get(field_key):
            return bad_request({"errors": {field_key: f"{field_name} is required."}})
    return None


def setup_airtable():
    base_key = os.environ.get("AIRTABLE_BASE_KEY")
    table_name = os.environ.get("TABLE_NAME")
    return Airtable(base_key, table_name)


def handle_photo(url):
    s3 = boto3.client("s3")
    data = requests.get(url)
    photo_id = str(uuid.uuid4())
    with open(f"/tmp/{photo_id}", "wb") as thefile:
        thefile.write(data.content)

    im = Image.open(f"/tmp/{photo_id}")
    im.thumbnail((128, 128))
    im.save(f"/tmp/thumbnail-{photo_id}.{im.format.lower()}")
    s3.put_object(
        Body=data.content,
        Bucket=os.environ.get("PHOTOS_BUCKET_NAME"),
        Key=f"{photo_id}.{im.format.lower()}",
    )
    s3.upload_file(
        f"/tmp/thumbnail-{photo_id}.{im.format.lower()}",
        Key=f"thumbnail-{photo_id}.{im.format.lower()}",
        Bucket=os.environ.get("PHOTOS_BUCKET_NAME"),
    )

    return f"{photo_id}.{im.format.lower()}"


def generate_photo_urls(photo_name):
    s3 = boto3.client("s3")
    bucket = os.environ["PHOTOS_BUCKET_NAME"]
    return {
        "thumbnail": s3.generate_presigned_url(
            "get_object", Params={"Key": f"thumbnail-{photo_name}", "Bucket": bucket}
        ),
        "full": s3.generate_presigned_url(
            "get_object", Params={"Key": f"{photo_name}", "Bucket": bucket}
        ),
    }


def delete_photos(photo_name):
    s3 = boto3.client("s3")
    bucket = os.environ["PHOTOS_BUCKET_NAME"]
    s3.delete_object(Bucket=bucket, Key=photo_name)
    s3.delete_object(Bucket=bucket, Key=f"thumbnail-{photo_name}")
