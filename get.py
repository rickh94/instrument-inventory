from common import setup_airtable
from responses import failure, success


def main(event, _context):
    """Get a record from airtable"""
    try:
        rec_id = event["pathParameters"]["id"]
    except KeyError:
        return failure(f"Please supply id", 404)
    try:
        at = setup_airtable()
        item = at.get(rec_id)
        if item:
            return success(item)
        else:
            return failure(f"Could not find {rec_id}")
    except Exception as err:
        return failure(f"Something has gone wrong {err}")
