import json
from pathlib import Path
from unittest import mock

import pytest

from app.utils.models import InstrumentModel

HERE = Path(__file__).parent
ROOT = HERE / ".."
MOCKS = ROOT / "mocks"


# ------------- EVENTS ----------------
def read_event(event_file_name):
    with Path(MOCKS / f"{event_file_name}.json").open("r") as event_file:
        return json.load(event_file)


@pytest.fixture
def retrieve_event():
    """Retrieve event"""
    return read_event("retrieve-event")


@pytest.fixture
def retrieve_multiple_event():
    return read_event("retrieve-multiple-event")


@pytest.fixture
def sign_out_event():
    return read_event("sign-out-event")


@pytest.fixture
def basic_create_event():
    return read_event("create-event")


@pytest.fixture
def full_create_event():
    return read_event("create-event-full")


@pytest.fixture
def search_number_event():
    return read_event("search-event")


@pytest.fixture
def search_assigned_event():
    return read_event("search-assigned-event")


@pytest.fixture
def get_event():
    return read_event("get-event")


@pytest.fixture
def fake_instrument():
    class FakeInstrument:
        def __init__(
            self,
            id_,
            number,
            size,
            type,
            location,
            assignedTo=None,
            maintenanceNotes=None,
            conditionNotes=None,
            condition=None,
            quality=None,
            rosin=False,
            bow=False,
            shoulderRestEndpinRest=False,
            ready=False,
            gifted=False,
            photo=None,
            airtableId=None,
            history=None,
        ):
            self.id = id_
            self.number = number
            self.size = size
            self.type = type
            self.location = location
            self.assignedTo = assignedTo
            self.maintenanceNotes = maintenanceNotes
            self.conditionNotes = conditionNotes
            self.condition = condition
            self.quality = quality
            self.rosin = rosin
            self.bow = bow
            self.shoulderRestEndpinRest = shoulderRestEndpinRest
            self.ready = ready
            self.gifted = gifted
            self.photo = photo
            self.airtableId = airtableId
            self.history = history
            self.save = mock.MagicMock()
            self.update = mock.MagicMock()
            self.delete = mock.MagicMock()
            self.refresh = mock.MagicMock()

        @property
        def attribute_values(self):
            return {
                "id": self.id,
                "number": self.number,
                "size": self.size,
                "type": self.type,
                "location": self.location,
                "assignedTo": self.assignedTo,
                "maintenanceNotes": self.maintenanceNotes,
                "conditionNotes": self.conditionNotes,
                "quality": self.quality,
                "rosin": self.rosin,
                "bow": self.bow,
                "shouldRestEndpinRest": self.shoulderRestEndpinRest,
                "ready": self.ready,
                "gifted": self.gifted,
                "photo": self.photo,
                "airtableId": self.airtableId,
                "history": self.history,
            }

    return FakeInstrument


# ----------------- DATA ------------------
@pytest.fixture
def records(fake_instrument):
    return [
        fake_instrument(
            id_="id0",
            number="1-605",
            assignedTo="Some Name",
            location="Office",
            size="4/4",
            type="Violin",
        ),
        fake_instrument(
            id_="rec1",
            number="1-601",
            assignedTo="Test Name",
            location="Office",
            size="4/4",
            type="Violin",
        ),
        fake_instrument(
            id_="rec2",
            number="1-602",
            assignedTo="Test Name2",
            location="Hedgepath Middle School",
            size="4/4",
            type="Violin",
        ),
        fake_instrument(
            id_="rec3",
            number="2-603",
            assignedTo="Random Person",
            location="Trenton High School",
            size="1/2",
            type="Violin",
        ),
        fake_instrument(
            id_="rec4",
            number="C1-505",
            assignedTo="A cellist",
            location="Grant Elementary School",
            size="4/4",
            type="Cello",
        ),
        fake_instrument(
            id_="rec5",
            number="V15-502",
            assignedTo="A violist",
            location="Storage",
            size='15"',
            type="Viola",
        ),
        fake_instrument(
            id_="rec6",
            number="V15-503",
            assignedTo="Another violist",
            location="Hedgepath Middle School",
            size='15"',
            type="Viola",
        ),
        fake_instrument(
            id_="rec7",
            number="B1-502",
            assignedTo="Bass Player",
            location="Storage",
            size="4/4",
            type="Bass",
        ),
        fake_instrument(
            id_="rec8",
            number="C2-508",
            assignedTo="Test Name",
            location="Storage",
            size="1/2",
            type="Cello",
        ),
        fake_instrument(
            id_="rec9", number="2-606", size="1/2", location="Storage", type="Violin"
        ),
    ]


@pytest.fixture
def pages(records):
    return [records[0:4], records[4:8], records[8:10]]


@pytest.fixture
def db_not_found():
    def _error(*_):
        raise InstrumentModel.DoesNotExist

    return _error


@pytest.fixture
def explode():
    def _error(*_):
        raise Exception

    return _error
