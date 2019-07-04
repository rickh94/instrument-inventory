from app.lib.common import serialize_item
from app.lib.decorators import something_might_go_wrong, load_and_validate
from app.lib.models import InstrumentModel
from app.lib.responses import data_or_404


@something_might_go_wrong
@load_and_validate({"term": "Search Term"})
def number(data):
    """Find an instrument by number"""
    # noinspection PyTypeChecker
    found_items = InstrumentModel.scan(InstrumentModel.number == data["term"])
    result_data = [serialize_item(item) for item in found_items]
    return data_or_404(result_data)


@something_might_go_wrong
@load_and_validate({"term": "Search Term"})
def assigned(data):
    """Find an instrument by who it's assigned to"""
    found_items = InstrumentModel.scan(
        InstrumentModel.assignedTo.contains(data["term"])
    )
    result_data = [serialize_item(item) for item in found_items]
    return data_or_404(result_data)


@something_might_go_wrong
@load_and_validate({"term": "Search Term"})
def history(data):
    """Find an instrument by its history"""
    found_items = InstrumentModel.scan(InstrumentModel.history.contains(data["term"]))
    result_data = [serialize_item(item) for item in found_items]
    return data_or_404(result_data)


@something_might_go_wrong
@load_and_validate({"term": "Search Term"})
def history_and_assigned(data):
    """Find a student's assigned instrument and history"""
    found_items = InstrumentModel.scan(
        InstrumentModel.history.contains(data["term"])
        | InstrumentModel.assignedTo.contains(data["term"])
    )
    result_data = [serialize_item(item) for item in found_items]
    return data_or_404(result_data)
