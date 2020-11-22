from app.bows.api_models import BowWithID
from app.bows.models import BowModel
from app.utils.decorators import something_might_go_wrong, no_args
from app.utils.responses import success


@something_might_go_wrong
@no_args
def main():
    """Get all the bows"""
    bows = [BowWithID.parse_obj(bow.attribute_values) for bow in BowModel.scan()]
    return success({"bows": [bow.dict() for bow in bows]})
