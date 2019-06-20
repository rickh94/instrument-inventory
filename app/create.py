import json
import uuid


from lib.common import validate_request, handle_photo, serialize_item
from lib.responses import failure, success
from lib.models import InstrumentModel


def main(event, _context):
    """Create a new instrument"""
    data = json.loads(event["body"])
    err_response = validate_request(
        body=data,
        required_fields={
            "instrumentNumber": "Instrument Number",
            "instrumentType": "Instrument Type",
            "location": "Location",
            "size": "Size",
        },
    )
    if err_response:
        return err_response
    try:
        photo_id = None
        if data.get("photo"):
            photo_id = handle_photo(data["photo"])

        new_instrument = InstrumentModel(
            str(uuid.uuid4()),
            number=data["instrumentNumber"].upper(),
            type=data["instrumentType"],
            size=data["size"],
            location=data["location"],
            assignedTo=data.get("studentName", None),
            maintenanceNotes=data.get("maintenanceNotes", None),
            conditionNotes=data.get("conditionNotes", None),
            condition=data.get("condition", None),
            quality=data.get("quality", None),
            rosin=data.get("rosin", False),
            bow=data.get("bow", False),
            shoulderRestEndpinRest=data.get("shoulderRestRockStop", False),
            ready=data.get("readyToGo", False),
            gifted=data.get("gifted", False),
            photo=photo_id,
        )
        new_instrument.save()
        return success(
            {
                "message": f"Instrument {new_instrument.number} created",
                "item": serialize_item(new_instrument),
                "id": new_instrument.id,
            },
            201,
        )
    except Exception as err:
        print(err)
        return failure(f"something has gone wrong")
