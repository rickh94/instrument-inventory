from typing import List, Dict

from pydantic import BaseModel, Schema, UrlStr
from enum import Enum


class Todo(BaseModel):
    content: str = Schema(
        ..., title="Content", description="The task to do", max_length=30
    )
    relevantInstrument: str = Schema(
        None,
        title="Relevant Instrument",
        description="An instrument related to the task",
        max_length=10,
    )
    completed: bool = Schema(
        False, title="Completed", description="Whether or not the task is completed"
    )


class TodoInDB(Todo):
    userId: str
    todoId: str


class TodoOut(Todo):
    todoId: str = Schema(
        ..., title="Todo ID", description="The unique id of the todo in the database."
    )


class InstrumentSizeEnum(str, Enum):
    sixteenth = "1/16"
    tenth = "1/10"
    eighth = "1/8"
    quarter = "1/4"
    half = "1/2"
    three_quarter = "3/4"
    seven_eights = "7/8"
    full = "4/4"
    nine_inch = '9"'
    ten_inch = '10"'
    eleven_inch = '11"'
    twelve_inch = '12"'
    thirteen_inch = '13"'
    fourteen_inch = '14"'
    fifteen_inch = '15"'
    fifteen_half_inch = '15.5"'
    sixteen_inch = '16.5"'
    seventeen_inch = '17"'


class LocationEnum(str, Enum):
    grant = "Grant Elementary School"
    hedgepath = "Hedgepath Elementary School"
    wilson = "Wilson Elementary School"
    high = "Trenton High School"
    columbus = "Columbus Elementary School"
    office = "Office"
    storage = "Storage"
    trade = "Trade"
    maintenance = "Maintenance"
    transit = "Transit"


class InstrumentTypeEnum(str, Enum):
    violin = "Violin"
    viola = "Viola"
    violin_strung_as_viola = "Violin strung as viola"
    cello = "Cello"
    bass = "Bass"


class Instrument(BaseModel):
    class Config:
        use_enum_values = True

    number: str = Schema(
        ...,
        title="Instrument Number",
        description="The inventory number of the instrument",
    )
    size: InstrumentSizeEnum = Schema(
        ...,
        title="Instrument Size",
        description="The fractional or inch size of the instrument",
    )
    type: InstrumentTypeEnum = Schema(
        ..., title="Instrument Type", description="What kind of instrument"
    )
    location: LocationEnum = Schema(..., title="Instrument Location")
    assignedTo: str = Schema(
        None, title="Assigned To", description="Who it is signed out to"
    )
    maintenanceNotes: str = Schema(None, title="Maintenance Notes", max_length=200)
    conditionNotes: str = Schema(None, title="Condition Notes", max_length=200)
    condition: int = Schema(None, title="Condition", gt=0, lt=6)
    quality: int = Schema(None, title="Condition", gt=0, lt=6)
    gifted: bool = Schema(
        False,
        title="Gifted",
        description="Whether it has been given permanently to"
        " the student it is assigned to.",
    )


class InstrumentIn(Instrument):
    photo: UrlStr = Schema(
        None, title="Photo URL", description="URL to download photo from"
    )


class InstrumentWithID(Instrument):
    id: str = Schema(
        ..., title="ID", description="The id of the instrument in the database"
    )


class InstrumentInDB(InstrumentWithID):
    photo: str = Schema(None, title="Photo", description="Filename of the photo")
    history_json: str = Schema(None, title="History")


class InstrumentOut(InstrumentWithID):
    photoUrls: Dict[str, UrlStr] = Schema(
        None, title="Photo URLS", description="Download urls for instrument photos"
    )
    history: List[str] = Schema(
        [], title="History", description="List of previous users"
    )
