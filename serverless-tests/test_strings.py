import ujson


def test_create_string_minimal(run_sls_cmd, generate_event):
    event_body = {"type": "Violin", "size": "4/4", "string": "A"}
    event_path = generate_event(event_body)
    result_data = run_sls_cmd("create-string", event_path)

    assert result_data["statusCode"] == 201
    body = ujson.loads(result_data["body"])
    assert body["item"]["type"] == event_body["type"]
    assert body["item"]["size"] == event_body["size"]
    assert body["item"]["string"] == event_body["string"]
    assert body["item"]["count"] == 0


def test_create_string_with_count(run_sls_cmd, generate_event):
    event_body = {
        "type": "Cello",
        "size": "1/4",
        "string": "C",
        "count": 4,
    }
    result_data = run_sls_cmd("create-string", generate_event(event_body))

    assert result_data["statusCode"] == 201
    body = ujson.loads(result_data["body"])
    assert body["item"]["type"] == event_body["type"]
    assert body["item"]["size"] == event_body["size"]
    assert body["item"]["string"] == event_body["string"]
    assert body["item"]["count"] == 4


def test_string_create_missing_data(run_sls_cmd, generate_event):
    event_body = {
        "type": "Viola",
    }
    result_data = run_sls_cmd("create-string", generate_event(event_body))

    assert result_data["statusCode"] == 422


def test_string_create_already_exits(run_sls_cmd, generate_event):
    event_body = {"type": "Viola", "size": '12"', "string": "G"}
    event_path = generate_event(event_body)

    res1 = run_sls_cmd("create-string", event_path)
    res2 = run_sls_cmd("create-string", event_path)

    assert res1["statusCode"] == 201
    assert res2["statusCode"] == 400


def test_get_all_strings(run_sls_cmd, generate_event):
    result_data = run_sls_cmd("get-strings", generate_event())

    assert result_data["statusCode"] == 200


def test_use_strings(run_sls_cmd, generate_event):
    """Test using strings (subtracting)"""
    create_string1 = generate_event(
        {"type": "Violin", "size": "3/4", "count": 5, "string": "A"}, "string1"
    )
    create_string2 = generate_event(
        {"type": "Viola", "size": '12"', "count": 2, "string": "C"}, "string2"
    )

    string1_res = run_sls_cmd("create-string", create_string1)
    string2_res = run_sls_cmd("create-string", create_string2)

    assert string1_res["statusCode"] == 201
    assert string2_res["statusCode"] == 201

    string1_id = ujson.loads(string1_res["body"])["item"]["id"]
    string2_id = ujson.loads(string2_res["body"])["item"]["id"]

    event_path = generate_event(
        {
            "string_updates": [
                {"id": string1_id, "amount": 2},
                {"id": string2_id, "amount": 1},
            ]
        }
    )

    response = run_sls_cmd("use-strings", event_path)

    assert response["statusCode"] == 200
    body = ujson.loads(response["body"])
    assert len(body["updated"]) == 2
    assert len(body["failed"]) == 0


def test_add_strings(run_sls_cmd, generate_event):
    """Test adding strings (subtracting)"""
    create_string1 = generate_event(
        {"type": "Cello", "size": "3/4", "count": 3, "string": "D"}, "string1"
    )
    create_string2 = generate_event(
        {"type": "Bass", "size": "1/4", "count": 7, "string": "G"}, "string2"
    )

    string1_res = run_sls_cmd("create-string", create_string1)
    string2_res = run_sls_cmd("create-string", create_string2)

    assert string1_res["statusCode"] == 201
    assert string2_res["statusCode"] == 201

    string1_id = ujson.loads(string1_res["body"])["item"]["id"]
    string2_id = ujson.loads(string2_res["body"])["item"]["id"]

    event_path = generate_event(
        {
            "string_updates": [
                {"id": string1_id, "amount": 4},
                {"id": string2_id, "amount": 10},
            ]
        }
    )

    response = run_sls_cmd("add-strings", event_path)

    assert response["statusCode"] == 200
    body = ujson.loads(response["body"])
    assert len(body["updated"]) == 2
    assert len(body["failed"]) == 0
