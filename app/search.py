from app.utils import api_models
from app.utils.common import serialize_item
from app.utils.decorators import something_might_go_wrong, load_and_validate, load_model
from app.utils.models import InstrumentModel
from app.utils.responses import data_or_404


@something_might_go_wrong
@load_model(api_models.Search)
def number(search: api_models.Search):
    """Find an instrument by number"""
    # noinspection PyTypeChecker
    found_items = InstrumentModel.scan(InstrumentModel.number == search.term)
    instruments_out = api_models.process_instrument_db_list(found_items)
    return data_or_404(instruments_out)


@something_might_go_wrong
@load_model(api_models.Search)
def assigned(search: api_models.Search):
    """Find an instrument by who it's assigned to"""
    found_items = InstrumentModel.scan(InstrumentModel.assignedTo.contains(search.term))
    instruments_out = api_models.process_instrument_db_list(found_items)
    return data_or_404(instruments_out)


@something_might_go_wrong
@load_model(api_models.Search)
def history(search: api_models.Search):
    """Find an instrument by its history"""
    found_items = InstrumentModel.scan(InstrumentModel.history.contains(search.term))
    instruments_out = api_models.process_instrument_db_list(found_items)
    return data_or_404(instruments_out)


@something_might_go_wrong
@load_model(api_models.Search)
def history_and_assigned(search: api_models.Search):
    """Find a student's assigned instrument and history"""
    found_items = InstrumentModel.scan(
        InstrumentModel.history.contains(search.term)
        | InstrumentModel.assignedTo.contains(search.term)
    )
    instruments_out = api_models.process_instrument_db_list(found_items)
    return data_or_404(instruments_out)
