from app.lib.common import generate_photo_urls, serialize_item
from app.lib.decorators import something_might_go_wrong, get_id_from_path, no_args
from app.lib.models import InstrumentModel
from app.lib.responses import success


@something_might_go_wrong
@get_id_from_path
def main(id_):
    """Get a single instrument from the database."""
    ins = InstrumentModel.get(id_)
    result = serialize_item(ins)
    result["photoUrls"] = generate_photo_urls(ins.photo) if ins.photo else None
    return success(result)


@something_might_go_wrong
@no_args
def all_():
    """Get all the instruments"""
    instruments = [serialize_item(ins) for ins in InstrumentModel.scan()]
    return success(instruments)
