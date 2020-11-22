import ujson


def test_create_bow_minimal(run_sls_cmd, generate_event):
    event_body = {
        "type": "Violin",
        "size": "4/4",
    }
    event_path = generate_event(event_body)

    result_data = run_sls_cmd("create-bow", event_path)

    assert result_data["statusCode"] == 201
    body = ujson.loads(result_data["body"])
    assert body["item"]["type"] == event_body["type"]
    assert body["item"]["size"] == event_body["size"]
    assert body["item"].get("id", False)
    assert body["item"]["count"] == 0


def test_create_bow_with_count(run_sls_cmd, generate_event):
    event_body = {
        "type": "Violin",
        "size": "1/2",
        "count": 8,
    }
    event_path = generate_event(event_body)

    result_data = run_sls_cmd("create-bow", event_path)

    assert result_data["statusCode"] == 201
    body = ujson.loads(result_data["body"])
    assert body["item"]["type"] == event_body["type"]
    assert body["item"]["size"] == event_body["size"]
    assert body["item"]["count"] == 8
    assert body["item"].get("id", False)


def test_bow_create_missing_data(run_sls_cmd, generate_event):
    event_body = {"type": "Violin"}
    event_path = generate_event(event_body)

    result_data = run_sls_cmd("create-bow", event_path)

    assert result_data["statusCode"] == 422


def test_create_already_exists(run_sls_cmd, generate_event):
    event_body = {
        "type": "Cello",
        "size": "1/4",
    }

    event_path = generate_event(event_body)

    res1 = run_sls_cmd("create-bow", event_path)
    res2 = run_sls_cmd("create-bow", event_path)

    assert res1["statusCode"] == 201
    assert res2["statusCode"] == 400
