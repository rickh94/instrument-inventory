import ujson
import os
import urllib.request
import uuid

import boto3
from PIL import Image

from app.utils.responses import bad_request, success


def validate_request(body: dict, required_fields: dict):
    """Validate that a request has all required data"""
    for field_key, field_name in required_fields.items():
        if not body.get(field_key):
            return bad_request({"errors": {field_key: f"{field_name} is required."}})
    return None


def handle_photo(url):
    s3 = boto3.client("s3")
    res = urllib.request.urlopen(url)
    photo_id = str(uuid.uuid4())
    content = res.read()
    with open(f"/tmp/{photo_id}", "wb") as thefile:
        thefile.write(content)

    im = Image.open(f"/tmp/{photo_id}")
    im.thumbnail((128, 128))
    im.save(f"/tmp/thumbnail-{photo_id}.{im.format.lower()}")

    s3.put_object(
        Body=content,
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
    bucket = os.getenv("PHOTOS_BUCKET_NAME")
    s3.delete_object(Bucket=bucket, Key=photo_name)
    s3.delete_object(Bucket=bucket, Key=f"thumbnail-{photo_name}")


def serialize_item(item):
    item_values = item.attribute_values

    if item.history:
        item_values["history"] = ujson.loads(item.history)

    return item_values


def make_new_history(history, assigned_to):
    history_list = ujson.loads(history) if history else []
    history_list.append(assigned_to)
    return ujson.dumps(history_list)


class MissingValue(Exception):
    pass


def str_uuid():
    return str(uuid.uuid4())


def update_items(item_updates, update_func, db_model, api_model):
    results = {"updated": [], "failed": [], "updatedItems": []}
    for item in item_updates:
        found = list(db_model.query(item.id))
        if not found:
            results["failed"].append(item.id)
        found_item = found[0]
        found_item.count = update_func(found_item.count, item.amount)
        if found_item.count < 0:
            found_item.count = 0
        found_item.save()
        found_item.refresh()
        results["updated"].append(found_item.id)
        results["updatedItems"].append(
            api_model.parse_obj(found_item.attribute_values).dict()
        )
    return success(results)
