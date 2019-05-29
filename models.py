import os

from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute


TODOS_TABLE_NAME = os.environ.get("TODOS_TABLE_NAME")


class TodoModel(Model):
    """A task to do later"""

    class Meta:
        table_name = TODOS_TABLE_NAME

    userId = UnicodeAttribute(hash_key=True)
    todoId = UnicodeAttribute(range_key=True)
    content = UnicodeAttribute()
    createdAt = UnicodeAttribute()
    relevantInstrument = UnicodeAttribute(null=True)
