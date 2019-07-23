from app.utils.common import delete_photos
from app.utils.decorators import something_might_go_wrong, get_id_from_path
from app.utils.models import InstrumentModel
from app.utils.responses import success


@something_might_go_wrong
@get_id_from_path
def main(id_):
    """Delete an instrument"""
    item = InstrumentModel.get(id_)
    if getattr(item, "photo", None):
        delete_photos(item.photo)
    item.delete()
    return success("Delete successful", 204)
