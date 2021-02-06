import os

from pynamodb.attributes import UnicodeAttribute, NumberAttribute, UnicodeSetAttribute
from pynamodb.models import Model

from app.utils.common import str_uuid

OTHER_TABLE_NAME = os.getenv("OTHER_TABLE_NAME", "fake_other_table")


class OtherModel(Model):
    """Another item"""

    class Meta:
        table_name = OTHER_TABLE_NAME
        host = os.getenv("DYNAMODB_HOST")

    id = UnicodeAttribute(hash_key=True, default=str_uuid)
    name = UnicodeAttribute()
    count = NumberAttribute(default=0)
    num_out = NumberAttribute(default=0)
    signed_out_to = UnicodeSetAttribute(null=True)
    notes = UnicodeAttribute(null=True)
