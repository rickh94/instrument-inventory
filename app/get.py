from lib.responses import failure, success
from lib.models import InstrumentModel
from lib.common import generate_photo_urls, serialize_item
import pynamodb.exceptions


def main(event, _context):
    """Get a record from airtable"""
    try:
        id_ = event["pathParameters"]["id"]
    except KeyError:
        return failure(f"Please supply id", 404)
    try:
        ins = InstrumentModel.get(id_)
        result = serialize_item(ins)
        result["photoUrls"] = generate_photo_urls(ins.photo) if ins.photo else None
        return success(result)
    except pynamodb.exceptions.DoesNotExist:
        return failure("Could not find matching item", 404)
    except Exception as err:
        print(err)
        return failure("Something has gone wrong")


def all_(_event, _context):
    """Get all the instruments"""
    try:
        instruments = [serialize_item(ins) for ins in InstrumentModel.scan()]
        return success(instruments)
    except Exception as err:
        print(err)
        return failure(f"Something has gone wrong")
