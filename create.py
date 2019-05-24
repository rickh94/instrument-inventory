import json

from common import setup_airtable, validate_request
from responses import failure, success


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
        at = setup_airtable()
    except Exception as err:
        return failure(f"Could not connect to airtable: {err}")
    try:
        fields = {
            "Number": data["instrumentNumber"].upper(),
            "Instrument Type": data["instrumentType"],
            "Size": data["size"],
            "Location": data["location"],
            "Assigned To": data.get("studentName", ""),
            "Maintenance Notes": data.get("maintenanceNotes", ""),
            "Condition Notes": data.get("conditionNotes", ""),
            "Condition": data.get("condition", None),
            "Quality": data.get("quality", None),
            "Rosin": data.get("rosin", False),
            "Bow": data.get("bow", False),
            "Shoulder Rest/Endpin Rest": data.get("shoulderRestRockStop", False),
            "Ready To Go": data.get("readyToGo", False),
            "Gifted to student": data.get("gifted", False),
            "Photo": [{"url": data.get("photo")}] if data.get("photo") else [],
        }
        rec = at.insert(fields)
        return success(
            {
                "message": f"Instrument {rec['fields']['Number']} created",
                "item": rec["fields"],
            },
            201,
        )
    except Exception as err:
        return failure(f"Something has gone wrong: {err}")
