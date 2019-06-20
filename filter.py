import json

from models import InstrumentModel
from responses import failure, success, something_has_gone_wrong, bad_request


def main(event, _context):
    """Filter instruments by certain values"""
    data = json.loads(event["body"])
    if not any(
        key in data for key in ["instrumentType", "notAssigned", "size", "location"]
    ):
        return bad_request(
            {"errors": "One of instrumentType, assigned, size, location is required"}
        )
    filter_list = []
    if data.get("instrumentType"):
        filter_list.append('(InstrumentModel.type == data["instrumentType"])')
    if data.get("size"):
        filter_list.append('(InstrumentModel.size == data["size"])')
    if data.get("location"):
        filter_list.append('(InstrumentModel.location == data["location"])')
    if data.get("notAssigned"):
        filter_list.append(
            "(InstrumentModel.assignedTo.does_not_exist() | "
            'InstrumentModel.assignedTo == "")'
        )

    filter_string = " & ".join(filter_list)

    try:
        found = InstrumentModel.scan(eval(filter_string))

        results_data = [item.attribute_values for item in found]

        return success(results_data)
    except Exception as err:
        print(err)
        return something_has_gone_wrong()
