import json

from app.utils.decorators import (
    something_might_go_wrong,
    load_and_validate,
    get_todo_ids,
)
from app.utils.models import TodoModel
from app.utils.responses import success


@something_might_go_wrong
@load_and_validate({"content": "Content"}, with_identity=True)
def create(data, identity_id):
    """Create a new to do in the database"""
    new_todo = TodoModel(
        identity_id,
        content=data["content"],
        relevantInstrument=data.get("relevantInstrument", None),
    )
    new_todo.save()
    return success(
        {
            "message": "Todo Created",
            "item": {
                "todoId": new_todo.todoId,
                "content": new_todo.content,
                "relevantInstrument": new_todo.relevantInstrument,
                "completed": new_todo.completed,
            },
        },
        201,
    )


@something_might_go_wrong
@get_todo_ids
def read_single(user_id, todo_id, _):
    """Get a single to do item"""
    item = TodoModel.get(user_id, todo_id)
    return success(
        {
            "todoId": item.todoId,
            "content": item.content,
            "relevantInstrument": item.relevantInstrument,
            "completed": item.completed,
        }
    )


@something_might_go_wrong
def read_active(event, _context):
    """Get all uncompleted to do items"""
    user_id = event["requestContext"]["identity"]["cognitoIdentityId"]
    items = TodoModel.query(user_id, TodoModel.completed == False)
    response_body = [item.attribute_values for item in items]
    return success(response_body)


@something_might_go_wrong
def read_completed(event, _context):
    """Get all completed to do items"""
    user_id = event["requestContext"]["identity"]["cognitoIdentityId"]
    items = TodoModel.query(user_id, TodoModel.completed == True)
    response_body = [item.attribute_values for item in items]
    return success(response_body)


def _modify_completed(user_id, todo_id, set_to):
    item = TodoModel.get(user_id, todo_id)
    item.completed = set_to
    item.save()
    item.refresh()
    return success({"message": "Updated", "item": item.attribute_values})


@something_might_go_wrong
@get_todo_ids
def mark_completed(user_id, todo_id, _):
    """Mark an item as completed"""
    return _modify_completed(user_id, todo_id, True)


@something_might_go_wrong
@get_todo_ids
def unmark_completed(user_id, todo_id, _):
    """Mark an to do item as not complete"""
    return _modify_completed(user_id, todo_id, False)


@something_might_go_wrong
@get_todo_ids
def update(user_id, todo_id, event):
    """Update the content or instrument of a to do item"""
    data = json.loads(event["body"])
    item = TodoModel.get(user_id, todo_id)
    if data.get("content"):
        item.content = data["content"]
    if data.get("relevantInstrument"):
        item.relevantInstrument = data["relevantInstrument"]
    item.save()
    item.refresh()
    return success({"message": "Updated", "item": item.attribute_values})


@something_might_go_wrong
@get_todo_ids
def delete(user_id, todo_id, _):
    """Delete a to do item"""
    item = TodoModel.get(user_id, todo_id)
    item.delete()
    return success({"message": "deleted"}, 204)
