from app.utils import api_models
from app.utils.common import serialize_item
from app.utils.decorators import something_might_go_wrong, load_model
from app.utils.models import InstrumentModel
from app.utils.responses import success


@something_might_go_wrong
@load_model(api_models.InstrumentIn)
def main(instrument: api_models.InstrumentIn):
    """Create a new instrument"""
    # photo_id = None
    # if instrument.photo:
    #     photo_id = handle_photo(instrument.photo)

    new_instrument = InstrumentModel(**instrument.dict(exclude={"photo"}))
    new_instrument.save()
    new_instrument.refresh()
    instrument_in_db = api_models.InstrumentInDB(**serialize_item(new_instrument))
    instrument_out = api_models.InstrumentOut(
        **instrument_in_db.dict(exclude={"photo"})
    )
    return success(
        {
            "message": f"Instrument {new_instrument.number} created",
            "item": instrument_out.dict(),
            "id": instrument_out.id,
        },
        201,
    )

