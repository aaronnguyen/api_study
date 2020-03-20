"""
## Flask API

Caching: when needed to scale. Some areas we can implement:
- Add potential here

"""
import json
# import logging
# import os

# import requests
from flask import Flask, jsonify, request
# from flask_pymongo import PyMongo
from fuzzywuzzy import fuzz

from calculate_distance import (calc_latlong_distance, find_max_latitude,
                                find_max_longitude, find_min_latitude,
                                find_min_longitude)

application = Flask(__name__)

# Development
DATASET = json.load(open("data_fulldump.json", "r"))


def _find_rentals_nearby(latitude, longitude, dist_range):
    """
    Input:
    - Coordinates of the center of the search area.
    - Range distance extending outside of the center.

    Output:
    - Dict of rental ids using the distance as the key.
    - Sorted list of keys in asc order.
    """

    # going to assume distance is the max that user is willing to go.
    # build a box around the coordinates. then start removing all the corners.
    # order by closest location.
    rentals_by_range = {}

    # Explicit of float
    latitude = float(latitude)
    longitude = float(longitude)

    # Find coordinate max min for lat and long
    # Range would be a circle a target coordinate
    # Build a square box around the search location for easier implementation.
    #   using a box to reduce the search space.
    # Just search areas around this zone and calculate the distance
    #   This will return a circle
    #   The more we break down the zones
    #       the more we can get closer to a circle search.
    max_lat = find_max_latitude(latitude, longitude, dist_range)
    max_lng = find_max_longitude(latitude, longitude, dist_range)
    min_lat = find_min_latitude(latitude, longitude, dist_range)
    min_lng = find_min_longitude(latitude, longitude, dist_range)

    # calculate lat long dist.
    # currently very slow
    #   iterating through all elements and checking the values
    # when implementing the db search,
    #   we can search for entries based on range
    # Should be faster then iterating through a list line by line.
    # If project is expanded,
    #   breakdown datasets into zones. counties. etc.
    for row_id in DATASET:
        row = DATASET[row_id]
        r_lat = float(row['latitude'])
        r_lng = float(row['longitude'])

        # if the entry is within the zone.
        if ((r_lat >= min_lat and r_lat <= max_lat) or
                (r_lng >= min_lng and r_lng <= max_lng)):
            dist = calc_latlong_distance([r_lat, r_lng], [latitude, longitude])
            if dist <= dist_range:

                # create a reference of ids based on distance.
                # when we sort the keys, we should have a list of closest
                #   to farthest locations.
                if dist not in rentals_by_range:
                    rentals_by_range[dist] = []
                rentals_by_range[dist].append(row["id"])

    # sort lat longs diff by value.
    #   saved the keys as ints means we can sort them easily.
    #   instead of building a totally new list object
    #   just add the sorted keys to the already created dict.
    # just using the sorted function in python. timsort seems pretty effecient.
    # NOTE: originally added the sorted list of keys into the dict.
    #   Just returning it as 2 items.
    # get rental info by id # based on lat long diff
    # TODO: maybe save some of these calculations?
    #   We could quickly calculate distance using pythagorean theorem
    #   although the Earth is curved, shouldn't be much
    #       difference in distance if nearby.
    #   Maybe when calculating distances, if the zone falls within a cached
    #   search range, then we can use those locations from that search.
    #   Maybe search that first? to save lookup? then search for new locations
    #   outside of the already searched area.
    return rentals_by_range, sorted(list(rentals_by_range.keys()))


def _check_request_fields(dict_datarequest, lst_requiredfields):
    """
    Input:

    - Data request from the HTTP call (Just passed the whole thing in)
    - List of expected keys.
    """

    # Use set subtraction to figure out if we are missing any fields.
    reqfields = set(lst_requiredfields) - set(dict_datarequest.keys())
    if len(reqfields) == 0:
        return True
    else:
        return False


@application.route('/')
def index():
    return jsonify(status=True, message='Rental Serach API.')


@application.route('/findnearby', methods=['GET'])
def find_nearby():
    data = request.get_json(force=True)
    lst_reqfields = ["latitude", "longitude", "distance"]
    if _check_request_fields(data, lst_reqfields) is False:
        return jsonify(
            status=False, message='Missing required search fields.'), 400

    lst_nearby_rentals, sorted_idkeys = _find_rentals_nearby(
        data['latitude'], data['longitude'], data['distance'])

    # build_search_ref =

    if "query" in data:
        # reduce the search based on the query relevance.
        pass

    if "filter" in data:
        # reduce the list by the filters passed in
        pass

    return jsonify(status=True, data=lst_nearby_rentals)


# TODO: could load data into elastic search and we could utilize
#   flexible search functions.
# For brevity, will use fuzzy wuzzy lib to do fuzzy string match.
#   Reduce host complexity as well.
# https://github.com/seatgeek/fuzzywuzzy
def fuzzy_search_query(query_str, row_desc):
    # use fuzzy search and find a location according to query.

    # Used at work before, better results using all four and averaging
    #   out the score.
    f_part_r_val = fuzz.partial_ratio(query_str, row_desc)
    f_r_val = fuzz.ratio(query_str, row_desc)
    tsortr_val = fuzz.token_sort_ratio(query_str, row_desc)
    tsetr_val = fuzz.token_set_ratio(query_str, row_desc)
    avg_score = (f_part_r_val + f_r_val + tsortr_val + tsetr_val) / 4
    return avg_score


# TODO: impl
def landmarks(query_str, coordinates, distance):
    # example given was probably just querying the desc.
    # but an idea, find a location that is in between landmark and coord.
    # But constrained by distance.
    pass


if __name__ == "__main__":
    nearby_rentals, sorted_keys_asc = _find_rentals_nearby(
        40.71344, -73.99037, 200)
    test_query = "LowerEastSide"

    for skey in sorted_keys_asc:
        for id_key in nearby_rentals[skey]:
            fuzz_score = fuzzy_search_query(
                test_query, DATASET[id_key]["name"])
            print(DATASET[id_key])
            print(fuzz_score)
            print("\n\n")
    # fuzzy_search_query("")
