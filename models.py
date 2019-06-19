import os

from pynamodb.models import Model
from pynamodb.attributes import (
    UnicodeAttribute,
    BooleanAttribute,
    NumberAttribute,
    UnicodeSetAttribute,
)

TODOS_TABLE_NAME = os.environ.get("TODOS_TABLE_NAME", "fake_table")
INSTRUMENTS_TABLE_NAME = os.environ.get(
    "INSTRUMENTS_TABLE_NAME", "fake_instruments_table"
)


class TodoModel(Model):
    """A task to do later"""

    class Meta:
        table_name = TODOS_TABLE_NAME

    userId = UnicodeAttribute(hash_key=True)
    todoId = UnicodeAttribute(range_key=True)
    content = UnicodeAttribute()
    relevantInstrument = UnicodeAttribute(null=True)
    completed = BooleanAttribute(default=False)


class InstrumentModel(Model):
    """A instrument"""

    class Meta:
        table_name = INSTRUMENTS_TABLE_NAME

    id = UnicodeAttribute(hash_key=True)
    number = UnicodeAttribute()
    size = UnicodeAttribute()
    type = UnicodeAttribute()
    location = UnicodeAttribute()
    assignedTo = UnicodeAttribute(null=True)
    maintenanceNotes = UnicodeAttribute(null=True)
    conditionNotes = UnicodeAttribute(null=True)
    condition = NumberAttribute(null=True)
    quality = NumberAttribute(null=True)
    rosin = BooleanAttribute(default=False)
    bow = BooleanAttribute(default=False)
    shoulderRestEndpinRest = BooleanAttribute(default=False)
    ready = BooleanAttribute(default=False)
    gifted = BooleanAttribute(default=False)
    photo = UnicodeAttribute(null=True)
    history = UnicodeSetAttribute(null=True)
    airtableId = UnicodeAttribute(null=True)
