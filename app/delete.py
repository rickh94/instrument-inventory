from app.lib.common import delete_photos
from app.lib.decorators import something_might_go_wrong
from app.lib.models import InstrumentModel
from app.lib.responses import bad_request, success


@something_might_go_wrong
def main(event, _context):
    """Delete an instrument"""
    try:
        id_ = event["pathParameters"]["id"]
    except KeyError:
        return bad_request("ID is required in path")

    item = InstrumentModel.get(id_)
    if getattr(item, "photo", None):
        delete_photos(item.photo)
    item.delete()
    return success("Delete successful", 204)
