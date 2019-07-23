import json

from app.utils import api_models
from app.utils.common import serialize_item
from app.utils.decorators import something_might_go_wrong, no_args, load_model
from app.utils.models import InstrumentModel
from app.utils.responses import success, bad_request, data_or_404


@something_might_go_wrong
@load_model(api_models.InstrumentFilter)
def main(instrument_filter: api_models.InstrumentFilter):
    """Filter instruments by certain values"""
    # data = json.loads(event["body"])
    # if not any(
    #     key in data for key in ["instrumentType", "notAssigned", "size", "location"]
    # ):
    #     return bad_request(
    #         {"errors": "One of instrumentType, assigned, size, location is required"}
    #     )
    # filter_list = []
    # if data.get("instrumentType"):
    #     filter_list.append('(InstrumentModel.type == data["instrumentType"])')
    # if data.get("size"):
    #     filter_list.append('(InstrumentModel.size == data["size"])')
    # if data.get("location"):
    #     filter_list.append('(InstrumentModel.location == data["location"])')
    # if data.get("notAssigned"):
    #     filter_list.append(
    #         "(InstrumentModel.assignedTo.does_not_exist() | "
    #         'InstrumentModel.assignedTo == "")'
    #     )

    # filter_string = " & ".join(filter_list)
    filter_string = instrument_filter.generate_filter_string()

    found = InstrumentModel.scan(eval(filter_string))
    found_instruments = [
        api_models.InstrumentInDB(**item.attribute_values) for item in found
    ]

    instruments_out = [
        api_models.InstrumentOut(**item.dict()) for item in found_instruments
    ]

    return success([instrument.dict() for instrument in instruments_out])


@something_might_go_wrong
@no_args
def signed_out():
    """Find instruments that haven't been signed back in yet"""
    found_items = InstrumentModel.scan(
        (InstrumentModel.assignedTo.exists()) & (InstrumentModel.gifted == False)
    )
    result_data = [serialize_item(item) for item in found_items]
    return data_or_404(result_data)


@something_might_go_wrong
@no_args
def gifted():
    """Find instruments that have been given away to students"""
    found_items = InstrumentModel.scan(InstrumentModel.gifted == True)
    result_data = [serialize_item(item) for item in found_items]
    return data_or_404(result_data)
