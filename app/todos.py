import ujson

from app.utils import api_models
from app.utils.decorators import something_might_go_wrong, get_todo_ids, load_model
from app.utils.models import TodoModel
from app.utils.responses import success


@something_might_go_wrong
@load_model(api_models.Todo, with_identity=True)
def create(todo: api_models.Todo, identity_id):
    """Create a new to do in the database"""
    new_todo = TodoModel(identity_id, **todo.dict())
    new_todo.save()
    todo_db = api_models.TodoInDB.parse_obj(new_todo.attribute_values)
    todo_out = api_models.TodoOut.parse_obj(todo_db)
    return success({"message": "Todo Created", "item": todo_out.dict()}, 201)


@something_might_go_wrong
@get_todo_ids
def read_single(user_id, todo_id, _):
    """Get a single to do item"""
    todo = TodoModel.get(user_id, todo_id)
    todo_db = api_models.TodoInDB.parse_obj(todo.attribute_values)
    todo_out = api_models.TodoOut.parse_obj(todo_db)
    return success(todo_out.dict())


@something_might_go_wrong
def read_active(event, _context):
    """Get all uncompleted to do items"""
    user_id = event["requestContext"]["identity"]["cognitoIdentityId"]
    items = TodoModel.query(user_id, TodoModel.completed == False)
    response_body = api_models.process_todo_db_list(items)
    return success(response_body)


@something_might_go_wrong
def read_completed(event, _context):
    """Get all completed to do items"""
    user_id = event["requestContext"]["identity"]["cognitoIdentityId"]
    items = TodoModel.query(user_id, TodoModel.completed == True)
    response_body = api_models.process_todo_db_list(items)
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
    data = ujson.loads(event["body"])
    item = TodoModel.get(user_id, todo_id)
    if data.get("content"):
        item.content = data["content"]
    if data.get("relevantInstrument"):
        item.relevantInstrument = data["relevantInstrument"]
    item.save()
    item.refresh()
    todo_db = api_models.TodoInDB.parse_obj(item.attribute_values)
    todo_out = api_models.TodoOut.parse_obj(todo_db)
    return success({"message": "Updated", "item": todo_out.dict()})


@something_might_go_wrong
@get_todo_ids
def delete(user_id, todo_id, _):
    """Delete a to do item"""
    item = TodoModel.get(user_id, todo_id)
    item.delete()
    return success({"message": "deleted"}, 204)
