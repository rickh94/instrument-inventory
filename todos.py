import json
import uuid

from common import validate_request
from models import TodoModel
from responses import failure, success


def create(event, _context):
    """Create a new to do in the database"""
    data = json.loads(event["body"])
    err_response = validate_request(data, {"content": "Content"})
    if err_response:
        return err_response
    try:
        new_todo = TodoModel(
            event["requestContext"]["identity"]["cognitoIdentityId"],
            str(uuid.uuid1()),
            content=data["content"],
            relevantInstrument=data.get("relevantInstrument", None),
        )
        new_todo.save()
        return success("Todo Created", 201)
    except Exception as err:
        return failure(f"Something has gone wrong: {err}")


def read_single(event, _context):
    pass


def read_multiple(event, _context):
    pass


def mark_complete(event, _context):
    pass


def update(event, _context):
    pass


def delete(event, _context):
    pass
