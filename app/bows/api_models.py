# class BowModel(Model):
#     """A Type of Bow"""
#
#     class Meta:
#         table_name = BOWS_TABLE_NAME
#
#     id = UnicodeAttribute(hash_key=True, default=str_uuid)
#     size = UnicodeAttribute()
#     type = UnicodeAttribute()
#     count = NumberAttribute(default=0)
from pydantic import Field
from pydantic.main import BaseModel

from app.utils.api_models import Size, Type


class Bow(BaseModel):
    class Config:
        use_enum_values = True

    size: Size = Field(..., title="Size", description="Instrument size of the bows")
    type: Type = Field(..., title="Type", description="Instrument type of the bows")
    count: int = Field(
        0, title="Count", description="How many of this type of bow do we have"
    )


class BowWithID(Bow):
    id: str = Field(..., title="ID", description="Unique id for the type of bow")
