import pynamodb.exceptions

from app.lib.common import generate_photo_urls, serialize_item
from app.lib.decorators import something_might_go_wrong
from app.lib.models import InstrumentModel
from app.lib.responses import failure, success


@something_might_go_wrong
def main(event, _context):
    """Get an instrument"""
    if "id" not in event["pathParameters"]:
        return failure(f"Please supply id", 404)
    id_ = event["pathParameters"]["id"]
    ins = InstrumentModel.get(id_)
    result = serialize_item(ins)
    result["photoUrls"] = generate_photo_urls(ins.photo) if ins.photo else None
    return success(result)


@something_might_go_wrong
def all_(_event, _context):
    """Get all the instruments"""
    instruments = [serialize_item(ins) for ins in InstrumentModel.scan()]
    return success(instruments)
