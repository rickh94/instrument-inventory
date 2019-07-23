import json
import subprocess
from pathlib import Path

import pytest


@pytest.fixture
def generate_event(tmp_path):
    def _generate(body: dict, event_name: str):
        event_path: Path = tmp_path / f"{event_name}.json"
        event_data = {
            "body": json.dumps(body),
            "requestContext": {"identity": {"cognitoIdentityId": "USER-SUB-1234"}},
        }
        with event_path.open("w") as event_file:
            json.dump(event_data, event_file)
        return str(event_path.absolute())

    return _generate


def test_create_instrument_minimal(make_sls_cmd, generate_event):
    event_body = {
        "number": "1-601",
        "type": "Violin",
        "size": "4/4",
        "location": "Office",
    }
    event_path = generate_event(event_body, "create_instrument_minimal")

    cmd = make_sls_cmd("create", event_path)
    result = subprocess.run(cmd, stdout=subprocess.PIPE)
    result_data = json.loads(result.stdout)

    print(result_data)
    assert result_data["statusCode"] == 201
    body = json.loads(result_data["body"])
    assert body["item"]["number"] == event_body["number"]
    assert body["item"]["type"] == event_body["type"]
    assert body["item"]["size"] == event_body["size"]
    assert body["item"]["location"] == event_body["location"]
