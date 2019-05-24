from common import setup_airtable


def number(event, _context):
    pass


def student(event, _context):
    pass


def search_helper(field, value, multiple=False):
    """Helper to do the necessary search logic"""
    at = setup_airtable()
    results = []
    for page in at.get_iter():
        for item in page:
            if item['fields'].get(field) == value:
                if not multiple:
                    return item
                results.append(item)

    return results
