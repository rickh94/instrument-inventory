import uuid

import boto3

from models import InstrumentModel
from common import setup_airtable, handle_photo

at = setup_airtable()
s3 = boto3.client("s3")


def get_items():
    return at.get_all()


if __name__ == "__main__":
    items = at.get_all()
    for item in items:
        print("processing item", item["fields"]["Number"])
        photo_key = None
        if item["fields"].get("Photo"):
            photo_key = handle_photo(item["fields"]["Photo"][0]["url"])
        print(photo_key)
        try:
            new_item = InstrumentModel(
                str(uuid.uuid4()),
                number=item["fields"]["Number"],
                size=item["fields"]["Size"],
                type=item["fields"]["Instrument Type"],
                location=item["fields"].get("Location", "Unknown"),
                assignedTo=item["fields"].get("Assigned To", None),
                maintenanceNotes=item["fields"].get("Maintenance Notes", None),
                conditionNotes=item["fields"].get("Condition Notes", None),
                quality=item["fields"].get("Quality", None),
                condition=item["fields"].get("Condition", None),
                rosin=item["fields"].get("Rosin", False),
                bow=item["fields"].get("Bow", False),
                shoulderRestEndpinRest=item["fields"].get(
                    "Shoulder Rest/Endpin Rest", False
                ),
                ready=item["fields"].get("Ready To Go", False),
                gifted=item["fields"].get("Gifted to student", False),
                airtableId=item["id"],
                photo=photo_key,
            )
            new_item.save()
        except KeyError:
            continue
