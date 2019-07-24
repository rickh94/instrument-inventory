import json
import subprocess
from pathlib import Path

import pytest


@pytest.fixture
def generate_event(tmp_path):
    def _generate(body: dict = None, name="event", path_parameters=None):
        event_path: Path = tmp_path / f"{name}.json"
        event_data = {
            "body": json.dumps(body),
            "requestContext": {"identity": {"cognitoIdentityId": "USER-SUB-1234"}},
            "pathParameters": path_parameters,
        }
        with event_path.open("w") as event_file:
            json.dump(event_data, event_file)
        return str(event_path.absolute())

    return _generate


@pytest.fixture
def instrument1(run_sls_cmd, generate_event):
    event_body = {
        "number": "1-602",
        "type": "Violin",
        "assignedTo": "Test Student",
        "location": "Grant Elementary School",
        "maintenanceNotes": "test maintenance",
        "conditionNotes": "test condition",
        "condition": 5,
        "quality": "3",
        "gifted": True,
        "size": "4/4",
        "photo": "https://unsplash.com/photos/uqKyeMaaAOQ/download?force=true",
    }
    event_path = generate_event(event_body, "instrument1")
    result_data = run_sls_cmd("create", event_path)
    body = json.loads(result_data["body"])

    return body["item"]


@pytest.fixture
def instrument2(run_sls_cmd, generate_event):
    event_body = {
        "number": "1-603",
        "type": "Violin",
        "assignedTo": "Test Student",
        "location": "Grant Elementary School",
        "size": "4/4",
    }

    event_path = generate_event(event_body, "instrument2")
    result_data = run_sls_cmd("create", event_path)
    body = json.loads(result_data["body"])

    return body["item"]


def instrument3(run_sls_cmd, generate_event):
    event_body = {
        "number": "1-603",
        "type": "Violin",
        "assignedTo": "Test Student",
        "location": "Grant Elementary School",
        "size": "4/4",
    }

    event_path = generate_event(event_body, "instrument2")
    result_data = run_sls_cmd("create", event_path)
    body = json.loads(result_data["body"])

    return body["item"]


def test_create_instrument_minimal(run_sls_cmd, generate_event):
    """Integration test for minimal instrument creation"""
    event_body = {
        "number": "1-601",
        "type": "Violin",
        "size": "4/4",
        "location": "Office",
    }
    event_path = generate_event(event_body)

    result_data = run_sls_cmd("create", event_path)

    assert result_data["statusCode"] == 201
    body = json.loads(result_data["body"])
    assert body["item"]["number"] == event_body["number"]
    assert body["item"]["type"] == event_body["type"]
    assert body["item"]["size"] == event_body["size"]
    assert body["item"]["location"] == event_body["location"]


def test_create_instrument_complete(run_sls_cmd, generate_event):
    """Integration test for full instrument creation"""
    event_body = {
        "number": "1-602",
        "type": "Violin",
        "assignedTo": "Test Student",
        "location": "Grant Elementary School",
        "maintenanceNotes": "test maintenance",
        "conditionNotes": "test condition",
        "condition": 5,
        "quality": "3",
        "gifted": True,
        "size": "4/4",
        "photo": "https://unsplash.com/photos/uqKyeMaaAOQ/download?force=true",
    }
    event_path = generate_event(event_body)

    result_data = run_sls_cmd("create", event_path)

    assert result_data["statusCode"] == 201
    body = json.loads(result_data["body"])
    for k, v in event_body.items():
        if k == "photo":
            continue
        if k == "quality":
            assert body["item"]["quality"] == int(event_body["quality"])
            continue
        assert body["item"][k] == v


def test_get_instrument(run_sls_cmd, generate_event, instrument1):
    """Integration test for getting an instrument"""
    path_parameters = {"id": instrument1["id"]}
    event_path = generate_event(path_parameters=path_parameters)

    result_data = run_sls_cmd("get", event_path)

    assert result_data["statusCode"] == 200
    body = json.loads(result_data["body"])
    assert body["number"] == instrument1["number"]


def test_get_all(run_sls_cmd, generate_event):
    """Integration test for getting all instruments"""
    event_path = generate_event()

    result_data = run_sls_cmd("get-all", event_path)

    assert result_data["statusCode"] == 200


