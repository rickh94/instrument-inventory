from common import setup_airtable


def filter_helper(field_value_sets: dict):
    results = []
    at = setup_airtable()
    for rec in at.get_all(
        fields=["Number", "Instrument Type", "Size", "Location", "Assigned To"]
    ):
        if all(item in rec["fields"].items() for item in field_value_sets.items()):
            results.append(rec)

    return results
