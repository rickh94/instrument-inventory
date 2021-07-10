import ujson

from app.other import api_models
from app.other.models import OtherModel
from app.utils.decorators import something_might_go_wrong, load_model
from app.utils.responses import bad_request, success


@something_might_go_wrong
@load_model(api_models.Other)
def main(item: api_models.Other):
    """Create a new type of misc item"""
    found_matching = list(OtherModel.scan(OtherModel.name == item.name))
    if found_matching:
        return bad_request(f"{item.name} already exists")
    new_item = OtherModel(**item.dict())
    new_item.save()
    created_item = api_models.OtherWithID(**new_item.attribute_values)
    # return success("test")
    return success(
        {"item": created_item.dict(), "message": f"{created_item.name} created"}, 201
    )
