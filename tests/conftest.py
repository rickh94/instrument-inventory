import json
from pathlib import Path

import pytest

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


# ----------------- DATA ------------------
@pytest.fixture
def records():
    return [
        {
            "id": "rec0",
            "fields": {
                "Number": "1-605",
                "Assigned To": "Some Name",
                "Location": "office",
                "Size": "4/4",
                "Instrument Type": "violin",
            },
        },
        {
            "id": "rec1",
            "fields": {
                "Number": "1-601",
                "Assigned To": "Test Name",
                "Location": "office",
                "Size": "4/4",
                "Instrument Type": "violin",
            },
        },
        {
            "id": "rec2",
            "fields": {
                "Number": "1-602",
                "Assigned To": "Test Name2",
                "Location": "Hedgepath Middle School",
                "Size": "4/4",
                "Instrument Type": "violin",
            },
        },
        {
            "id": "rec3",
            "fields": {
                "Number": "2-603",
                "Assigned To": "Random Person",
                "Location": "Trenton High School",
                "Size": "1/2",
                "Instrument Type": "violin",
            },
        },
        {
            "id": "rec4",
            "fields": {
                "Number": "C1-505",
                "Assigned To": "A cellist",
                "Location": "Grant Elementary School",
                "Size": "4/4",
                "Instrument Type": "cello",
            },
        },
        {
            "id": "rec5",
            "fields": {
                "Number": "V15-502",
                "Assigned To": "A violist",
                "Location": "Storage",
                "Size": '15"',
                "Instrument Type": "viola",
            },
        },
        {
            "id": "rec6",
            "fields": {
                "Number": "V15-503",
                "Assigned To": "Another violist",
                "Location": "Hedgepath Middle School",
                "Size": '15"',
                "Instrument Type": "viola",
            },
        },
        {
            "id": "rec7",
            "fields": {
                "Number": "B1-502",
                "Assigned To": "Bass Player",
                "Location": "Storage",
                "Size": "4/4",
                "Instrument Type": "bass",
            },
        },
        {
            "id": "rec8",
            "fields": {
                "Number": "C2-508",
                "Assigned To": "Test Name",
                "Location": "Storage",
                "Size": "1/2",
                "Instrument Type": "cello",
            },
        },
        {
            "id": "rec9",
            "fields": {
                "Number": "2-606",
                "Size": "1/2",
                "Location": "Storage",
                "Instrument Type": "violin",
            },
        },
    ]


@pytest.fixture
def pages(records):
    return [records[0:4], records[4:8], records[8:10]]


@pytest.fixture
def fake_airtable(pages, records):
    class FakeAirtable:
        @staticmethod
        def get_iter():
            for page in pages:
                yield page

        @staticmethod
        def get_all(**kwargs):
            return records

    return FakeAirtable()
