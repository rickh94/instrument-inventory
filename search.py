import json

from common import setup_airtable, validate_request, make_filter_formula

from responses import failure, success


def number(event, _context):
    """Find an instrument by number"""
    data = json.loads(event["body"])
    err_response = validate_request(data, {"instrumentNumber": "Instrument Number"})
    if err_response:
        return err_response
    try:
        at = setup_airtable()
        result = at.get_all(
            formula=make_filter_formula("Number", data["instrumentNumber"])
        )
        if result:
            return success(result)
        else:
            return failure("No matching instrument was found.", 404)
    except Exception as err:
        return failure(f"Something has gone wrong: {err}")


def assigned(event, _context):
    """Find an instrument by who it's assigned to"""
    data = json.loads(event["body"])
    err_response = validate_request(data, {"assignedTo": "Assigned To"})
    if err_response:
        return err_response
    try:
        at = setup_airtable()
        results = at.get_all(
            formula=(
                "SEARCH('" + data["assignedTo"].lower() + "', LOWER({Assigned To}))"
            )
        )
        if results:
            return success(results)
        else:
            return failure(f"No matching instrument was found", 404)
    except Exception as err:
        return failure(f"Something has gone wrong {err}")
