import json

from common import setup_airtable, move_instrument
from responses import failure, success


def main(event, _context):
    """Sign out an instrument"""
    data = json.loads(event["body"])

    try:
        at = setup_airtable()
    except Exception as err:
        return failure(f"Could not connect to airtable: {err}")
    try:
        rec = move_instrument(
            data["instrumentNumber"], at, data["assignedTo"], data["location"]
        )
        if not rec:
            return failure(
                {"errors": {"instrumentNumber": "Could not find matching instrument"}},
                400,
            )

        return success(
            {
                "message": f"Instrument: {rec['fields']['Number']} signed out to "
                f"{rec['fields']['Assigned To']} at {rec['fields']['Location']}.",
                "id": rec["id"],
            }
        )

    except Exception as err:
        print(err)
        return failure(f"Something has gone wrong: {err}")
