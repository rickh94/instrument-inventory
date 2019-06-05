import json

from common import setup_airtable, validate_request
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
        _retrieve_instrument(data["instrumentNumber"], at)
        return success("Instrument retrieved")
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
            _retrieve_instrument(instrument_number, at)
            response_body["instrumentsUpdated"].append(instrument_number)
        except Exception as err:
            message = {"number": instrument_number}
            if isinstance(err, IndexError):
                message["error"] = "Could not find instrument"
            else:
                message["error"] = err
            response_body["instrumentsFailed"].append(message)
    return success(response_body)


def _add_to_history(new, history):
    """Add a new student to an instrument's history"""
    if not new:
        return None
    if not history:
        return new
    return f"{history}, {new}"


def _retrieve_instrument(instrument_number, at):
    """Perform the operations for retrieving an instrument"""
    result = at.search("Number", instrument_number)[0]
    assigned_to = result["fields"].get("Assigned To", None)
    history = result["fields"].get("History", None)
    new_history = _add_to_history(assigned_to, history)
    update = {"Location": "Storage", "Assigned To": ""}
    if new_history:
        update["History"] = new_history
    at.update(result["id"], update)
