import json

from common import setup_airtable, validate_request, handle_photo, delete_photos
from responses import failure, success
from models import InstrumentModel
import pynamodb.exceptions


frontend_backend_field_names = {
    "instrumentType": "Instrument Type",
    "number": "Number",
    "size": "Size",
    "location": "Location",
    "assignedTo": "Assigned To",
    "condition": "Condition",
    "quality": "Quality",
    "conditionNotes": "Condition Notes",
    "maintenanceNotes": "Maintenance Notes",
    "rosin": "Rosin",
    "bow": "Bow",
    "readyToGo": "Ready To Go",
    "shoulderRestEndpinRest": "Shoulder Rest/Endpin Rest",
    "giftedToStudent": "Gifted To Student",
}


def to_airtable_name(field_name):
    return frontend_backend_field_names[field_name]


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
        new_photo = handle_photo(data["photoUrl"])
        ins.update(actions=[InstrumentModel.photo.set(new_photo)])
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
        return success({"message": "Update Successful", "item": ins.attribute_values})
    except pynamodb.exceptions.DoesNotExist:
        return failure("Could not find matching item", 404)
    except Exception as err:
        print(err)
        return failure(f"Something has gone wrong")
