import os

from pynamodb.attributes import UnicodeAttribute, NumberAttribute
from pynamodb.models import Model

from app.utils.common import str_uuid

OTHER_TABLE_NAME = os.getenv("OTHER_TABLE_NAME", "fake_other_table")


class OtherModel(Model):
    """Another item"""

    class Meta:
        table_name = OTHER_TABLE_NAME

    id = UnicodeAttribute(hash_key=True, default=str_uuid)
    item = UnicodeAttribute()
    count = NumberAttribute(default=0)
