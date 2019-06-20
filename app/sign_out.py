import json

from lib.common import validate_request
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
        found = list(
            InstrumentModel.scan(InstrumentModel.number == data["instrumentNumber"])
        )
        if not found:
            return failure(
                {"errors": {"instrumentNumber": "Could not find matching instrument"}},
                404,
            )
        item = found[0]
        actions = [
            InstrumentModel.assignedTo.set(data["assignedTo"]),
            InstrumentModel.location.set(data["location"]),
        ]
        if item.assignedTo:
            prev = item.assignedTo
            actions.append(InstrumentModel.history.add({prev}))
        item.update(actions=actions)
        item.save()
        item.refresh()
        return success(
            f"Instrument {item.number} signed out to {item.assignedTo}"
            f" at {item.location}"
        )
    except Exception as err:
        print(err)
        return something_has_gone_wrong()
