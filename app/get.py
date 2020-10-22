from app.utils import api_models
from app.utils.common import generate_photo_urls
from app.utils.decorators import something_might_go_wrong, get_id_from_path, no_args
from app.utils.models import InstrumentModel
from app.utils.responses import success


@something_might_go_wrong
@get_id_from_path
def main(id_):
    """Get a single instrument from the database."""
    ins = api_models.InstrumentInDB.parse_obj(InstrumentModel.get(id_).attribute_values)
    photo_urls = generate_photo_urls(ins.photo) if ins.photo else None
    ins_out = api_models.InstrumentOut(**ins.dict(), photoUrls=photo_urls)
    return success(ins_out.dict())


@something_might_go_wrong
@no_args
def all_():
    """Get all the instruments"""
    instruments, instruments_failed = api_models.process_all_instruments_list(
        InstrumentModel.scan()
    )
    return success(
        {"instruments": instruments, "instrumentsFailed": instruments_failed}
    )
