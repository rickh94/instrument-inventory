import json

from lib.common import validate_request, make_new_history
from lib.responses import failure, success, something_has_gone_wrong
from lib.models import InstrumentModel


def main(event, _context):
    """Sign out an instrument"""
    data = json.loads(event["body"])
    err_response = validate_request(
        data,
        {
            "instrumentNumber": "Instrument Number",
            "assignedTo": "Assigned To",
            "location": "Location",
        },
    )
    if err_response:
        return err_response

    try:
        # noinspection PyTypeChecker
        found = list(
            InstrumentModel.scan(InstrumentModel.number == data["instrumentNumber"])
        )
        if not found:
            return failure(
                {"errors": {"instrumentNumber": "Could not find matching instrument"}},
                404,
            )
        item = found[0]
        if item.assignedTo:
            item.history = make_new_history(item.history, item.assignedTo)
        item.assignedTo = data["assignedTo"]
        item.location = data["location"]
        item.save()
        item.refresh()
        return success(
            {
                "message": f"Instrument {item.number} signed out to {item.assignedTo}"
                f" at {item.location}",
                "id": item.id,
            }
        )
    except Exception as err:
        print(err)
        return something_has_gone_wrong()
