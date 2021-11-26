from app.utils import api_models
from app.utils.decorators import something_might_go_wrong, load_model
from app.utils.models import InstrumentModel
from app.utils.responses import success


@something_might_go_wrong
@load_model(api_models.MoveMultiple)
def multiple(body: api_models.MoveMultiple):
    numbers = [number.upper() for number in body.numbers]
    response_body = {"instrumentsUpdated": [], "instrumentsFailed": []}
    scan = InstrumentModel.scan(InstrumentModel.number.is_in(*numbers))
    for ins in scan:
        try:
            ins.location = body.location
            ins.save()
            response_body["instrumentsUpdated"].append(ins.number)
        except Exception as err:
            print(err)
            response_body["instrumentsFailed"].append(ins.number)
    for instrument_number in body.numbers:
        if (
            instrument_number not in response_body["instrumentsUpdated"]
            and instrument_number not in response_body["instrumentsFailed"]
        ):
            response_body["instrumentsFailed"].append(instrument_number)

    return success(response_body)
