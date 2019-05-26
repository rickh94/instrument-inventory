import os

from airtable import Airtable, params
from responses import failure


def validate_request(body: dict, required_fields: dict):
    """Validate that a request has all required data"""
    for field_key, field_name in required_fields.items():
        if not body.get(field_key):
            return failure({"errors": {field_key: f"{field_name} is required."}}, 400)
    return None


def setup_airtable():
    base_key = os.environ.get("AIRTABLE_BASE_KEY")
    table_name = os.environ.get("TABLE_NAME")
    return Airtable(base_key, table_name)


def make_filter_formula(field, value):
    return params.AirtableParams.FormulaParam.from_name_and_value(field, value)
