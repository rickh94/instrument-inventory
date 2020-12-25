from app.strings import api_models
from app.strings.models import StringModel
from app.utils.common import update_items
from app.utils.decorators import something_might_go_wrong, load_model


@something_might_go_wrong
@load_model(api_models.UseStrings)
def use_strings(string_updates: api_models.UseStrings):
    return update_items(
        string_updates.string_updates,
        lambda x, y: x - y,
        StringModel,
        api_models.StringWithID,
    )


@something_might_go_wrong
@load_model(api_models.AddStrings)
def add_strings(string_updates: api_models.AddStrings):
    return update_items(
        string_updates.string_updates,
        lambda x, y: x + y,
        StringModel,
        api_models.StringWithID,
    )
