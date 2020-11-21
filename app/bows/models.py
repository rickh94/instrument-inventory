import os

from pynamodb.attributes import UnicodeAttribute, NumberAttribute
from pynamodb.models import Model

from app.utils.common import str_uuid

BOWS_TABLE_NAME = os.getenv("BOWS_TABLE_NAME", "fake_bows_table")


class BowModel(Model):
    """A Type of Bow"""

    class Meta:
        table_name = BOWS_TABLE_NAME

    id = UnicodeAttribute(hash_key=True, default=str_uuid)
    size = UnicodeAttribute()
    type = UnicodeAttribute()
    count = NumberAttribute(default=0)
