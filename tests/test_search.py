from unittest import mock

import pytest

import search


@pytest.fixture
def records():
    return [
        {"id": "rec0", "fields": {"Number": "1-605", "Assigned To": "Some Name"}},
        {"id": "rec1", "fields": {"Number": "1-601", "Assigned To": "Test Name"}},
        {"id": "rec2", "fields": {"Number": "1-602", "Assigned To": "Test Name2"}},
        {"id": "rec3", "fields": {"Number": "1-603", "Assigned To": "Random Person"}},
        {"id": "rec4", "fields": {"Number": "C1-505", "Assigned To": "A cellist"}},
        {"id": "rec5", "fields": {"Number": "V15-502", "Assigned To": "A violist"}},
        {
            "id": "rec6",
            "fields": {"Number": "V15-503", "Assigned To": "Another violist"},
        },
        {"id": "rec7", "fields": {"Number": "B1-502", "Assigned To": "Bass Player"}},
        {"id": "rec8", "fields": {"Number": "C2-508", "Assigned To": "Test Name"}},
    ]


@pytest.fixture
def pages(records):
    return [records[0:4], records[4:8], [records[8]]]


@pytest.fixture
def fake_airtable(pages):
    class FakeAirtable:
        def get_iter(self):
            for page in pages:
                yield page

    return FakeAirtable()


def test_search_helper_single(monkeypatch, fake_airtable, records):
    """Test the search helper function gets one result"""
    monkeypatch.setattr("search.setup_airtable", lambda: fake_airtable)

    results = search.search_helper("Number", "1-605")

    assert results == records[0]


def test_search_helper_multiple(monkeypatch, fake_airtable, records):
    """Test the search helper function gets all results"""
    monkeypatch.setattr("search.setup_airtable", lambda: fake_airtable)

    results = search.search_helper("Assigned To", "Test Name", multiple=True)

    assert set([rec["id"] for rec in results]) == {records[1]["id"], records[8]["id"]}


def test_search_helper_single_gets_only_one(monkeypatch, fake_airtable):
    """
    Test that the search helper gets only one result even when there are multiple
    matches.
    """
    monkeypatch.setattr("search.setup_airtable", lambda: fake_airtable)

    result = search.search_helper("Assigned To", "Test Name", multiple=False)

    assert not isinstance(result, list)
