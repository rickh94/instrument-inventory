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
    """Test that creating a bow with missing info fails"""
    event_body = {"type": "Violin"}
    event_path = generate_event(event_body)

    result_data = run_sls_cmd("create-bow", event_path)

    assert result_data["statusCode"] == 422


def test_create_already_exists(run_sls_cmd, generate_event):
    """Test that creating a bow that already exists fails"""
    event_body = {
        "type": "Cello",
        "size": "1/4",
    }

    event_path = generate_event(event_body)

    res1 = run_sls_cmd("create-bow", event_path)
    res2 = run_sls_cmd("create-bow", event_path)

    assert res1["statusCode"] == 201
    assert res2["statusCode"] == 400


def test_get_all_bows(run_sls_cmd, generate_event):
    """Test getting all bows from the database"""
    event_path = generate_event()

    result_data = run_sls_cmd("get-bows", event_path)

    assert result_data["statusCode"] == 200


def test_use_bows(run_sls_cmd, generate_event):
    """Test using bows (subtracting)"""
    create_bow1 = generate_event({"type": "Violin", "size": "3/4", "count": 5}, "bow1")
    create_bow2 = generate_event({"type": "Viola", "size": '12"', "count": 2}, "bow2")

    bow1_res = run_sls_cmd("create-bow", create_bow1)
    bow2_res = run_sls_cmd("create-bow", create_bow2)

    assert bow1_res["statusCode"] == 201
    assert bow2_res["statusCode"] == 201

    bow1_id = ujson.loads(bow1_res["body"])["item"]["id"]
    bow2_id = ujson.loads(bow2_res["body"])["item"]["id"]

    event_path = generate_event(
        {"bow_updates": [{"id": bow1_id, "amount": 2}, {"id": bow2_id, "amount": 1}]}
    )

    response = run_sls_cmd("use-bows", event_path)

    assert response["statusCode"] == 200
    body = ujson.loads(response["body"])
    assert len(body["updated"]) == 2
    assert len(body["failed"]) == 0


def test_add_bows(run_sls_cmd, generate_event):
    """Test adding bows"""
    create_bow1 = generate_event({"type": "Cello", "size": "3/4", "count": 3}, "bow1")
    create_bow2 = generate_event({"type": "Bass", "size": "1/4", "count": 7}, "bow2")

    bow1_res = run_sls_cmd("create-bow", create_bow1)
    bow2_res = run_sls_cmd("create-bow", create_bow2)

    assert bow1_res["statusCode"] == 201
    assert bow2_res["statusCode"] == 201

    bow1_id = ujson.loads(bow1_res["body"])["item"]["id"]
    bow2_id = ujson.loads(bow2_res["body"])["item"]["id"]

    event_path = generate_event(
        {"bow_updates": [{"id": bow1_id, "amount": 4}, {"id": bow2_id, "amount": 10}]}
    )

    response = run_sls_cmd("add-bows", event_path)

    assert response["statusCode"] == 200
    body = ujson.loads(response["body"])
    assert len(body["updated"]) == 2
    assert len(body["failed"]) == 0
