import json
from unittest import mock


import search


# def test_search_helper_single(monkeypatch, fake_airtable, records):
#     """Test the search helper function gets one result"""
#     monkeypatch.setattr("search.setup_airtable", lambda: fake_airtable)
#
#     results = search.search_helper("Number", "1-605")
#
#     assert results == records[0]


def test_search_helper_multiple(monkeypatch, fake_airtable, records):
    """Test the search helper function gets all results"""
    monkeypatch.setattr("search.setup_airtable", lambda: fake_airtable)

    results = search.search_helper("Assigned To", "Test Name", multiple=True)

    assert {rec["id"] for rec in results} == {records[1]["id"], records[8]["id"]}


def test_search_helper_single_gets_only_one(monkeypatch, fake_airtable):
    """
    Test that the search helper gets only one result even when there are multiple
    matches.
    """
    monkeypatch.setattr("search.setup_airtable", lambda: fake_airtable)

    result = search.search_helper("Assigned To", "Test Name", multiple=False)

    assert not isinstance(result, list)


def test_search_helper_partial_matches(monkeypatch, fake_airtable, records):
    """Test that the search helper returns partial patches"""
    monkeypatch.setattr("search.setup_airtable", lambda: fake_airtable)

    results = search.search_helper("Assigned To", "Name", multiple=True, exact=False)

    assert len(results) == 4
    assert {rec["id"] for rec in results} == {
        records[0]["id"],
        records[1]["id"],
        records[2]["id"],
        records[8]["id"],
    }


def test_search_number(monkeypatch, search_number_event):
    """Test searching for an instrument number"""
    found = {
        "id": "rec15",
        "fields": {
            "Number": "1-201",
            "Instrument Type": "violin",
            "Assigned To": "Test Name",
        },
    }
    at_mock = mock.MagicMock()
    at_mock.get_all.return_value = found
    monkeypatch.setattr("search.setup_airtable", lambda: at_mock)

    response = search.number(search_number_event, {})

    at_mock.get_all.assert_called_with(formula="{Number}='1-201'")

    assert response["statusCode"] == 200
    assert response["body"] == json.dumps(found)


def test_search_number_not_found(monkeypatch, search_number_event):
    """Test searching for an instrument number"""
    found = []
    at_mock = mock.MagicMock()
    at_mock.get_all.return_value = found
    monkeypatch.setattr("search.setup_airtable", lambda: at_mock)

    response = search.number(search_number_event, {})

    at_mock.get_all.assert_called_with(formula="{Number}='1-201'")

    assert response["statusCode"] == 404


def test_search_number_bad_request():
    """Test request missing data returns bad request"""
    response = search.number({"body": "{}"}, {})

    assert response["statusCode"] == 400


def test_search_assigned(monkeypatch, search_assigned_event, records):
    """Test searching for a student name"""
    found = [records[1], records[2], records[8]]
    search_helper_mock = mock.MagicMock()
    search_helper_mock.return_value = found
    monkeypatch.setattr("search.search_helper", search_helper_mock)

    response = search.assigned(search_assigned_event, {})

    search_helper_mock.assert_called_with(
        "Assigned To", "Test Name", multiple=True, exact=False
    )
    assert response["statusCode"] == 200
    assert response["body"] == json.dumps(found)


def test_search_assigned_bad_request():
    """Test searching for a name missing data returns bad request"""
    response = search.assigned({"body": "{}"}, {})

    assert response["statusCode"] == 400
