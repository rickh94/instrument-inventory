import pytest
import ujson
import uuid


@pytest.fixture
def item_factory(run_sls_cmd, generate_event):
    def _create_item(item_body):
        result_data = run_sls_cmd(
            "create-other", generate_event(item_body, str(uuid.uuid4()))
        )

        assert result_data["statusCode"] == 201

        return ujson.loads(result_data["body"])["item"]

    return _create_item


def test_create_other_minimal(run_sls_cmd, generate_event):
    event_body = {
        "name": "Rosin",
        "count": 20,
    }

    result_data = run_sls_cmd("create-other", generate_event(event_body))

    assert result_data["statusCode"] == 201
    body = ujson.loads(result_data["body"])
    assert body["item"]["name"] == "Rosin"
    assert body["item"]["count"] == 20
    assert body["item"]["signed_out_to"] is None
    assert body["item"]["notes"] is None
    assert body["item"]["location_counts"]["Storage"] == 20


def test_create_other_full(run_sls_cmd, generate_event):
    event_body = {
        "name": "Metronome",
        "count": 8,
        "signed_out_to": ["Test1", "Person Number2"],
        "notes": "Some cheap metronomes",
        "location_counts": {"Storage": 5},
    }

    result_data = run_sls_cmd("create-other", generate_event(event_body))

    print(result_data)
    assert result_data["statusCode"] == 201
    body = ujson.loads(result_data["body"])
    assert body["item"]["name"] == "Metronome"
    assert body["item"]["count"] == 8
    assert "Test1" in body["item"]["signed_out_to"]
    assert "Person Number2" in body["item"]["signed_out_to"]
    assert body["item"]["notes"] == "Some cheap metronomes"
    assert "Storage" in body["item"]["location_counts"]
    assert body["item"]["location_counts"]["Storage"] == 5


def test_create_other_missing_data(run_sls_cmd, generate_event):
    event_body = {"count": 4}

    result_data = run_sls_cmd("create-other", generate_event(event_body))

    assert result_data["statusCode"] == 422


def test_create_already_exists(run_sls_cmd, generate_event):
    event_body = {
        "name": "Music Stand",
        "count": 10,
    }

    res1 = run_sls_cmd("create-other", generate_event(event_body))
    res2 = run_sls_cmd("create-other", generate_event(event_body))

    assert res1["statusCode"] == 201
    assert res2["statusCode"] == 400


def test_get_all_other(run_sls_cmd, generate_event):
    result_data = run_sls_cmd("get-other", generate_event())

    assert result_data["statusCode"] == 200


def test_use_other(run_sls_cmd, generate_event, item_factory):
    item1_id = item_factory({"name": "Test1", "count": 4})["id"]
    item2_id = item_factory({"name": "Test2", "count": 8})["id"]

    event_path = generate_event(
        {
            "item_updates": [
                {"id": item1_id, "amount": 2},
                {"id": item2_id, "amount": 5},
            ]
        }
    )

    response = run_sls_cmd("use-other", event_path)

    assert response["statusCode"] == 200
    body = ujson.loads(response["body"])
    assert len(body["updated"]) == 2
    assert len(body["failed"]) == 0


def test_add_other(run_sls_cmd, generate_event, item_factory):
    counts = [4, 8]
    updates = [2, 5]
    item_ids = ["", ""]

    item_ids[0] = item_factory({"name": "Test5", "count": counts[0]})["id"]
    item_ids[1] = item_factory({"name": "Test6", "count": counts[1]})["id"]

    event_path = generate_event(
        {
            "item_updates": [
                {"id": item_ids[0], "amount": updates[0]},
                {"id": item_ids[1], "amount": updates[1]},
            ]
        }
    )

    response = run_sls_cmd("add-other", event_path)

    assert response["statusCode"] == 200
    body = ujson.loads(response["body"])
    assert len(body["updated"]) == 2
    assert len(body["failed"]) == 0
    for item in body["updatedItems"]:
        if item["id"] == item_ids[0]:
            assert item["location_counts"]["Storage"] == counts[0] + updates[0]
        elif item["id"] == item_ids[1]:
            assert item["location_counts"]["Storage"] == counts[1] + updates[1]


def test_move_some_other(run_sls_cmd, generate_event, item_factory):
    count = 4
    update = 2
    item_id = item_factory({"name": "test7", "count": count})["id"]

    event_path = generate_event(
        {
            "id": item_id,
            "count": update,
            "from_location": "Storage",
            "to_location": "Westminster Presbyterian Church",
        }
    )

    response = run_sls_cmd("move-other", event_path)

    print(response)
    assert response["statusCode"] == 200
    body = ujson.loads(response["body"])
    assert body["item"]["location_counts"]["Storage"] == count - update
    assert body["item"]["location_counts"]["Westminster Presbyterian Church"] == update


def test_move_all_other(run_sls_cmd, generate_event, item_factory):
    count = 20
    update = 10
    create_item = {
        "name": "Test8",
        "count": count,
        "location_counts": {
            "Storage": 5,
            "Westminster Presbyterian Church": 10,
            "Office": 5,
        },
    }
    item_id = item_factory(create_item)["id"]

    event_path = generate_event(
        {
            "id": item_id,
            "count": update,
            "from_location": "Westminster Presbyterian Church",
            "to_location": "Storage",
        }
    )

    response = run_sls_cmd("move-other", event_path)

    assert response["statusCode"] == 200
    body = ujson.loads(response["body"])
    assert (
        body["item"]["location_counts"]["Storage"]
        == create_item["location_counts"]["Storage"] + update
    )
    assert (
        body["item"]["location_counts"]["Westminster Presbyterian Church"]
        == create_item["location_counts"]["Westminster Presbyterian Church"] - update
    )
    assert (
        body["item"]["location_counts"]["Office"]
        == create_item["location_counts"]["Office"]
    )


def test_move_too_many_other(run_sls_cmd, generate_event, item_factory):
    count = 20
    update = 25
    create_item = {
        "name": "Test9",
        "count": count,
        "location_counts": {
            "Storage": 5,
            "Westminster Presbyterian Church": 10,
            "Office": 5,
        },
    }
    item_id = item_factory(create_item)["id"]

    event_path = generate_event(
        {
            "id": item_id,
            "count": update,
            "from_location": "Westminster Presbyterian Church",
            "to_location": "Storage",
        }
    )

    response = run_sls_cmd("move-other", event_path)

    assert response["statusCode"] == 400


def test_move_more_than_location_other(run_sls_cmd, generate_event, item_factory):
    count = 20
    update = 11
    create_item = {
        "name": "Test10",
        "count": count,
        "location_counts": {
            "Storage": 5,
            "Westminster Presbyterian Church": 10,
            "Office": 5,
        },
    }
    item_id = item_factory(create_item)["id"]

    event_path = generate_event(
        {
            "id": item_id,
            "count": update,
            "from_location": "Westminster Presbyterian Church",
            "to_location": "Storage",
        }
    )

    response = run_sls_cmd("move-other", event_path)

    assert response["statusCode"] == 400
