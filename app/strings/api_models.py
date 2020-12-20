from enum import Enum
from typing import List

from pydantic import BaseModel, Field

from app.utils.api_models import Size, Type


class StringOption(str, Enum):
    e_string = "E"
    a_string = "A"
    d_string = "D"
    g_string = "G"
    c_string = "C"


class String(BaseModel):
    class Config:
        use_enum_values = True

    type: Type = Field(..., title="Type", description="Type of instrument")
    size: Size = Field(..., title="Size", descripiton="Instrument size for the string")
    string: StringOption = Field(..., title="String", description="Which string it is")
    count: int = Field(
        0, title="Count", description="How many of this type of string we have"
    )


class StringWithID(String):
    id: str = Field(..., title="ID", description="Unique id for the type of string")


class AddString(BaseModel):
    id: str = Field(..., title="String ID", description="Unique id of string type")
    amount: int = Field(..., title="Bow ID", description="Number of the string to add")


class UseString(BaseModel):
    id: str = Field(..., title="String ID", description="Unique id of string type")
    amount: int = Field(..., title="Bow ID", description="Number of the string to use")


class AddStrings(BaseModel):
    string_updates: List[AddString] = Field(
        ..., title="String Updates", description="Ids and counts of strings to add"
    )


class UseStrings(BaseModel):
    string_updates: List[AddString] = Field(
        ..., title="String Updates", description="Ids and counts of strings to use"
    )
