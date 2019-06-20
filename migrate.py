import time
import uuid

from lib.models import InstrumentModel
from lib.common import setup_airtable, handle_photo

at = setup_airtable()


def main():
    items = at.get_all()
    for item in items:
        time.sleep(0.2)
        print("processing item", item["fields"]["Number"])
        photo_key = None
        if item["fields"].get("Photo"):
            photo_key = handle_photo(item["fields"]["Photo"][0]["url"])
        print(photo_key)
        history = None
        if item["fields"].get("History"):
            history = set(item["fields"]["History"].split(", "))
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
                history=history,
            )
            new_item.save()
        except KeyError as err:
            print(item["fields"].get("Number"), f"not migrated: {err}")
            continue


if __name__ == "__main__":
    main()
