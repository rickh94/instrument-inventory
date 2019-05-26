from common import setup_airtable
from responses import success, failure


def main(event, _context):
    """Get a record from airtable"""
    if not event.get("pathParameters"):
        return failure(f"Please supply id", 404)
    if not event["pathParameters"].get("id"):
        return failure(f"Please supply id", 404)
    rec_id = event["pathParameters"]["id"]
    try:
        at = setup_airtable()
        item = at.get(rec_id)
        if item:
            return success(item)
        else:
            return failure(f"Could not find {rec_id}")
    except Exception as err:
        return failure(f"Something has gone wrong {err}")
