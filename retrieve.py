import json
import os

from airtable import Airtable
from responses import success, failure


def _setup_airtable():
    base_key = os.environ.get("AIRTABLE_BASE_KEY")
    table_name = os.environ.get("TABLE_NAME")
    return Airtable(base_key, table_name)


def single(event, _context):
    """Mark an instrument as having been retrieved"""
    data = json.loads(event["body"])
    try:
        at = _setup_airtable()
    except Exception as err:
        return failure(f"Could not connect to airtable: {err}")
    try:
        _retrieve_instrument(data["instrumentNumber"], at)
        return success("Instrument retrieved")
    except Exception as err:
        if isinstance(err, IndexError):
            return failure("Could not find matching instrument")
        return failure(f"Something has gone wrong: {err}")


def multiple(event, _context):
    """Mark multiple instruments as having been retrieved"""
    data = json.loads(event["body"])
    response_body = {"instrumentsUpdated": [], "instrumentsFailed": []}
    try:
        at = _setup_airtable()
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
    update = {"Location": "transit", "Assigned To": ""}
    if new_history:
        update["History"] = new_history
    at.update(result["id"], update)
