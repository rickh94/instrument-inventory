from app.strings import api_models
from app.strings.models import StringModel
from app.utils.common import update_items
from app.utils.decorators import something_might_go_wrong, load_model
from app.utils.responses import success


def update_strings(string_updates, update_func):
    results = {"updated": [], "failed": [], "updatedItems": []}
    for item in string_updates.string_updates:
        found = list(StringModel.query(item.id))
        if not found:
            results["failed"].append(item.id)
        string = found[0]
        string.count = update_func(string.count, item.amount)
        if string.count < 0:
            string.count = 0
        string.save()
        string.refresh()
        results["updated"].append(string.id)
        results["updatedItems"].append(
            api_models.StringWithID.parse_obj(string.attribute_values).dict()
        )
    return success(results)


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
