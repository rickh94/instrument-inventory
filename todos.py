import json
import uuid

from common import validate_request
from models import TodoModel
from responses import failure, success
import pynamodb.exceptions


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
    except Exception as err:
        return failure(f"Something has gone wrong: {err}")


def read_single(event, _context):
    """Get a single to do item"""
    try:
        todo_id = event["pathParameters"]["id"]
        user_id = event["requestContext"]["identity"]["cognitoIdentityId"]
    except KeyError:
        return failure("Please provide a todoId and userId", 400)

    try:
        item = TodoModel.get(user_id, todo_id)
        return success(
            {
                "todoId": item.todoId,
                "content": item.content,
                "relevantInstrument": item.relevantInstrument,
                "completed": item.completed,
            }
        )
    except pynamodb.exceptions.DoesNotExist:
        return failure("Could not find matching item", 404)
    except Exception as err:
        print(err)
        return failure("Something has gone wrong")


def read_active(event, _context):
    """Get all uncompleted to do items"""
    try:
        user_id = event["requestContext"]["identity"]["cognitoIdentityId"]
        items = TodoModel.query(user_id, TodoModel.completed == False)
        response_body = [item.attribute_values for item in items]
        return success(response_body)
    except Exception as err:
        print(err)
        return failure("Something has gone wrong")


def read_completed(event, _context):
    """Get all completed to do items"""
    try:
        user_id = event["requestContext"]["identity"]["cognitoIdentityId"]
        items = TodoModel.query(user_id, TodoModel.completed == True)
        response_body = [item.attribute_values for item in items]
        return success(response_body)
    except Exception as err:
        print(err)
        return failure("Something has gone wrong")


def _modify_completed(event, set_to):
    try:
        user_id = event["requestContext"]["identity"]["cognitoIdentityId"]
        todo_id = event["pathParameters"]["id"]
    except KeyError:
        return failure("User and todo id are required", 400)
    try:
        item = TodoModel.get(user_id, todo_id)
    except pynamodb.exceptions.DoesNotExist:
        return failure("Could not find matching item", 404)
    try:
        item.update(actions=[TodoModel.completed.set(set_to)])
        item.save()
        item.refresh()
        return success({"message": "Updated", "item": item.attribute_values})
    except Exception as err:
        print(err)
        return failure("Something has gone wrong")


def mark_completed(event, _context):
    """Mark an item as completed"""
    return _modify_completed(event, True)


def unmark_completed(event, _context):
    """Mark an to do item as not complete"""
    return _modify_completed(event, False)


def update(event, _context):
    """Update the content or instrument of a to do item"""
    data = json.loads(event["body"])
    try:
        user_id = event["requestContext"]["identity"]["cognitoIdentityId"]
        todo_id = event["pathParameters"]["id"]
    except KeyError:
        return failure("User and todo id are required", 400)
    try:
        item = TodoModel.get(user_id, todo_id)
    except pynamodb.exceptions.DoesNotExist:
        return failure("Could not find matching item", 404)
    try:
        actions = []
        if data.get("content"):
            actions.append(TodoModel.content.set(data["content"]))
        if data.get("relevantInstrument"):
            actions.append(TodoModel.relevantInstrument.set(data["relevantInstrument"]))
        item.update(actions=actions)
        item.save()
        item.refresh()
        return success({"message": "Updated", "item": item.attribute_values})
    except Exception as err:
        print(err)
        return failure("Something has gone wrong")


def delete(event, _context):
    """Delete a to do item"""
    try:
        user_id = event["requestContext"]["identity"]["cognitoIdentityId"]
        todo_id = event["pathParameters"]["id"]
    except KeyError:
        return failure("User and todo id are required", 400)
    try:
        item = TodoModel.get(user_id, todo_id)
    except pynamodb.exceptions.DoesNotExist:
        return failure("Could not find matching item", 404)
    try:
        item.delete()
        return success({"message": "deleted"}, 204)
    except Exception as err:
        print(err)
        return failure("Something has gone wrong")
