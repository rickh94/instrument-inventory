from enum import Enum
from typing import List, Dict, Iterable

from pydantic import BaseModel, Field, AnyUrl, Json, ValidationError

from app.utils.common import MissingValue


class Todo(BaseModel):
    content: str = Field(
        ..., title="Content", description="The task to do", max_length=30
    )
    relevantInstrument: str = Field(
        None,
        title="Relevant Instrument",
        description="An instrument related to the task",
        max_length=10,
    )
    completed: bool = Field(
        False, title="Completed", description="Whether or not the task is completed"
    )


class TodoInDB(Todo):
    userId: str
    todoId: str


class TodoOut(Todo):
    todoId: str = Field(
        ..., title="Todo ID", description="The unique id of the todo in the database."
    )


class Size(str, Enum):
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
    sixteen_inch = '16"'
    sixteen_half_inch = '16.5"'
    seventeen_inch = '17"'
    na = "N/A"


class Location(str, Enum):
    union_baptist = "Union Baptist Church"
    westminster = "Westminster Presbyterian Church"
    vcs = "Village Charter School"
    online = "Online Program Participant"
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
    spoutu = "SproutU"
    cseix = "Christina Seix Academy"
    unknown = "Unknown"
    lost = "Lost"
    trash = "Trash"


class Type(str, Enum):
    violin = "Violin"
    viola = "Viola"
    violin_strung_as_viola = "Violin strung as viola"
    cello = "Cello"
    bass = "Bass"
    keyboard = "Keyboard"
    drum = "Drum"
    orff = "Orff Instrument"


class Instrument(BaseModel):
    class Config:
        use_enum_values = True

    number: str = Field(
        ...,
        title="Instrument Number",
        description="The inventory number of the instrument",
    )
    size: Size = Field(
        ...,
        title="Instrument Size",
        description="The fractional or inch size of the instrument",
    )
    type: Type = Field(
        ..., title="Instrument Type", description="What kind of instrument"
    )
    location: Location = Field(..., title="Instrument Location")
    assignedTo: str = Field(
        None, title="Assigned To", description="Who it is signed out to"
    )
    maintenanceNotes: str = Field(None, title="Maintenance Notes", max_length=200)
    conditionNotes: str = Field(None, title="Condition Notes", max_length=200)
    condition: int = Field(None, title="Condition", gte=0, lt=6)
    quality: int = Field(None, title="Quality", gte=0, lt=6)
    gifted: bool = Field(
        False,
        title="Gifted To Student",
        description="Whether it has been given permanently to"
        " the student it is assigned to.",
    )
    archived: bool = Field(
        False,
        title="Archived",
        description="An instrument that has been removed from inventory for some "
        "reason.",
    )


class InstrumentIn(Instrument):
    photo: AnyUrl = Field(
        None, title="Photo URL", description="URL to download photo from"
    )


class InstrumentWithID(Instrument):
    id: str = Field(
        ..., title="ID", description="The id of the instrument in the database"
    )


class InstrumentInDB(InstrumentWithID):
    photo: str = Field(None, title="Photo", description="Filename of the photo")
    history: Json[List[str]] = Field(None, title="History")


class InstrumentOut(InstrumentWithID):
    photoUrls: Dict[str, AnyUrl] = Field(
        None, title="Photo URLS", description="Download urls for instrument photos"
    )
    history: List[str] = Field(
        None, title="History", description="List of previous users"
    )


locations = {m.name: m.value for m in Location}
locations["none"] = None


def make_optional_enum(OriginalEnum: Enum, name: str):
    keys = {m.name: m.value for m in OriginalEnum}
    keys["none"] = None
    # noinspection PyArgumentList
    return Enum(name, keys)


TypeOptionalEnum = make_optional_enum(Type, "TypeOptionalEnum")
SizeOptionalEnum = make_optional_enum(Size, "SizeOptionalEnum")
LocationOptionalEnum = make_optional_enum(Location, "LocationOptionalEnum")


class InstrumentFilter(BaseModel):
    type: TypeOptionalEnum = Field(None, title="Instrument Type")
    size: SizeOptionalEnum = Field(None, title="Size")
    location: LocationOptionalEnum = Field(None, title="Location")
    notAssigned: bool = Field(False, title="Search only unassigned instruments")

    def generate_filter_string(self):
        filter_list = []
        if self.type:
            filter_list.append(f"(InstrumentModel.type == '{self.type.value}')")
        if self.size:
            filter_list.append(f"(InstrumentModel.size == '{self.size.value}')")
        if self.location:
            filter_list.append(f"(InstrumentModel.location == '{self.location.value}')")
        if self.notAssigned:
            pass
        # if self.notAssigned:
        #     filter_list.append(
        #         # "(InstrumentModel.assignedTo.does_not_exist())"
        #         # ' | InstrumentModel.assignedTo == "")'
        #     )
        if not filter_list:
            raise MissingValue("Must provide one of type, size, location, notAssigned")
        return " & ".join(filter_list)


class RetrieveSingle(BaseModel):
    number: str = Field(
        ...,
        title="Instrument Number",
        description="The number of the instrument to retrieve",
    )


class RetrieveMultiple(BaseModel):
    numbers: List[str] = Field(
        ...,
        title="Instrument Numbers",
        description="A list of instrument numbers to retrieve",
    )


class Search(BaseModel):
    term: str = Field(
        ...,
        title="Search Term",
        description="Instrument number or name to search assigned or history",
    )


class SignOut(BaseModel):
    class Config:
        use_enum_values = True

    number: str = Field(
        ..., title="Instrument Number", description="Instrument Number to sign out"
    )
    assignedTo: str = Field(
        None, title="Assigned To", description="Name of the Person to sign out to"
    )
    location: Location = Field(
        ..., title="Location", description="Primary location of instrument"
    )


class SignOutMultiple(BaseModel):
    class Config:
        use_enum_values = True

    instruments: List[SignOut] = Field(
        ...,
        title="Instrument assignments",
        description="A list of instrument numbers, students, and locations",
    )


def process_instrument_db_list(instruments: Iterable):
    instruments_db = [
        InstrumentInDB.parse_obj(ins.attribute_values) for ins in instruments
    ]
    instruments_out = [InstrumentOut.parse_obj(ins) for ins in instruments_db]
    return [ins.dict() for ins in instruments_out]


def process_all_instruments_list(
    instruments: Iterable,
) -> (List[dict], List[List[str]]):
    instruments_db = []
    instruments_failed = []
    for ins in instruments:
        try:
            instruments_db.append(InstrumentInDB.parse_obj(ins.attribute_values))
        except ValidationError as err:
            instruments_failed.append([ins.number, str(err)])
    # instruments_db = [
    #     InstrumentInDB.parse_obj(ins.attribute_values) for ins in instruments
    # ]
    instruments_out = [InstrumentOut.parse_obj(ins) for ins in instruments_db]
    return [ins.dict() for ins in instruments_out], instruments_failed


def process_todo_db_list(todos: Iterable):
    todos_db = [TodoInDB.parse_obj(todo.attribute_values) for todo in todos]
    todos_out = [TodoOut.parse_obj(todo) for todo in todos_db]
    return [todo.dict() for todo in todos_out]
