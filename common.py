import os

from airtable import Airtable


def setup_airtable():
    base_key = os.environ.get("AIRTABLE_BASE_KEY")
    table_name = os.environ.get("TABLE_NAME")
    return Airtable(base_key, table_name)
