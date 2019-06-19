import json

from common import make_filter_formula, setup_airtable, validate_request
from responses import failure, success, not_found, something_has_gone_wrong
from models import InstrumentModel


def number(event, _context):
    """Find an instrument by number"""
    data = json.loads(event["body"])
    err_response = validate_request(data, {"instrumentNumber": "Instrument Number"})
    if err_response:
        return err_response
    try:
        found_items = InstrumentModel.scan(
            InstrumentModel.number == data["instrumentNumber"]
        )
        result_data = [item.attribute_values for item in found_items]
        if result_data:
            return success(result_data)
        else:
            return not_found()
    except Exception as err:
        print(err)
        return something_has_gone_wrong()


def assigned(event, _context):
    """Find an instrument by who it's assigned to"""
    data = json.loads(event["body"])
    err_response = validate_request(data, {"assignedTo": "Assigned To"})
    if err_response:
        return err_response
    try:
        found_items = InstrumentModel.scan(
            InstrumentModel.assignedTo.contains(data["assignedTo"])
        )
        result_data = [item.attribute_values for item in found_items]
        if result_data:
            return success(result_data)
        else:
            return not_found()
    except Exception as err:
        print(err)
        return something_has_gone_wrong()
