"""
## Flask RESTful API

Caching: when needed to scale. Some areas we can implement:
- Add potential here

"""


def get_request(request_data):
    pass


def find_location_nearby(coordinates, distance):
    # going to assume distance is the max that user is willing to go.
    pass


def fuzzy_search_description(query_str):
    # use fuzzy search and find a location according to query.
    pass


def landmarks(query_str, coordinates, distance):
    # example given was probably just querying the desc.
    # but an idea, find a location that is in between landmark and coord.
    # But constrained by distance.
    pass
