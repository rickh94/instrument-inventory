from app.lib.models import InstrumentModel
from app.lib.responses import something_has_gone_wrong, not_found, bad_request, success
from app.lib.common import delete_photos

import pynamodb.exceptions


def main(event, _context):
    """Delete an instrument"""
    try:
        id_ = event["pathParameters"]["id"]
        item = InstrumentModel.get(id_)
        if getattr(item, "photo", None):
            delete_photos(item.photo)
        item.delete()
        return success("Delete successful", 204)
    except KeyError:
        return bad_request("ID is required in path")
    except pynamodb.exceptions.DoesNotExist:
        return not_found()
    except Exception as err:
        print(err)
        return something_has_gone_wrong()
