from app.lib.common import handle_photo, serialize_item
from app.lib.decorators import something_might_go_wrong, load_and_validate
from app.lib.models import InstrumentModel
from app.lib.responses import success

required_fields = {
    "instrumentNumber": "Instrument Number",
    "instrumentType": "Instrument Type",
    "location": "Location",
    "size": "Size",
}


@something_might_go_wrong
@load_and_validate(required_fields)
def main(data):
    """Create a new instrument"""
    photo_id = None
    if data.get("photo"):
        photo_id = handle_photo(data["photo"])

    new_instrument = InstrumentModel(
        number=data["instrumentNumber"].upper(),
        type=data["instrumentType"],
        size=data["size"],
        location=data["location"],
        assignedTo=data.get("assignedTo", None),
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
