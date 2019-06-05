import json

from common import setup_airtable, validate_request, move_instrument
from responses import failure, success


def single(event, _context):
    """Mark an instrument as having been retrieved"""
    data = json.loads(event["body"])
    err_response = validate_request(
        body=data, required_fields={"instrumentNumber": "Instrument Number"}
    )
    if err_response:
        return err_response
    try:
        at = setup_airtable()
    except Exception as err:
        return failure(f"Could not connect to airtable: {err}")
    try:
        rec = move_instrument(data["instrumentNumber"], at)
        return success({"message": "Instrument retrieved", "id": rec["id"]})
    except Exception as err:
        if isinstance(err, IndexError):
            return failure("Could not find matching instrument", 404)
        return failure(f"Something has gone wrong: {err}")


def multiple(event, _context):
    """Mark multiple instruments as having been retrieved"""
    data = json.loads(event["body"])
    err_response = validate_request(
        body=data, required_fields={"instrumentNumbers": "Instrument Number List"}
    )
    if err_response:
        return err_response
    response_body = {"instrumentsUpdated": [], "instrumentsFailed": []}
    try:
        at = setup_airtable()
    except Exception as err:
        return failure(f"Could not connect to airtable: {err}")

    for instrument_number in data["instrumentNumbers"]:
        try:
            move_instrument(instrument_number, at)
            response_body["instrumentsUpdated"].append(instrument_number)
        except Exception as err:
            message = {"number": instrument_number}
            if isinstance(err, IndexError):
                message["error"] = "Could not find instrument"
            else:
                message["error"] = err
            response_body["instrumentsFailed"].append(message)
    return success(response_body)
