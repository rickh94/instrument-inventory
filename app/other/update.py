from app.other import api_models
from app.other.models import OtherModel
from app.utils.common import update_items
from app.utils.decorators import something_might_go_wrong, load_model
from app.utils.responses import not_found, success, failure


@something_might_go_wrong
@load_model(api_models.UseOthers)
def use_items(item_updates: api_models.UseOthers):
    return update_items(
        item_updates.item_updates,
        lambda x, y: x - y,
        OtherModel,
        api_models.OtherWithID,
    )


@something_might_go_wrong
@load_model(api_models.AddOthers)
def add_items(item_updates: api_models.AddOthers):
    return update_items(
        item_updates.item_updates,
        lambda x, y: x + y,
        OtherModel,
        api_models.OtherWithID,
    )


@something_might_go_wrong
@load_model(api_models.SignOutItem)
def sign_out(sign_out_item: api_models.SignOutItem):
    found = list(OtherModel.query(sign_out_item.id))
    if not found:
        return not_found()

    found_item: OtherModel = found[0]
    if not found_item.location_counts:
        found_item.location_counts = {}
    if "Storage" not in found_item.location_counts:
        found_item.location_counts["Storage"] = 0
    elif found_item.location_counts["Storage"] >= 1:
        found_item.location_counts["Storage"] -= 1
    if not found_item.signed_out_to:
        found_item.signed_out_to = []
    found_item.signed_out_to.append(sign_out_item.to)
    found_item.save()
    found_item.refresh()

    return success(
        {"item": api_models.OtherWithID.parse_obj(found_item.attribute_values).dict()}
    )


@something_might_go_wrong
@load_model(api_models.RetrieveItem)
def retrieve(retrieve_item: api_models.RetrieveItem):
    found = list(OtherModel.query(retrieve_item.id))
    if not found:
        return not_found()

    found_item: OtherModel = found[0]
    found_item.signed_out_to.remove(retrieve_item.from_)
    if not found_item.location_counts:
        found_item.location_counts = {}
    if "Storage" not in found_item.location_counts:
        found_item.location_counts["Storage"] = 1
    elif found_item.location_counts["Storage"] >= 1:
        found_item.location_counts["Storage"] += 1
    found_item.save()
    found_item.refresh()

    return success(
        {"item": api_models.OtherWithID.parse_obj(found_item.attribute_values).dict()}
    )


@something_might_go_wrong
@load_model(api_models.LostItem)
def lose(lost_item: api_models.LostItem):
    found = list(OtherModel.query(lost_item.id))
    if not found:
        return not_found()

    found_item: OtherModel = found[0]
    found_item.signed_out_to.remove(lost_item.from_)
    found_item.save()
    found_item.refresh()

    return success(
        {"item": api_models.OtherWithID.parse_obj(found_item.attribute_values).dict()}
    )


@something_might_go_wrong
@load_model(api_models.MovedItems)
def move(moved_items: api_models.MovedItems):
    found = list(OtherModel.query(moved_items.id))
    if not found:
        return not_found()

    found_item: OtherModel = found[0]
    if moved_items.count > found_item.count:
        return failure(
            "Cannot move more items than we have. Please add them first", 400
        )
    if not found_item.location_counts:
        found_item.location_counts = {}
    if moved_items.count > found_item.location_counts.get(
        moved_items.from_location, 0
    ):
        return failure("Cannot move more items than we have in the location", 400)
    found_item.location_counts[moved_items.from_location] -= moved_items.count

    if moved_items.to_location in found_item.location_counts:
        found_item.location_counts[moved_items.to_location] += moved_items.count
    else:
        found_item.location_counts[moved_items.to_location] = moved_items.count

    found_item.save()
    found_item.refresh()

    return success(
        {"item": api_models.OtherWithID.parse_obj(found_item.attribute_values).dict()}
    )


@something_might_go_wrong
@load_model(api_models.OtherWithID, with_path_id=True)
def edit(updated_item: api_models.OtherWithID, path_id):
    item = OtherModel.get(path_id)
    for key, value in updated_item.dict().items():
        setattr(item, key, value)
    item.save()

    updated_item = api_models.OtherWithID(**item.attribute_values)

    return success({"message": "Update Successful", "item": updated_item.dict()})
