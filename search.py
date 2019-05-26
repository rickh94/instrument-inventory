import json

from common import setup_airtable, validate_request, make_filter_formula
from fuzzywuzzy import fuzz

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
        result = search_helper(
            "Assigned To", data["assignedTo"], multiple=True, exact=False
        )
        if result:
            return success(result)
        else:
            return failure(f"No matching instrument was found", 404)
    except Exception as err:
        return failure(f"Something has gone wrong {err}")


def search_helper(field, value, multiple=False, exact=True):
    """Helper to do the necessary search logic"""
    at = setup_airtable()
    results = []
    for page in at.get_iter():
        for item in page:
            if _check_item(item, field, value, exact):
                if not multiple:
                    return item
                results.append(item)

    return results


def _check_item(item, field, value, exact):
    if field not in item["fields"]:
        return False
    actual_value = item["fields"].get(field)
    if actual_value.lower() == value.lower():
        return True
    elif not exact and fuzz.partial_ratio(value.lower(), actual_value.lower()) > 80:
        return True
    return False
