from app.utils import api_models

# from app.utils.common import delete_photos, serialize_item
from app.utils.decorators import something_might_go_wrong, load_model
from app.utils.models import InstrumentModel
from app.utils.responses import success


@something_might_go_wrong
@load_model(api_models.Instrument, with_path_id=True)
def full(new_instrument: api_models.Instrument, path_id):
    """Update a full record"""
    ins = InstrumentModel.get(path_id)
    for key, value in new_instrument.dict().items():
        setattr(ins, key, value)
    ins.save()
    ins_db = api_models.InstrumentInDB.parse_obj(ins.attribute_values)
    ins_out = api_models.InstrumentOut.parse_obj(ins_db)
    return success({"message": "Update Successful", "item": ins_out.dict()})
