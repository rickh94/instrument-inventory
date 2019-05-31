import json

from common import setup_airtable, validate_request
from responses import failure, success


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
        rec_id = event["pathParameters"]["id"]
    except KeyError:
        return failure("Record ID must be in url", 400)
    try:
        at = setup_airtable()
        at.update(rec_id, {"Photo": [{"url": data["photoUrl"]}]})
        return success({"message": "Photo successfully updated"})
    except Exception as err:
        return failure(f"Something has gone wrong: {err}")


def full(event, _context):
    """Update a full record"""
    data = json.loads(event["body"])
    try:
        rec_id = event["pathParameters"]["id"]
    except KeyError:
        return failure("Please supply id", 400)
    fields = {}
    for key, value in data.items():
        if key in frontend_backend_field_names:
            fields[to_airtable_name(key)] = value
    print(fields)
    try:
        at = setup_airtable()
        updated = at.update(rec_id, fields, typecast=True)
        print(updated)
        return success({"message": "Update Successful", "item": updated})
    except Exception as err:
        return failure(f"Something has gone wrong: {err}")
