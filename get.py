from responses import failure, success
from models import InstrumentModel
from common import generate_photo_urls
import pynamodb.exceptions


def main(event, _context):
    """Get a record from airtable"""
    try:
        id_ = event["pathParameters"]["id"]
    except KeyError:
        return failure(f"Please supply id", 404)
    try:
        ins = InstrumentModel.get(id_)
        result = {field: value for field, value in ins.attribute_values.items()}
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
        instruments = [ins.attribute_values for ins in InstrumentModel.scan()]
        return success(instruments)
    except Exception as err:
        print(err)
        return failure(f"Something has gone wrong")
