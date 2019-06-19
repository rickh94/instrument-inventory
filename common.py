import os
import uuid

import boto3
import requests
from PIL import Image

from airtable import Airtable, params

from responses import failure


def validate_request(body: dict, required_fields: dict):
    """Validate that a request has all required data"""
    for field_key, field_name in required_fields.items():
        if not body.get(field_key):
            return failure({"errors": {field_key: f"{field_name} is required."}}, 400)
    return None


def setup_airtable():
    base_key = os.environ.get("AIRTABLE_BASE_KEY")
    table_name = os.environ.get("TABLE_NAME")
    return Airtable(base_key, table_name)


def make_filter_formula(field, value):
    return params.AirtableParams.FormulaParam.from_name_and_value(field, value)


def add_to_history(new, history):
    """Add a new student to an instrument's history"""
    if not new:
        return None
    if not history:
        return new
    return f"{history}, {new}"


def move_instrument(instrument_number, at, assigned_to="", location="Storage"):
    """Perform the operations for retrieving an instrument
    :param instrument_number: The instrument to move
    :param at: airtable instance
    :param assigned_to: person to assign the instrument to
    :param location: where it is going
    """
    result = at.search("Number", instrument_number)[0]
    old_assigned_to = result["fields"].get("Assigned To", None)
    history = result["fields"].get("History", None)
    new_history = add_to_history(old_assigned_to, history)
    update = {"Location": location, "Assigned To": assigned_to}
    if new_history:
        update["History"] = new_history
    rec = at.update(result["id"], update)
    return rec


def handle_photo(url):
    s3 = boto3.client("s3")
    data = requests.get(url)
    photo_id = str(uuid.uuid4())
    with open(f"/tmp/{photo_id}", "wb") as thefile:
        thefile.write(data.content)
    # print(photo_id)
    im = Image.open(f"/tmp/{photo_id}")
    # print(im.format)
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
