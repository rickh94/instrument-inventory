from app.utils.common import make_new_history
from app.utils.decorators import something_might_go_wrong, load_and_validate
from app.utils.models import InstrumentModel
from app.utils.responses import failure, success

required_fields = {
    "instrumentNumber": "Instrument Number",
    "assignedTo": "Assigned To",
    "location": "Location",
}


@something_might_go_wrong
@load_and_validate(required_fields)
def main(data):
    """Sign out an instrument"""
    # noinspection PyTypeChecker
    found = list(
        InstrumentModel.scan(InstrumentModel.number == data["instrumentNumber"])
    )
    if not found:
        return failure(
            {"errors": {"instrumentNumber": "Could not find matching instrument"}}, 404
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
