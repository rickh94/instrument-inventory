import os

from pydantic.schema import schema

from app.utils import api_models
from app.utils.decorators import something_might_go_wrong, no_args
from app.utils.responses import success


@something_might_go_wrong
@no_args
def main():
    model_schema = schema(
        [
            api_models.Todo,
            api_models.TodoOut,
            api_models.Instrument,
            api_models.InstrumentOut,
            api_models.InstrumentFilter,
            api_models.RetrieveSingle,
            api_models.RetrieveMultiple,
            api_models.Search,
            api_models.SignOut,
            api_models.SignOutMultiple,
        ],
        ref_prefix="#/components/schemas/"
    )["definitions"]
    schema_body = {
        "openapi": "3.0.2",
        "info": {"title": "Instrument Inventory", "version": os.getenv("VERSION", "1")},
        "components": {"schemas": model_schema},
    }

    return success(schema_body)
