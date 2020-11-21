from unittest import mock

import app.bows.create


def test_bow_create_successful(monkeypatch, bow_create_event):
    """Test a bow creation event"""
    bow_mock = mock.MagicMock()
    created_item = mock.MagicMock()
    created_item.attribute_values = {
        "id": "fakeuuid",
        "type": "Violin",
        "size": "4/4",
        "count": 0,
    }
    created_item.type = "Violin"
    created_item.id = "fakeuuid"
    created_item.size = "4/4"
    created_item.count = 0
    bow_mock.scan.return_value = []
    bow_mock.return_value = created_item

    monkeypatch.setattr("app.bows.create.BowModel", bow_mock)

    response = app.bows.create.main(bow_create_event, {})

    bow_mock.assert_called_with(type="Violin", size="4/4", count=0)
    created_item.save.assert_called()

    assert response["statusCode"] == 201
