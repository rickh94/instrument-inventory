from app.utils import api_models
from app.utils.common import make_new_history
from app.utils.decorators import something_might_go_wrong, load_and_validate, load_model
from app.utils.models import InstrumentModel
from app.utils.responses import failure, success, not_found


@something_might_go_wrong
@load_model(api_models.SignOut)
def main(sign_out: api_models.SignOut):
    """Sign out an instrument"""
    # noinspection PyTypeChecker
    found = list(InstrumentModel.scan(InstrumentModel.number == sign_out.number))
    if not found:
        return not_found()
    item = found[0]
    if item.assignedTo:
        item.history = make_new_history(item.history, item.assignedTo)
    item.assignedTo = sign_out.assignedTo
    item.location = sign_out.location
    item.save()
    item.refresh()
    return success(
        {
            "message": f"Instrument {item.number} signed out to {item.assignedTo}"
            f" at {item.location}",
            "id": item.id,
        }
    )
