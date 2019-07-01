import json

from app.lib.common import validate_request, serialize_item
from app.lib.responses import success, not_found, something_has_gone_wrong, bad_request
from app.lib.models import InstrumentModel


def number(event, _context):
    """Find an instrument by number"""
    data = json.loads(event["body"])
    err_response = validate_request(data, {"term": "Search Term"})
    if err_response:
        return err_response
    try:
        # noinspection PyTypeChecker
        found_items = InstrumentModel.scan(InstrumentModel.number == data["term"])
        result_data = [serialize_item(item) for item in found_items]
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
    err_response = validate_request(data, {"term": "Search Term"})
    if err_response:
        return err_response
    try:
        found_items = InstrumentModel.scan(
            InstrumentModel.assignedTo.contains(data["term"])
        )
        result_data = [serialize_item(item) for item in found_items]
        if result_data:
            return success(result_data)
        else:
            return not_found()
    except Exception as err:
        print(err)
        return something_has_gone_wrong()


def history(event, _context):
    """Find an instrument by its history"""
    data = json.loads(event["body"])
    err_response = validate_request(data, {"term": "Term"})
    if err_response:
        return err_response
    try:
        found_items = InstrumentModel.scan(
            InstrumentModel.history.contains(data["term"])
        )
        result_data = [serialize_item(item) for item in found_items]
        if result_data:
            return success(result_data)
        else:
            return not_found()
    except Exception as err:
        print(err)
        return something_has_gone_wrong()


def history_and_assigned(event, _context):
    """Find a student's assigned instrument and history"""
    data = json.loads(event["body"])
    err_response = validate_request(data, {"term": "Search Term"})
    if err_response:
        return err_response
    try:
        found_items = InstrumentModel.scan(
            InstrumentModel.history.contains(data["term"])
            | InstrumentModel.assignedTo.contains(data["term"])
        )
        result_data = [serialize_item(item) for item in found_items]
        if result_data:
            return success(result_data)
        else:
            return not_found()
    except Exception as err:
        print(err)
        return something_has_gone_wrong()
