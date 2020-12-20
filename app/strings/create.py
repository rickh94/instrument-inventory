from app.strings import api_models
from app.strings.models import StringModel
from app.utils.decorators import something_might_go_wrong, load_model
from app.utils.responses import bad_request, success


@something_might_go_wrong
@load_model(api_models.String)
def main(string: api_models.String):
    """Create a new type of string."""
    found_matching = list(
        StringModel.scan(
            (StringModel.type == string.type)
            & (StringModel.size == string.size)
            & (StringModel.string == string.string)
        )
    )
    if found_matching:
        return bad_request(
            f"{string.size} {string.type} {string.string} String already exists"
        )
    new_string = StringModel(**string.dict())
    new_string.save()
    new_string.refresh()
    created_string = api_models.StringWithID(**new_string.attribute_values)

    return success(
        {
            "item": created_string.dict(),
            "message": f"{created_string.size} {created_string.type} "
            f"{created_string.string} String created",
        },
        201,
    )
