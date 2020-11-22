from app.bows import api_models
from app.bows.models import BowModel
from app.utils.decorators import something_might_go_wrong, load_model
from app.utils.responses import success


@something_might_go_wrong
@load_model(api_models.UseBows)
def use_bows(bow_updates: api_models.UseBows):
    results = {"updated": [], "failed": []}
    for item in bow_updates.bow_updates:
        found = list(BowModel.query(item.id))
        if not found:
            results["failed"].append(item.id)
        bow = found[0]
        bow.count = bow.count - item.use
        bow.save()
        results["updated"].append(bow.id)
    return success(results)


def add_bows():
    pass
