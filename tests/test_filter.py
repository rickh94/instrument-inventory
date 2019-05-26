import pytest

import filter


def _result_id_set(records):
    return {rec["id"] for rec in records}


def test_filter_by_instrument(monkeypatch, fake_airtable, records):
    """Test the filter helper function filters by instrument"""
    monkeypatch.setattr("filter.setup_airtable", lambda: fake_airtable)

    results = filter.filter_helper({"Instrument Type": "violin"})

    assert _result_id_set(results) == _result_id_set([*records[0:4], records[9]])


def test_filter_by_location(monkeypatch, fake_airtable, records):
    """Test the filter helper function filters by location"""
    monkeypatch.setattr("filter.setup_airtable", lambda: fake_airtable)

    results = filter.filter_helper({"Location": "office"})

    assert _result_id_set(results) == _result_id_set(records[0:2])


def test_filter_by_size(monkeypatch, fake_airtable, records):
    """Test the filter helper function filters by size"""
    monkeypatch.setattr("filter.setup_airtable", lambda: fake_airtable)

    results = filter.filter_helper({"Size": "4/4"})

    assert _result_id_set(results) == _result_id_set(
        [records[0], records[1], records[2], records[4], records[7]]
    )


def test_filter_more_complex(monkeypatch, fake_airtable, records):
    """Test a more complex example for the helper function"""
    monkeypatch.setattr("filter.setup_airtable", lambda: fake_airtable)

    results = filter.filter_helper({"Instrument Type": "cello", "Size": "1/2"})

    assert _result_id_set(results) == _result_id_set([records[8]])


def test_filter_helper_everything(monkeypatch, fake_airtable, records):
    """Test a full example"""
    monkeypatch.setattr("filter.setup_airtable", lambda: fake_airtable)

    results = filter.filter_helper(
        {"Instrument Type": "violin", "Size": "1/2", "Location": "Storage"}
    )

    assert _result_id_set(results) == _result_id_set([records[9]])


def test_filter_no_results(monkeypatch, fake_airtable, records):
    """Test an example that returns nothing"""
    monkeypatch.setattr("filter.setup_airtable", lambda: fake_airtable)

    results = filter.filter_helper({"Instrument Type": "bass", "Size": "1/10"})

    assert results == []
