import json

from lib.common import validate_request, handle_photo, delete_photos, serialize_item
from lib.responses import failure, success
from lib.models import InstrumentModel
import pynamodb.exceptions


def photo(event, _context):
    """Change or add a photo"""
    data = json.loads(event["body"])
    err_response = validate_request(data, {"photoUrl": "Photo"})
    if err_response:
        return err_response
    try:
        id_ = event["pathParameters"]["id"]
    except KeyError:
        return failure("Record ID must be in url", 400)
    try:
        ins = InstrumentModel.get(id_)
        if ins.photo:
            delete_photos(ins.photo)
        ins.photo = handle_photo(data["photoUrl"])
        ins.save()
        return success({"message": "Photo successfully updated"})
    except pynamodb.exceptions.DoesNotExist as err:
        print(err)
        return failure("Could not find matching item", 404)
    except Exception as err:
        print(err)
        return failure(f"Something has gone wrong")


def full(event, _context):
    """Update a full record"""
    data = json.loads(event["body"])
    try:
        id_ = event["pathParameters"]["id"]
    except KeyError:
        return failure("Please supply id", 400)
    actions = []
    try:
        for key, value in data.items():
            if key in ["condition", "quality"] and value is not None:
                value = int(value)
            field = getattr(InstrumentModel, key)
            actions.append(field.set(value))
    except AttributeError as err:
        print(err)
        return failure("Unknown field in request", 400)
    try:
        ins = InstrumentModel.get(id_)
        ins.update(actions=actions)
        ins.save()
        return success({"message": "Update Successful", "item": serialize_item(ins)})
    except pynamodb.exceptions.DoesNotExist:
        return failure("Could not find matching item", 404)
    except Exception as err:
        print(err)
        return failure(f"Something has gone wrong")
