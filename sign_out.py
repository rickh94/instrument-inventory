import json

from common import setup_airtable
from responses import failure, success


def main(event, _context):
    """Sign out an instrument"""
    data = json.loads(event["body"])

    try:
        at = setup_airtable()
    except Exception as err:
        return failure(f"Could not connect to airtable: {err}")
    try:
        rec = at.update_by_field(
            "Number",
            data["instrumentNumber"],
            {"Assigned To": data["studentName"], "Location": data["school"]},
        )
        if not rec:
            return failure(
                {"errors": {"instrumentNumber": "Could not find matching instrument"}},
                400,
            )

        return success(
            f"Instrument: {rec['fields']['Number']} signed out to "
            f"{rec['fields']['Assigned To']} at {rec['fields']['Location']}."
        )

    except Exception as err:
        return failure(f"Something has gone wrong: {err}")
