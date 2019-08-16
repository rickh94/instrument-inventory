from app.utils import api_models
from app.utils.decorators import something_might_go_wrong, no_args, load_model
from app.utils.models import InstrumentModel
from app.utils.responses import success, bad_request, data_or_404


@something_might_go_wrong
@load_model(api_models.InstrumentFilter)
def main(instrument_filter: api_models.InstrumentFilter):
    """Filter instruments by certain values"""
    filter_string = instrument_filter.generate_filter_string()

    found = InstrumentModel.scan(eval(filter_string))
    instruments_out = api_models.process_instrument_db_list(found)

    return success(instruments_out)


@something_might_go_wrong
@no_args
def signed_out():
    """Find instruments that haven't been signed back in yet"""
    found = InstrumentModel.scan(
        (InstrumentModel.assignedTo.exists()) & (InstrumentModel.gifted == False)
    )
    instruments_out = api_models.process_instrument_db_list(found)

    return data_or_404(instruments_out)


@something_might_go_wrong
@no_args
def gifted():
    """Find instruments that have been given away to students"""
    found = InstrumentModel.scan(InstrumentModel.gifted == True)
    instruments_out = api_models.process_instrument_db_list(found)
    return data_or_404(instruments_out)
