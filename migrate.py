import json
import os
import time
import uuid

import pydantic
from airtable import Airtable

from app.utils import api_models
from app.utils.models import InstrumentModel
from app.utils.common import handle_photo


def setup_airtable():
    base_key = os.environ.get("AIRTABLE_BASE_KEY")
    table_name = os.environ.get("TABLE_NAME")
    return Airtable(base_key, table_name)


at = setup_airtable()


def main():
    items = at.get_all()
    for item in items:
        time.sleep(0.2)
        print("processing item", item["fields"]["Number"])
        photo_key = None
        if item["fields"].get("Photo"):
            photo_key = handle_photo(item["fields"]["Photo"][0]["url"])
        history = None
        if item["fields"].get("History"):
            history = json.dumps(item["fields"]["History"].split(", "))
        try:
            new_instrument = api_models.Instrument(
                id=str(uuid.uuid4),
                number=item["fields"]["Number"].strip(),
                size=item["fields"]["Size"].strip(),
                type=item["fields"]["Instrument Type"].strip(),
                location=item["fields"].get("Location", "Unknown").strip(),
                assignedTo=item["fields"].get("Assigned To", None),
                maintenanceNotes=item["fields"].get("Maintenance Notes", None),
                conditionNotes=item["fields"].get("Condition Notes", None),
                quality=item["fields"].get("Quality", None),
                condition=item["fields"].get("Condition", None),
                gifted=item["fields"].get("Gifted to student", False),
            )
            new_item = InstrumentModel(
                **new_instrument.dict(exclude={"photo", "history"}),
                photo=photo_key,
                history=history,
            )
            new_item.save()
        except KeyError as err:
            print(item["fields"].get("Number"), f"not migrated: {err}")
            continue


if __name__ == "__main__":
    main()
