import json

from common import setup_airtable
from responses import failure, success


def main(event, _context):
    """Filter instruments by certain values"""
    data = json.loads(event["body"])
    if not any(
        key in data for key in ["instrumentType", "notAssigned", "size", "location"]
    ):
        return failure(
            {"errors": "One of instrumentType, assigned, size, location is required"},
            400,
        )
    filter_list = []
    if data.get("instrumentType"):
        filter_list.append("{Instrument Type}='" + data["instrumentType"] + "'")
    if data.get("size"):
        filter_list.append("{Size}='" + data["size"] + "'")
    if data.get("location"):
        filter_list.append("{Location}='" + data["location"] + "'")
    if data.get("notAssigned"):
        filter_list.append("{Assigned To}=''")

    filter_string = ",".join(filter_list)

    try:
        at = setup_airtable()
        results = at.get_all(formula=f"AND({filter_string})")

        return success(results)
    except Exception as err:
        return failure(f"Something has gone wrong: {err}")
