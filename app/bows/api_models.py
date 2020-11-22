from typing import List

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


class AddBow(BaseModel):
    id: str = Field(..., title="Bow ID", description="Unique id for the bow to add to")
    amount: int = Field(..., title="Number to add")


class UseBow(BaseModel):
    id: str = Field(..., title="Bow ID", description="Unique id of the bow to use")
    amount: int = Field(..., title="Number to use")


class AddBows(BaseModel):
    bow_updates: List[AddBow] = Field(..., title="List of bow updates")


class UseBows(BaseModel):
    bow_updates: List[UseBow] = Field(..., title="List of bow updates")
