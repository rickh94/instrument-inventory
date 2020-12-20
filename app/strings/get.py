from app.strings.api_models import StringWithID
from app.strings.models import StringModel
from app.utils.decorators import something_might_go_wrong, no_args
from app.utils.responses import success


@something_might_go_wrong
@no_args
def main():
    """Get all the strings"""
    strings = [
        StringWithID.parse_obj(string.attribute_values) for string in StringModel.scan()
    ]
    return success({"strings": [string.dict() for string in strings]})
