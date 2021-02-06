import ujson


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
    assert body["item"]["num_out"] == 0
    assert body["item"]["signed_out_to"] is None
    assert body["item"]["notes"] is None


def test_create_other_full(run_sls_cmd, generate_event):
    event_body = {
        "name": "Metronome",
        "count": 8,
        "num_out": 5,
        "signed_out_to": ["Test1", "Person Number2"],
        "notes": "Some cheap metronomes",
    }

    result_data = run_sls_cmd("create-other", generate_event(event_body))

    assert result_data["statusCode"] == 201
    body = ujson.loads(result_data["body"])
    assert body["item"]["name"] == "Metronome"
    assert body["item"]["count"] == 8
    assert body["item"]["num_out"] == 5
    assert "Test1" in body["item"]["signed_out_to"]
    assert "Person Number2" in body["item"]["signed_out_to"]
    assert body["item"]["notes"] == "Some cheap metronomes"


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


def test_use_other(run_sls_cmd, generate_event):
    create_item1 = {"name": "Test1", "count": 4}
    create_item2 = {"name": "Test2", "count": 8}

    item1_res = run_sls_cmd("create-other", generate_event(create_item1))
    item2_res = run_sls_cmd("create-other", generate_event(create_item2))

    assert item1_res["statusCode"] == 201
    assert item2_res["statusCode"] == 201

    item1_id = ujson.loads(item2_res["body"])["item"]["id"]
    item2_id = ujson.loads(item2_res["body"])["item"]["id"]

    event_path = generate_event(
        {"item_updates": [{"id": item1_id, "amount": 2}, {"id": item2_id, "amount": 5}]}
    )

    response = run_sls_cmd("use-other", event_path)

    assert response["statusCode"] == 200
    body = ujson.loads(response["body"])
    assert len(body["updated"]) == 2
    assert len(body["failed"]) == 0


def test_add_other(run_sls_cmd, generate_event):
    create_item1 = {"name": "Test3", "count": 4}
    create_item2 = {"name": "Test4", "count": 8}

    item1_res = run_sls_cmd("create-other", generate_event(create_item1, "item1"))
    item2_res = run_sls_cmd("create-other", generate_event(create_item2, "item2"))

    assert item1_res["statusCode"] == 201
    assert item2_res["statusCode"] == 201

    item1_id = ujson.loads(item2_res["body"])["item"]["id"]
    item2_id = ujson.loads(item2_res["body"])["item"]["id"]

    event_path = generate_event(
        {"item_updates": [{"id": item1_id, "amount": 2}, {"id": item2_id, "amount": 5}]}
    )

    response = run_sls_cmd("add-other", event_path)

    assert response["statusCode"] == 200
    body = ujson.loads(response["body"])
    assert len(body["updated"]) == 2
    assert len(body["failed"]) == 0
