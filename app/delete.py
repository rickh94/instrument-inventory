from app.lib.common import delete_photos
from app.lib.decorators import something_might_go_wrong, get_id_from_path
from app.lib.models import InstrumentModel
from app.lib.responses import bad_request, success


@something_might_go_wrong
@get_id_from_path
def main(id_):
    """Delete an instrument"""
    item = InstrumentModel.get(id_)
    if getattr(item, "photo", None):
        delete_photos(item.photo)
    item.delete()
    return success("Delete successful", 204)
