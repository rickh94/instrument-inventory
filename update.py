import json

from common import setup_airtable, validate_request
from responses import failure, success


def photo(event, _context):
    """Change or add a photo"""
    data = json.loads(event["body"])
    err_response = validate_request(data, {"photoUrl": "Photo"})
    if err_response:
        return err_response
    try:
        rec_id = event["pathParameters"]["id"]
    except KeyError as err:
        return failure("Record ID must be in url", 404)
    try:
        at = setup_airtable()
        at.update(rec_id, {"Photo": [{"url": data["photoUrl"]}]})
        return success({"message": "Photo successfully updated"})
    except Exception as err:
        return failure(f"Something has gone wrong: {err}")
