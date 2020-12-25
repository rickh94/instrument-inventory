from typing import List, Optional

from pydantic import Field
from pydantic.main import BaseModel


class Other(BaseModel):
    class Config:
        use_enum_values = True

    item: str = Field(..., title="Item", description="The name of the item in question")
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
