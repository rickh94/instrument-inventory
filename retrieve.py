import json

from common import setup_airtable, validate_request, move_instrument
from responses import failure, success, not_found, something_has_gone_wrong
from models import InstrumentModel


def single(event, _context):
    """Mark an instrument as having been retrieved"""
    data = json.loads(event["body"])
    err_response = validate_request(
        body=data, required_fields={"instrumentNumber": "Instrument Number"}
    )
    if err_response:
        return err_response
    try:
        found = list(
            InstrumentModel.scan(InstrumentModel.number == data["instrumentNumber"])
        )
        if not found:
            return not_found()
        item = found[0]
        actions = generate_actions(item)
        item.update(actions=actions)
        item.save()
        return success({"message": "Instrument retrieved", "id": item.id})
    except Exception as err:
        print(err)
        return something_has_gone_wrong()


def generate_actions(ins):
    actions = [
        InstrumentModel.assignedTo.set(None),
        InstrumentModel.location.set("Storage"),
    ]
    if ins.assignedTo:
        prev = ins.assignedTo
        actions.append(InstrumentModel.history.add({prev}))

    return actions


def multiple(event, _context):
    """Mark multiple instruments as having been retrieved"""
    data = json.loads(event["body"])
    err_response = validate_request(
        body=data, required_fields={"instrumentNumbers": "Instrument Number List"}
    )
    if err_response:
        return err_response
    response_body = {"instrumentsUpdated": [], "instrumentsFailed": []}
    try:
        scan = InstrumentModel.scan(
            InstrumentModel.number.is_in(*data["instrumentNumbers"])
        )
    except Exception as err:
        print(err)
        return something_has_gone_wrong()
    for ins in scan:
        try:
            actions = generate_actions(ins)
            ins.update(actions=actions)
            ins.save()
            response_body["instrumentsUpdated"].append(ins.number)
        except Exception as err:
            print(err)
            response_body["instrumentsFailed"].append(ins.number)
    for instrument_number in data["instrumentNumbers"]:
        if (
            instrument_number not in response_body["instrumentsUpdated"]
            and instrument_number not in response_body["instrumentsFailed"]
        ):
            response_body["instrumentsFailed"].append(instrument_number)
    return success(response_body)
