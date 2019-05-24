import json

from common import setup_airtable
from fuzzywuzzy import fuzz

from responses import failure, success


def number(event, _context):
    """Find an instrument by number"""
    data = json.loads(event["body"])
    try:
        result = search_helper(
            "Number", data["instrumentNumber"], multiple=False, exact=True
        )
        if result:
            return success(result)
        else:
            return failure("No matching instrument was found.", 404)
    except Exception as err:
        return failure(f"Something has gone wrong: {err}")


def student(event, _context):
    pass


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
    actual_value = item["fields"].get(field)
    if actual_value.lower() == value.lower():
        return True
    elif not exact and fuzz.partial_ratio(value.lower(), actual_value.lower()) > 80:
        return True
    return False
