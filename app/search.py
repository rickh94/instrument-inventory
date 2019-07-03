from app.lib.common import serialize_item
from app.lib.decorators import something_might_go_wrong, load_and_validate
from app.lib.response import data_or_404
from app.lib.models import InstrumentModel


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


@something_might_go_wrong
def outstanding(_event, _context):
    """Find instruments that haven't been signed back in yet"""
    found_items = InstrumentModel.scan(
        InstrumentModel.assignedTo.exists() & InstrumentModel.gifted == False
    )
    result_data = [serialize_item(item) for item in found_items]
    return data_or_404(result_data)


@something_might_go_wrong
def gifted(_event, _context):
    """Find instruments that have been given away to students"""
    found_items = InstrumentModel.scan(InstrumentModel.gifted == True)
    result_data = [serialize_item(item) for item in found_items]
    return data_or_404(result_data)
