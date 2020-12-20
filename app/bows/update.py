from app.bows import api_models
from app.bows.models import BowModel
from app.utils.common import update_items
from app.utils.decorators import something_might_go_wrong, load_model


@something_might_go_wrong
@load_model(api_models.UseBows)
def use_bows(bow_updates: api_models.UseBows):
    return update_items(
        bow_updates.bow_updates, lambda x, y: x - y, BowModel, api_models.BowWithID
    )


@something_might_go_wrong
@load_model(api_models.AddBows)
def add_bows(bow_updates: api_models.AddBows):
    return update_items(
        bow_updates.bow_updates, lambda x, y: x + y, BowModel, api_models.BowWithID
    )
