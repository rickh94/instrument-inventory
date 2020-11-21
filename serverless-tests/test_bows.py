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
    assert body["item"].get("id", False)
    assert body["item"]["count"] == 8
