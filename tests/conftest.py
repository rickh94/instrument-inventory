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
