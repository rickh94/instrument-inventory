from typing import List, Dict, Iterable

from pydantic import BaseModel, Schema, UrlStr, validator, ValidationError, Json
from enum import Enum

from app.utils.common import MissingValue


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
    hedgepath = "Hedgepath Middle School"
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
    history: Json[List[str]] = Schema(None, title="History")


class InstrumentOut(InstrumentWithID):
    photoUrls: Dict[str, UrlStr] = Schema(
        None, title="Photo URLS", description="Download urls for instrument photos"
    )
    history: List[str] = Schema(
        None, title="History", description="List of previous users"
    )


class InstrumentFilter(BaseModel):
    type: InstrumentTypeEnum = Schema(None, title="Instrument Type")
    size: InstrumentSizeEnum = Schema(None, title="Size")
    location: LocationEnum = Schema(None, title="Location")
    notAssigned: bool = Schema(False, title="Search only unassigned instruments")

    def generate_filter_string(self):
        filter_list = []
        if self.type:
            filter_list.append(f"(InstrumentModel.type == '{self.type}')")
        if self.size:
            filter_list.append(f"(InstrumentModel.size == '{self.size}')")
        if self.location:
            filter_list.append(f"(InstrumentModel.location == '{self.location}')")
        if self.notAssigned:
            filter_list.append(
                "(InstrumentModel.assignedTo.does_not_exist() | "
                'InstrumentModel.assignedTo == "")'
            )
        if not filter_list:
            raise MissingValue("Must provide one of type, size, location, notAssigned")
        return " & ".join(filter_list)


class RetrieveSingle(BaseModel):
    number: str = Schema(
        ...,
        title="Instrument Number",
        description="The number of the instrument to retrieve",
    )


class RetrieveMultiple(BaseModel):
    numbers: List[str] = Schema(
        ...,
        title="Instrument Numbers",
        description="A list of instrument numbers to retrieve",
    )


class Search(BaseModel):
    term: str = Schema(
        ...,
        title="Search Term",
        description="Instrument number or name to search assigned or history",
    )


class SignOut(BaseModel):
    class Config:
        use_enum_values = True

    number: str = Schema(
        ..., title="Instrument Number", description="Instrument Number to sign out"
    )
    assignedTo: str = Schema(
        ..., title="Assigned To", description="Name of the Person to sign out to"
    )
    location: LocationEnum = Schema(
        ..., title="Location", description="Primary location of instrument"
    )


def process_instrument_db_list(instruments: Iterable):
    instruments_db = [
        InstrumentInDB.parse_obj(ins.attribute_values) for ins in instruments
    ]
    instruments_out = [InstrumentOut.parse_obj(ins) for ins in instruments_db]
    return [ins.dict() for ins in instruments_out]


def process_todo_db_list(todos: Iterable):
    todos_db = [TodoInDB.parse_obj(todo.attribute_values) for todo in todos]
    todos_out = [TodoOut.parse_obj(todo) for todo in todos_db]
    return [todo.dict() for todo in todos_out]
