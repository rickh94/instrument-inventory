from app.utils import api_models
from app.utils.common import make_new_history
from app.utils.decorators import something_might_go_wrong, load_model
from app.utils.models import InstrumentModel
from app.utils.responses import success, not_found


@something_might_go_wrong
@load_model(api_models.SignOut)
def main(sign_out: api_models.SignOut):
    """Sign out an instrument"""
    item = sign_out_instrument(sign_out)
    if item:
        ins = api_models.InstrumentInDB.parse_obj(item.attribute_values)
        return success(
            {
                "message": f"Instrument {item.number} signed out to {item.assignedTo}"
                           f" at {item.location}",
                "id": item.id,
                "item": ins.dict(exclude={"photo"})
            }
        )
    else:
        return not_found()


def sign_out_instrument(sign_out):
    # noinspection PyTypeChecker
    found = list(InstrumentModel.scan(InstrumentModel.number == sign_out.number))
    if not found:
        return None
    item = found[0]
    if item.assignedTo:
        item.history = make_new_history(item.history, item.assignedTo)
    item.assignedTo = sign_out.assignedTo
    item.location = sign_out.location
    item.save()
    item.refresh()
    return item


@something_might_go_wrong
@load_model(api_models.SignOutMultiple)
def multiple(assignments: api_models.SignOutMultiple):
    successes = []
    failures = []
    for asg in assignments.instruments:
        if sign_out_instrument(asg):
            successes.append(asg.number)
        else:
            failures.append(asg.number)
    return success({"updated": successes, "failed": failures})
