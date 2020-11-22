from app.bows import api_models
from app.bows.models import BowModel
from app.utils.decorators import something_might_go_wrong, load_model
from app.utils.responses import success


def update_bows(bow_updates, update_func):
    results = {"updated": [], "failed": []}
    for item in bow_updates.bow_updates:
        found = list(BowModel.query(item.id))
        if not found:
            results["failed"].append(item.id)
        bow = found[0]
        bow.count = update_func(bow.count, item.amount)
        bow.save()
        results["updated"].append(bow.id)
    return success(results)


@something_might_go_wrong
@load_model(api_models.UseBows)
def use_bows(bow_updates: api_models.UseBows):
    return update_bows(bow_updates, lambda x, y: x - y)


@something_might_go_wrong
@load_model(api_models.AddBows)
def add_bows(bow_updates: api_models.AddBows):
    return update_bows(bow_updates, lambda x, y: x + y)
