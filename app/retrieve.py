from app.utils import api_models
from app.utils.common import make_new_history
from app.utils.decorators import something_might_go_wrong, load_model
from app.utils.models import InstrumentModel
from app.utils.responses import success, not_found


@something_might_go_wrong
@load_model(api_models.RetrieveSingle)
def single(body: api_models.RetrieveSingle):
    """Mark an instrument as having been retrieved"""
    # noinspection PyTypeChecker
    found = list(InstrumentModel.scan(InstrumentModel.number == body.number.upper()))
    if not found:
        return not_found()
    item = found[0]
    item.location = "Storage"
    if item.assignedTo:
        item.history = make_new_history(item.history, item.assignedTo)
    item.assignedTo = None
    item.save()
    return success({"message": f"{item.type} {item.number} retrieved", "id": item.id})


def generate_actions(ins):
    actions = [
        InstrumentModel.assignedTo.set(None),
        InstrumentModel.location.set("Storage"),
    ]
    if ins.assignedTo:
        prev = ins.assignedTo
        actions.append(InstrumentModel.history.add({prev}))

    return actions


@something_might_go_wrong
@load_model(api_models.RetrieveMultiple)
def multiple(body: api_models.RetrieveMultiple):
    """Mark multiple instruments as having been retrieved"""
    numbers = [number.upper() for number in body.numbers]
    response_body = {"instrumentsUpdated": [], "instrumentsFailed": []}
    scan = InstrumentModel.scan(InstrumentModel.number.is_in(*numbers))
    for ins in scan:
        try:
            ins.location = "Storage"
            if ins.assignedTo:
                ins.history = make_new_history(ins.history, ins.assignedTo)
            ins.assignedTo = None
            ins.save()
            response_body["instrumentsUpdated"].append(ins.number)
        except Exception as err:
            print(err)
            response_body["instrumentsFailed"].append(ins.number)
    for instrument_number in body.numbers:
        if (
            instrument_number not in response_body["instrumentsUpdated"]
            and instrument_number not in response_body["instrumentsFailed"]
        ):
            response_body["instrumentsFailed"].append(instrument_number)
    return success(response_body)