def test_update_photo(run_sls_cmd, generate_event, instrument1):
    """Integration test for updating an instrument photo"""
    path_parameters = {"id": instrument1["id"]}
    event_body = {
        "photoUrl": "https://unsplash.com/photos/wPaBwop_rSo/download?force=true"
    }
    event_path = generate_event(body=event_body, path_parameters=path_parameters)

    result_data = run_sls_cmd("update-photo", event_path)

    assert result_data["statusCode"] == 200


def test_update_full(run_sls_cmd, generate_event, instrument1):
    """Integration test for updating an instrument"""
    path_parameters = {"id": instrument1["id"]}
    event_body = {
        "type": "Cello",
        "number": "C1-502",
        "size": "4/4",
        "location": "Office",
        "assignedTo": "Test Name",
        "condition": 4,
        "quality": 2,
        "conditionNotes": "test condition notes",
        "maintenanceNotes": "test maintenance notes",
        "gifted": True,
    }
    event_path = generate_event(body=event_body, path_parameters=path_parameters)

    result_data = run_sls_cmd("update-full", event_path)

    assert result_data["statusCode"] == 200


def test_delete(run_sls_cmd, generate_event, instrument1, make_sls_cmd):
    """Integration test for deleting an instrument"""
    path_parameters = {"id": instrument1["id"]}
    event_path = generate_event(path_parameters=path_parameters)

    result_data = run_sls_cmd("delete", event_path)

    assert result_data["statusCode"] == 204

    get_cmd = make_sls_cmd("get", event_path)
    get_output = subprocess.run(get_cmd, stdout=subprocess.PIPE)
    get_data = get_output.stdout.split(b"\n\n")[1]
    get_result = json.loads(get_data)

    assert get_result["statusCode"] == 404


def test_retrieve(run_sls_cmd, generate_event, instrument1):
    """Integration test for retrieving a single instrument."""
    event_body = {"number": instrument1["number"]}
    event_path = generate_event(body=event_body)

    result_data = run_sls_cmd("retrieve-single", event_path)

    assert result_data["statusCode"] == 200


def test_retrieve_multiple(run_sls_cmd, generate_event, instrument1, instrument2):
    """Integration test for retrieving multiple instruments"""
    event_body = {"numbers": [instrument1["number"], instrument2["number"]]}
    event_path = generate_event(body=event_body)

    result_data = run_sls_cmd("retrieve-multiple", event_path)

    assert result_data["statusCode"] == 200


def test_sign_out(run_sls_cmd, generate_event, instrument1):
    """Integration test for signing out an instrument"""
    event_body = {
        "number": instrument1["number"],
        "assignedTo": "Test Student",
        "location": "Grant Elementary School",
    }
    event_path = generate_event(body=event_body)

    result_data = run_sls_cmd("sign-out", event_path)

    assert result_data["statusCode"] == 200


def test_search_number(run_sls_cmd, generate_event, instrument1):
    """Integration test for searching by number"""
    event_body = {"term": instrument1["number"]}
    event_path = generate_event(body=event_body)

    result_data = run_sls_cmd("search-number", event_path)

    assert result_data["statusCode"] == 200


def test_search_assigned(run_sls_cmd, generate_event, instrument1):
    """Integration test for searching by assigned name"""
    event_body = {"term": instrument1["assignedTo"]}
    event_path = generate_event(body=event_body)

    result_data = run_sls_cmd("search-assigned", event_path)

    assert result_data["statusCode"] == 200


def test_search_assigned_history(run_sls_cmd, generate_event, instrument1):
    """Integration test for searching by assigned name"""
    event_body = {"term": instrument1["assignedTo"]}
    event_path = generate_event(body=event_body)

    result_data = run_sls_cmd("search-assigned-history", event_path)

    assert result_data["statusCode"] == 200


def test_filter_complete(run_sls_cmd, generate_event, instrument1):
    """Integration test for filtering"""
    event_body = {
        "type": "Violin",
        "size": "4/4",
        "location": "Office",
        "notAssigned": False,
    }
    event_path = generate_event(body=event_body)

    result_data = run_sls_cmd("filter", event_path)

    assert result_data["statusCode"] == 200


def test_filter_signed_out(run_sls_cmd, generate_event, instrument2):
    """Integration test for filtering signed out instruments"""
    event_path = generate_event()

    result_data = run_sls_cmd("filter-signed-out", event_path)
    print(result_data)

    assert result_data["statusCode"] == 200


def test_filter_gifted(run_sls_cmd, generate_event, instrument1):
    """Integration test for filtering gifted instruments"""
    event_path = generate_event()

    result_data = run_sls_cmd("filter-gifted", event_path)

    assert result_data["statusCode"] == 200