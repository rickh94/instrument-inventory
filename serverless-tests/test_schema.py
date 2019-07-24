import json


def test_schema(run_sls_cmd, generate_event):
    """Integration test for getting api schema."""
    event_path = generate_event()

    result_data = run_sls_cmd("schema", event_path)

    assert result_data["statusCode"] == 200
    body = json.loads(result_data["body"])
    assert "components" in body
