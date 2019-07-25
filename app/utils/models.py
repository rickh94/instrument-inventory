import os
import uuid

from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, BooleanAttribute, NumberAttribute

TODOS_TABLE_NAME = os.getenv("TODOS_TABLE_NAME", "fake_table")
INSTRUMENTS_TABLE_NAME = os.getenv("INSTRUMENTS_TABLE_NAME", "fake_instruments_table")


def str_uuid():
    return str(uuid.uuid4())


class TodoModel(Model):
    """A task to do later"""

    class Meta:
        table_name = TODOS_TABLE_NAME

    userId = UnicodeAttribute(hash_key=True)
    todoId = UnicodeAttribute(range_key=True, default=str_uuid)
    content = UnicodeAttribute()
    relevantInstrument = UnicodeAttribute(null=True)
    completed = BooleanAttribute(default=False)


class InstrumentModel(Model):
    """A instrument"""

    class Meta:
        table_name = INSTRUMENTS_TABLE_NAME

    id = UnicodeAttribute(hash_key=True, default=str_uuid)
    number = UnicodeAttribute()
    size = UnicodeAttribute()
    type = UnicodeAttribute()
    location = UnicodeAttribute()
    assignedTo = UnicodeAttribute(null=True)
    maintenanceNotes = UnicodeAttribute(null=True)
    conditionNotes = UnicodeAttribute(null=True)
    condition = NumberAttribute(null=True)
    quality = NumberAttribute(null=True)
    gifted = BooleanAttribute(default=False)
    photo = UnicodeAttribute(null=True)
    history = UnicodeAttribute(null=True)
