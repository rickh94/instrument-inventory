from app.other.api_models import OtherWithID
from app.other.models import OtherModel
from app.utils.decorators import something_might_go_wrong, no_args
from app.utils.responses import success


# @something_might_go_wrong
@no_args
def main():
    """Get all the other items"""
    items = [OtherWithID.parse_obj(item.attribute_values) for item in OtherModel.scan()]
    return success({"items": [item.dict() for item in items]})
