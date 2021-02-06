from typing import List, Optional

from pydantic import Field
from pydantic.main import BaseModel


class Other(BaseModel):
    class Config:
        use_enum_values = True

    name: str = Field(..., title="Name", description="The name of the item in question")
    count: int = Field(
        ..., title="Count", description="How many of the item are in storage"
    )
    num_out: int = Field(
        0, title="Number Out", description="How many have been sent out to students"
    )
    signed_out_to: Optional[List[str]] = Field(
        None,
        title="Signed out to",
        description="Names of students that have one of the item signed out to them",
    )
    notes: Optional[str] = Field(None, title="Notes")


class OtherWithID(Other):
    id: str = Field(..., title="ID", description="Unique ID for this type of item.")


class AddOther(BaseModel):
    id: str = Field(..., title="Item ID")
    amount: int = Field(..., title="Number to add")


class UseOther(BaseModel):
    id: str = Field(..., title="Item ID")
    amount: int = Field(..., title="Number to use")


class SignOutItem(BaseModel):
    id: str = Field(..., title="Item ID")
    to: str = Field(
        ..., title="Sign Out To", description="The person to sign out the item to"
    )


class RetrieveItem(BaseModel):
    id: str = Field(..., title="Item ID")
    from_: str = Field(
        ...,
        title="Retrieved From",
        description="The person who returned the item",
        alias="from",
    )


class LostItem(BaseModel):
    id: str = Field(..., title="Item ID")
    from_: str = Field(
        ...,
        title="Lost From",
        description="The person who lost/brok the item",
        alias="from",
    )


class AddOthers(BaseModel):
    item_updates: List[AddOther] = Field(..., title="List of item updates")


class UseOthers(BaseModel):
    item_updates: List[UseOther] = Field(..., title="List of item updates")
