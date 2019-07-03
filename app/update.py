from app.lib.common import handle_photo, delete_photos, serialize_item
from app.lib.decorators import something_might_go_wrong, load_and_validate
from app.lib.responses import failure, success
from app.lib.models import InstrumentModel


@something_might_go_wrong
@load_and_validate({"photoUrl": "Photo"}, with_path_id=True)
def photo(data, path_id):
    """Change or add a photo"""
    if not path_id:
        return failure("Record ID must be in url", 400)
    ins = InstrumentModel.get(path_id)
    if ins.photo:
        delete_photos(ins.photo)
    ins.photo = handle_photo(data["photoUrl"])
    ins.save()
    return success({"message": "Photo successfully updated"})


@something_might_go_wrong
@load_and_validate({}, with_path_id=True)
def full(data, path_id):
    """Update a full record"""
    actions = []
    try:
        for key, value in data.items():
            if key in ["condition", "quality"] and value is not None:
                value = int(value)
            field = getattr(InstrumentModel, key)
            actions.append(field.set(value))
    except AttributeError as err:
        print(err)
        return failure("Unknown field in request", 400)
    ins = InstrumentModel.get(path_id)
    ins.update(actions=actions)
    ins.save()
    return success({"message": "Update Successful", "item": serialize_item(ins)})
