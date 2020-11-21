from app.bows import api_models
from app.bows.models import BowModel
from app.utils.decorators import something_might_go_wrong, load_model
from app.utils.responses import success, bad_request


@something_might_go_wrong
@load_model(api_models.Bow)
def main(bow: api_models.Bow):
    """Create a new type of bow."""
    found_matching = list(
        BowModel.scan((BowModel.type == bow.type) & (BowModel.size == bow.size))
    )
    if found_matching:
        return bad_request("This type of bow already exists")
    new_bow = BowModel(**bow.dict())
    new_bow.save()
    new_bow.refresh()
    created_bow = api_models.BowWithID(**new_bow.attribute_values)
    return success(
        {
            "item": created_bow.dict(),
            "message": f"{created_bow.size} {created_bow.type} created",
        },
        201,
    )
