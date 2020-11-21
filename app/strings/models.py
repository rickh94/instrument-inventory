import os

from pynamodb.attributes import UnicodeAttribute, NumberAttribute
from pynamodb.models import Model

from app.utils.common import str_uuid

STRINGS_TABLE_NAME = os.getenv("STRINGS_TABLE_NAME", "fake_strings_table")


class StringModel(Model):
    """A Type of String"""

    class Meta:
        table_name = STRINGS_TABLE_NAME

    id = UnicodeAttribute(hash_key=True, default=str_uuid)
    size = UnicodeAttribute()
    type = UnicodeAttribute()
    string = UnicodeAttribute()
    count = NumberAttribute(default=0)
