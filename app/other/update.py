from app.other import api_models
from app.other.models import OtherModel
from app.utils.common import update_items
from app.utils.decorators import something_might_go_wrong, load_model
from app.utils.responses import not_found, success


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
    found_item.count -= 1
    found_item.num_out += 1
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
    found_item.count += 1
    found_item.num_out -= 1
    found_item.signed_out_to.remove(retrieve_item.from_)
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
    found_item.num_out -= 1
    found_item.signed_out_to.remove(lost_item.from_)
    found_item.save()
    found_item.refresh()

    return success(
        {"item": api_models.OtherWithID.parse_obj(found_item.attribute_values).dict()}
    )
